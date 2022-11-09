from typing import List, Any
from django.db.models import Model
from django.db.models.query import QuerySet
from sightings.filters.base import BaseFilterResolver, BaseFilter
from sightings.filters.posts import (
    PostsLocationIdsFilter,
    PostsSightingIdsFilter,
    PostsQueryStringFilter
)
from sightings.filters.sightings import (
    SightingsLocationIdsFilter,
    SightingsSightingIdsFilter,
    SightingsLocationQueryStringFilter,
)
from sightings.filters.locations import (
    LocationExactFilter,
    LocationQueryStringFilter,
    LocationIdsFilter,
)

from sightings.exceptions import FilterValidationException


class AndResolver(BaseFilterResolver):
    """
    Combine filters by ANDing their results and return the resulting queryset.
    """
    def __init__(self, filters: List[BaseFilter] = None):
        self.filters = filters

    @staticmethod
    def __has_location_q_filter(filters: List[BaseFilter]):
        return any(isinstance(fil, LocationQueryStringFilter) for fil in filters)

    @staticmethod
    def __has_location_id_filter(filters: List[BaseFilter]):
        return any(isinstance(fil, LocationIdsFilter) for fil in filters)

    @staticmethod
    def __has_sightings_q_filter(filters: List[BaseFilter]):
        return any(isinstance(fil, SightingsLocationQueryStringFilter) for fil in filters)

    @staticmethod
    def __has_posts_q_filter(filters: List[BaseFilter]):
        return any(isinstance(fil, PostsQueryStringFilter) for fil in filters)

    @staticmethod
    def __has_location_exact_filter(filters: List[BaseFilter]):
        return any(isinstance(fil, LocationExactFilter) for fil in filters)

    @staticmethod
    def __has_sighting_location_id_filter(filters: List[BaseFilter]):
        return any(isinstance(fil, SightingsLocationIdsFilter) for fil in filters)

    @staticmethod
    def __has_post_location_id_filter(filters: List[BaseFilter]):
        return any(isinstance(fil, PostsLocationIdsFilter) for fil in filters)

    @staticmethod
    def __has_sighting_sighting_id_filter(filters: List[BaseFilter]):
        return any(isinstance(fil, SightingsSightingIdsFilter) for fil in filters)

    @staticmethod
    def __has_post_sighting_id_filter(filters: List[BaseFilter]):
        return any(isinstance(fil, PostsSightingIdsFilter) for fil in filters)

    @staticmethod
    def __get_first_filter_instance(filter: Any, filters: List[BaseFilter]):
        for fil in filters:
            if isinstance(fil, filter):
                return fil

        return None

    @staticmethod
    def __has_duplicate_filters(filters: List):
        types = set([type(f) for f in filters])
        if len(types) < len(filters):
            return True

        return False

    def resolve(self, filters: List[BaseFilter] = None, qs: QuerySet = None) -> QuerySet:
        resolve_filters = filters or self.filters

        if resolve_filters is None:
            return qs

        for f in resolve_filters:
            qs = f.filter_qs(query_set=qs)

        return qs

    def __has_many_loc_id_filters(self, filters: List[BaseFilter]):
        return (self.__has_sighting_location_id_filter(filters) and self.__has_post_location_id_filter(filters)) \
            or (self.__has_sighting_location_id_filter(filters) and self.__has_location_id_filter(filters)) \
            or (self.__has_post_location_id_filter(filters) and self.__has_location_id_filter(filters))

    def __has_many_sighting_id_filters(self, filters: List[BaseFilter]):
        return self.__has_sighting_sighting_id_filter(filters) and self.__has_post_sighting_id_filter(filters)

    def __has_many_q_filters(self, filters: List[BaseFilter]):
        return (self.__has_location_q_filter(filters) and self.__has_posts_q_filter(filters)) \
            or (self.__has_location_q_filter(filters) and self.__has_sightings_q_filter(filters)) \
            or (self.__has_posts_q_filter(filters) and self.__has_sightings_q_filter(filters))

    def validate_filters(self, filters: List[BaseFilter] = None, model: Model = None) -> bool:
        val_filters = filters or self.filters

        if val_filters is None:
            return True

        if self.__has_many_q_filters(filters=val_filters):
            msg = 'Cannot have multiple query filters in one call'
            raise FilterValidationException(msg)

        if self.__has_duplicate_filters(filters=val_filters):
            msg = 'Cannot pass duplicate filters in a single call'
            raise FilterValidationException(msg)

        return all([fil.validate() for fil in val_filters])

    def aggregate_filters(self, filters: List[BaseFilter] = None) -> List[BaseFilter]:
        """
        Recursively aggregate certain filters to ensure no unnecessary processing or easily resolved conflicts take
        place.
        :param filters:
        :return:
        """
        filters = filters or self.filters

        # aggregate sightings location ids filters and location id filters
        if self.__has_sighting_location_id_filter(filters) and self.__has_location_id_filter(filters):
            sighting_location_id_filter = self.__get_first_filter_instance(SightingsLocationIdsFilter, filters)
            location_id_filter = self.__get_first_filter_instance(LocationIdsFilter, filters)

            aggregated_locations = list(
                set(sighting_location_id_filter.location_ids.extend(location_id_filter.location_ids))
            )
            new_filter = SightingsLocationIdsFilter(location_ids=aggregated_locations)

            filters.remove(sighting_location_id_filter)
            filters.remove(location_id_filter)
            filters.append(new_filter)

            return self.aggregate_filters(filters)

        # aggregate sightings location ids filters and posts location id filters
        if self.__has_sighting_location_id_filter(filters) and self.__has_post_location_id_filter(filters):
            sighting_location_id_filter = self.__get_first_filter_instance(SightingsLocationIdsFilter, filters)
            post_location_id_filter = self.__get_first_filter_instance(PostsLocationIdsFilter, filters)

            aggregated_locations = list(
                set(sighting_location_id_filter.location_ids.extend(post_location_id_filter.location_ids))
            )
            new_filter = PostsLocationIdsFilter(location_ids=aggregated_locations)

            filters.remove(sighting_location_id_filter)
            filters.remove(post_location_id_filter)
            filters.append(new_filter)

            return self.aggregate_filters(filters)

        # aggregate location ids filters and posts location id filters
        if self.__has_location_id_filter(filters) and self.__has_post_location_id_filter(filters):
            post_location_id_filter = self.__get_first_filter_instance(PostsLocationIdsFilter, filters)
            location_id_filter = self.__get_first_filter_instance(LocationIdsFilter, filters)

            aggregated_locations = list(
                set(post_location_id_filter.location_ids.extend(location_id_filter.location_ids))
            )
            new_filter = PostsLocationIdsFilter(location_ids=aggregated_locations)

            filters.remove(post_location_id_filter)
            filters.remove(location_id_filter)
            filters.append(new_filter)

            return self.aggregate_filters(filters)

        # aggregate sighting ids filters and posts sighting ids filters
        if self.__has_sighting_sighting_id_filter(filters) and self.__has_post_sighting_id_filter(filters):
            post_sighting_id_filter = self.__get_first_filter_instance(PostsSightingIdsFilter, filters)
            sighting_id_filter = self.__get_first_filter_instance(SightingsSightingIdsFilter, filters)

            aggregate_sightings = list(
                set(post_sighting_id_filter.sighting_ids.extend(sighting_id_filter.sighting_ids))
            )
            new_filter = PostsSightingIdsFilter(sighting_ids=aggregate_sightings)

            filters.remove(post_sighting_id_filter)
            filters.remove(sighting_id_filter)
            filters.append(new_filter)

            return self.aggregate_filters(filters)

        return filters

    def validate_and_resolve(self, qs: QuerySet):
        """
        Validate, aggregate and resolve filters to return a filtered Queryset
        :param qs:
        :return:
        """
        self.validate_filters()
        filters = self.aggregate_filters()

        return self.resolve(filters=filters, qs=qs)
