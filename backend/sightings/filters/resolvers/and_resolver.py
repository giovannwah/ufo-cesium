from typing import Iterable
from django.db.models import Model
from django.db.models.query import QuerySet
from sightings.filters.base import BaseFilterResolver, BaseFilter
from sightings.filters.posts import (
    PostsLocationIdsFilter,
    PostsUserIdsFilter,
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
)

from sightings.exceptions import FilterValidationException


class AndResolver(BaseFilterResolver):
    """
    Combine filters by ANDing their results and return the resulting queryset.
    """
    def __init__(self, filters: Iterable[BaseFilter] = None):
        self.filters = filters

    def resolve(self, filters: Iterable[BaseFilter] = None, qs: QuerySet = None) -> QuerySet:
        resolve_filters = filters or self.filters

        if resolve_filters is None:
            return qs

        for f in resolve_filters:
            qs = f.filter_qs(query_set=qs)

        return qs

    def __has_location_q_filter(self, filters: Iterable[BaseFilter]):
        return any(isinstance(fil, LocationQueryStringFilter) for fil in filters)

    def __has_sightings_q_filter(self, filters: Iterable[BaseFilter]):
        return any(isinstance(fil, SightingsLocationQueryStringFilter) for fil in filters)

    def __has_posts_q_filter(self, filters: Iterable[BaseFilter]):
        return any(isinstance(fil, PostsQueryStringFilter) for fil in filters)

    def __has_location_exact_filter(self, filters: Iterable[BaseFilter]):
        return any(isinstance(fil, LocationExactFilter) for fil in filters)

    def __has_sighting_location_id_filter(self, filters: Iterable[BaseFilter]):
        return any(isinstance(fil, SightingsLocationIdsFilter) for fil in filters)

    def __has_post_location_id_filter(self, filters: Iterable[BaseFilter]):
        return any(isinstance(fil, PostsLocationIdsFilter) for fil in filters)

    def __has_sighting_sighting_id_filter(self, filters: Iterable[BaseFilter]):
        return any(isinstance(fil, SightingsSightingIdsFilter) for fil in filters)

    def __has_post_sighting_id_filter(self, filters: Iterable[BaseFilter]):
        return any(isinstance(fil, PostsSightingIdsFilter) for fil in filters)

    def __has_many_loc_id_filters(self, filters: Iterable[BaseFilter]):
        return self.__has_sighting_location_id_filter(filters) and self.__has_post_location_id_filter(filters)

    def __has_many_sighting_id_filters(self, filters: Iterable[BaseFilter]):
        return self.__has_sighting_sighting_id_filter(filters) and self.__has_post_sighting_id_filter(filters)

    def __has_many_q_filters(self, filters: Iterable[BaseFilter]):
        return (self.__has_location_q_filter(filters) or self.__has_posts_q_filter(filters)) \
            and (self.__has_location_q_filter(filters) or self.__has_sightings_q_filter(filters))

    def validate_filters(self, filters: Iterable[BaseFilter] = None, model: Model = None) -> bool:
        val_filters = filters or self.filters

        if val_filters is None:
            return True

        if self.__has_many_q_filters(filters=val_filters):
            msg = 'Cannot have multiple query filters'
            raise FilterValidationException(msg)

        if self.__has_many_loc_id_filters(filters=val_filters):
            msg = "Cannot have multiple location ID filters"
            raise FilterValidationException(msg)

        if self.__has_many_sighting_id_filters(filters=val_filters):
            msg = "Cannot have multiple sighting ID filters"
            raise FilterValidationException(msg)

        return all([fil.validate() for fil in filters])
