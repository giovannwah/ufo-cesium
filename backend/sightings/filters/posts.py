from typing import Optional, List
from django.db.models.query import QuerySet, Q
from strawberry_django_plus.relay import from_base64
from sightings.filters.base import (
    BaseFilter,
    SimpleFilter,
)
from sightings.filters.locations import (
    DistanceFromFilter
)
from sightings.helpers.geocoding import (
    validate_longitude_latitude,
    posts_distance_within_q,
    posts_distance_outside_q,
)
from sightings.helpers.post import (
    posts_q_by_search_query,
    posts_q_by_state_name_exact,
    posts_q_by_state_exact,
    posts_q_by_country_exact,
    posts_q_by_city_exact,
)
from sightings.models import Post
from sightings.exceptions import (
    PostInputValidationException,
)
from sightings.gql.types.post import PostFilterInput


class PostsUfoShapeFilter(SimpleFilter):
    """
    Filter Posts by ufo shape
    """
    def __init__(self, ufo_shape: str):
        self.ufo_shape = ufo_shape

    def get_query(self) -> Q:
        if self.ufo_shape is None or self.ufo_shape.strip() == "":
            return Q()

        return Q(ufo_shape__iexact=self.ufo_shape)


class PostsQueryStringFilter(SimpleFilter):
    """
    Filter Posts by a query string
    """
    def __init__(self, q: str):
        self.q = q

    def get_query(self) -> Q:
        if self.q is None or self.q.strip() == "":
            return Q()

        return posts_q_by_search_query(self.q)


class PostsLocationExactFilter(SimpleFilter):
    def __init__(
        self,
        city_exact: Optional[str] = None,
        state_exact: Optional[str] = None,
        state_name_exact: Optional[str] = None,
        country_exact: Optional[str] = None
    ):
        self.city_exact = city_exact
        self.state_exact = state_exact
        self.state_name_exact = state_name_exact
        self.country_exact = country_exact

    def validate(self) -> bool:
        if self.state_exact and self.state_name_exact:
            raise PostInputValidationException('Cannot specify both stateExact and stateNameExact')

        return True

    def get_query(self) -> Q:
        query = Q()

        if all(i is None or i.strip() == "" for i in
           [self.city_exact, self.state_exact, self.state_name_exact, self.country_exact]
        ):
            return query

        if self.state_name_exact:
            query &= posts_q_by_state_name_exact(self.state_name_exact)
        if self.country_exact:
            query &= posts_q_by_country_exact(self.country_exact)
        if self.state_exact:
            query &= posts_q_by_state_exact(self.state_exact)
        if self.city_exact:
            query &= posts_q_by_city_exact(self.city_exact)

        return query


class PostsLocationIdsFilter(SimpleFilter):
    def __init__(self, location_ids: List[str]):
        self.location_ids = location_ids

    def get_query(self) -> Q:
        return Q(sighting__location__id__in=[from_base64(location)[1] for location in self.location_ids])


class PostsSightingIdsFilter(SimpleFilter):
    def __init__(self, sighting_ids: List[str]):
        self.sighting_ids = sighting_ids

    def get_query(self) -> Q:
        return Q(sighting__id__in=[from_base64(sighting)[1] for sighting in self.sighting_ids])


class PostsPostIdsFilter(SimpleFilter):
    def __init__(self, post_ids: List[str]):
        self.post_ids = post_ids

    def get_query(self) -> Q:
        return Q(id__in=[from_base64(post)[1] for post in self.post_ids])


class PostsUserIdsFilter(SimpleFilter):
    def __init__(self, user_ids: List[str]):
        self.user_ids = user_ids

    def get_query(self) -> Q:
        return Q(user__id__in=[from_base64(user)[1] for user in self.user_ids])


def get_post_filters(pfi: PostFilterInput):
    ret = []
    shape = pfi.ufo_shape if pfi else None
    q = pfi.q if pfi else None
    post_created = pfi.post_created_datetime if pfi else None
    sighting_filter = pfi.sighting_filter
    loc_input = sighting_filter.location_filter if sighting_filter else None
    sdt_input = sighting_filter.sighting_datetime_filter if sighting_filter else None
