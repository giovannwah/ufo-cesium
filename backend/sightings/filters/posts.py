from typing import List
from django.db.models.query import Q
from strawberry_django_plus.relay import from_base64
from sightings.filters.base import SimpleFilter
from sightings.filters.locations import (
    DistanceFromFilter,
    LocationExactFilter
)
from sightings.filters.datetime import (
    DateFilter,
    TimeFilter,
)
from sightings.helpers.post import posts_q_by_search_query
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
    if pfi:
        # FIXME: This could all definitely be cleaned up
        shape = getattr(pfi, "ufo_shape", None)
        q = getattr(pfi, "q", None)
        post_created = getattr(pfi, "post_created_datetime", None)
        sighting_ids = getattr(pfi, "sighting_ids", None)
        user_ids = getattr(pfi, "user_ids", None)
        post_ids = getattr(pfi, "post_ids", None)
        location_ids = getattr(pfi, "location_ids", None)
        sighting_filter = getattr(pfi, "sighting_filter", None)
        loc_input = getattr(sighting_filter, "location_filter", None) if sighting_filter else None
        sdt_input = getattr(sighting_filter, "sighting_datetime_filter", None) if sighting_filter else None

        if shape:
            ret.append(
                PostsUfoShapeFilter(ufo_shape=shape)
            )
        if q:
            ret.append(
                PostsQueryStringFilter(q=q)
            )
        if sighting_ids:
            ret.append(
                PostsSightingIdsFilter(sighting_ids=sighting_ids)
            )
        if user_ids:
            ret.append(
                PostsUserIdsFilter(user_ids=user_ids)
            )
        if post_ids:
            ret.append(
                PostsPostIdsFilter(post_ids=post_ids)
            )
        if location_ids:
            ret.append(
                PostsLocationIdsFilter(location_ids=location_ids)
            )
        if post_created:
            if post_created.date_before or post_created.date_after or post_created.date_exact:
                ret.append(
                    DateFilter(
                        date_after=post_created.date_after,
                        date_before=post_created.date_before,
                        date_exact=post_created.date_exact,
                        pre="created_datetime"
                    )
                )

            if post_created.time_before or post_created.time_after or post_created.time_exact:
                ret.append(
                    TimeFilter(
                        time_after=post_created.time_after,
                        time_before=post_created.time_before,
                        time_exact=post_created.time_exact,
                        pre="created_datetime"
                    )
                )

        if loc_input:
            if loc_input.city_exact or loc_input.state_exact or loc_input.country_exact or loc_input.state_name_exact:
                ret.append(
                    LocationExactFilter(
                        city_exact=loc_input.city_exact,
                        state_exact=loc_input.state_exact,
                        state_name_exact=loc_input.state_name_exact,
                        country_exact=loc_input.country_exact,
                    )
                )

            if loc_input.distance_from:
                ret.append(
                    DistanceFromFilter(
                        longitude=loc_input.distance_from.longitude,
                        latitude=loc_input.distance_from.latitude,
                        arc_length=loc_input.distance_from.arc_length,
                        inside_circle=loc_input.distance_from.inside_circle,
                    )
                )

        if sdt_input:
            if sdt_input.date_before or sdt_input.date_after or sdt_input.date_exact:
                ret.append(
                    DateFilter(
                        date_after=sdt_input.date_after,
                        date_before=sdt_input.date_before,
                        date_exact=sdt_input.date_exact,
                        pre="sighting__sighting_datetime"
                    )
                )

            if sdt_input.time_before or sdt_input.time_after or sdt_input.time_exact:
                ret.append(
                    TimeFilter(
                        time_after=sdt_input.time_after,
                        time_before=sdt_input.time_before,
                        time_exact=sdt_input.time_exact,
                        pre="sighting__sighting_datetime"
                    )
                )

    return ret
