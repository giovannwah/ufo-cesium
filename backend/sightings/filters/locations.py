from typing import Optional
from django.db.models import QuerySet
from django.db.models.query import Q
from sightings.filters.base import BaseFilter
from sightings.exceptions import LocationInputValidationException
from sightings.models import Location
from sightings.helpers.geocoding import (
    validate_longitude_latitude,
    locations_distance_within_q,
    locations_distance_outside_q,
)
from sightings.helpers.locations import (
    locations_q_by_search_query,
    locations_q_by_state_name_exact,
    locations_q_by_country_exact,
    locations_q_by_state_exact,
    locations_q_by_city_exact,
)


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
        inside_circle: bool
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
        self, locations: QuerySet[Location], latitude: float, longitude: float, arc_length: float
    ) -> Q:
        if self.inside_circle:
            return locations_distance_within_q(
                locations, self.latitude, self.longitude, self.arc_length
            )
        else:
            return locations_distance_outside_q(
                locations, self.latitude, self.longitude, self.arc_length
            )

    def filter_qs(self, query_set: QuerySet[Location]) -> QuerySet[Location]:
        if not query_set.exists():
            return query_set

        return query_set.filter(self.get_query(
            locations=query_set,
            latitude=self.latitude,
            longitude=self.longitude,
            arc_length=self.arc_length,
        ))


class LocationQueryStringFilter(BaseFilter):
    """
    Filter for a location query string
    """
    def __init__(self, q: Optional[str] = None):
        self.q = q

    def validate(self) -> bool:
        """
        Validate LocationFilterInput
        """
        return True

    def get_query(self) -> Q:
        if self.q is None or self.q.strip() == "":
            return Q()

        return locations_q_by_search_query(self.q)

    def filter_qs(self, query_set: QuerySet[Location]) -> QuerySet[Location]:
        if not query_set.exists():
            return query_set

        return query_set.filter(self.get_query())


class LocationExactFilter(BaseFilter):
    """
    Filter for Exact location
    """
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
        """
        Validate LocationExactFilter
        """
        if self.state_exact and self.state_name_exact:
            raise LocationInputValidationException('Cannot specify both stateExact and stateNameExact')

        return True

    def get_query(self) -> Q:
        query = Q()

        if all(i is None or i.strip() == "" for i in
           [self.city_exact, self.state_exact, self.state_name_exact, self.country_exact]
        ):
            return query

        if self.state_name_exact:
            query &= locations_q_by_state_name_exact(self.state_name_exact)
        if self.country_exact:
            query &= locations_q_by_country_exact(self.country_exact)
        if self.state_exact:
            query &= locations_q_by_state_exact(self.state_exact)
        if self.city_exact:
            query &= locations_q_by_city_exact(self.city_exact)

        return query

    def filter_qs(self, query_set: QuerySet[Location]) -> QuerySet[Location]:
        if not query_set.exists():
            return query_set

        return query_set.filter(self.get_query())