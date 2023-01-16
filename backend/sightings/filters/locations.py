from typing import Optional, List
from strawberry_django_plus.relay import from_base64
from django.db.models import QuerySet, Model
from django.db.models.query import Q
from sightings.filters.base import BaseFilter, SimpleFilter
from sightings.exceptions import LocationInputValidationException
from sightings.helpers.geocoding import (
    validate_longitude_latitude,
    generic_distance_outside_q,
    generic_distance_within_q,
)
from sightings.helpers.locations import (
    locations_q_by_search_query,
)
from sightings.helpers.common import update_filter_args
from sightings.gql.types.location import LocationFilterInput
from sightings.models import Sighting, Post


class DistanceFromFilter(BaseFilter):
    """
    Filter a list of locations in some way based on position relative to the circumference of a
    circle defined by a center of (latitude, longitude), and an arc drawn from that center.
    latitude - central location's latitude
    longitude - central location's longitude
    arc_length - distance, in meters, from the central location
    inside_circle - boolean, True if targeting locations inside the circle, False otherwise.
    """
    def __init__(
        self,
        longitude: float,
        latitude: float,
        arc_length: float,
        inside_circle: bool,
    ):
        self.longitude = longitude
        self.latitude = latitude
        self.arc_length = arc_length
        self.inside_circle = inside_circle

    def validate(self) -> bool:
        if not validate_longitude_latitude(self.longitude, self.latitude):
            raise LocationInputValidationException(
                f'Invalid latitude and longitude: ({self.latitude}, {self.longitude})'
            )
        if self.arc_length <= 0:
            raise LocationInputValidationException(
                f'Invalid arcLength: {self.arc_length}'
            )

        return True

    def get_query(
        self, qs: QuerySet, latitude: float, longitude: float, arc_length: float
    ) -> Q:
        if self.inside_circle:
            return generic_distance_within_q(
                qs, self.latitude, self.longitude, self.arc_length
            )
        else:
            return generic_distance_outside_q(
                qs, self.latitude, self.longitude, self.arc_length
            )

    def filter_qs(self, query_set: QuerySet) -> QuerySet:
        if not query_set.exists():
            return query_set

        return query_set.filter(
            self.get_query(
                qs=query_set,
                latitude=self.latitude,
                longitude=self.longitude,
                arc_length=self.arc_length,
            )
        )


class LocationQueryStringFilter(SimpleFilter):
    """
    Filter for a location query string
    """
    def __init__(self, q: Optional[str] = None):
        self.q = q

    def get_query(self) -> Q:
        if self.q is None or self.q.strip() == "":
            return Q()

        return locations_q_by_search_query(self.q)


class LocationExactFilter(SimpleFilter):
    """
    Filter for Exact location
    """
    def __init__(
        self,
        city_exact: Optional[str] = None,
        state_exact: Optional[str] = None,
        state_name_exact: Optional[str] = None,
        country_exact: Optional[str] = None,
    ):
        self.city_exact = city_exact
        self.state_exact = state_exact
        self.state_name_exact = state_name_exact
        self.country_exact = country_exact

    def validate(self) -> bool:
        """
        Validate LocationExactFilter
        """
        if self.state_exact and self.state_name_exact:
            raise LocationInputValidationException('Cannot specify both stateExact and stateNameExact')

        return True

    def get_query(self, model: Model) -> Q:
        query = Q()

        if all(i is None or i.strip() == "" for i in
           [self.city_exact, self.state_exact, self.state_name_exact, self.country_exact]
        ):
            return query

        state_name_exact_query = {
            "state_name__iexact": self.state_name_exact
        }
        state_exact_query = {
            "state__iexact": self.state_exact
        }
        city_exact_query = {
            "city__iexact": self.city_exact
        }
        country_exact_query = {
            "country__iexact": self.country_exact
        }

        if model is Sighting:
            state_name_exact_query = update_filter_args(state_name_exact_query, sightings=True)
            state_exact_query = update_filter_args(state_exact_query, sightings=True)
            city_exact_query = update_filter_args(city_exact_query, sightings=True)
            country_exact_query = update_filter_args(country_exact_query, sightings=True)
        if model is Post:
            state_name_exact_query = update_filter_args(state_name_exact_query, posts=True)
            state_exact_query = update_filter_args(state_exact_query, posts=True)
            city_exact_query = update_filter_args(city_exact_query, posts=True)
            country_exact_query = update_filter_args(country_exact_query, posts=True)

        if self.state_name_exact:
            query &= Q(**state_name_exact_query)
        if self.country_exact:
            query &= Q(**country_exact_query)
        if self.state_exact:
            query &= Q(**state_exact_query)
        if self.city_exact:
            query &= Q(**city_exact_query)

        return query

    def filter_qs(self, query_set: QuerySet, **kwargs) -> QuerySet:
        return super().filter_qs(query_set, model=query_set.model)


class LocationIdsFilter(SimpleFilter):
    def __init__(self, location_ids: List[str]):
        self.location_ids = location_ids

    def get_query(self):
        return Q(id__in=[from_base64(loc)[1] for loc in self.location_ids])


def get_location_filters(linput: LocationFilterInput):
    ret = []

    if not linput:
        return ret

    if linput.city_exact or linput.state_exact or linput.country_exact or linput.state_name_exact:
        ret.append(
            LocationExactFilter(
                city_exact=linput.city_exact,
                state_exact=linput.state_exact,
                state_name_exact=linput.state_name_exact,
                country_exact=linput.country_exact,
            )
        )
    if linput.q:
        ret.append(
            LocationQueryStringFilter(q=linput.q)
        )
    if linput.distance_from:
        ret.append(
            DistanceFromFilter(
                longitude=linput.distance_from.longitude,
                latitude=linput.distance_from.latitude,
                arc_length=linput.distance_from.arc_length,
                inside_circle=linput.distance_from.inside_circle
            )
        )
    if linput.location_ids:
        ret.append(
            LocationIdsFilter(
                location_ids=linput.location_ids
            )
        )

    return ret
