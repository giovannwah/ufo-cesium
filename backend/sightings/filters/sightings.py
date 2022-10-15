from typing import Optional
from datetime import datetime, time
from django.db.models import QuerySet
from django.db.models.query import Q
from sightings.filters.base import BaseFilter
from sightings.exceptions import (
    SightingInputValidationException,
    DatetimeInputValidationException,
)
from sightings.models import Sighting
from sightings.helpers.geocoding import (
    validate_longitude_latitude,
    sightings_distance_within_q,
    sightings_distance_outside_q,
)
from sightings.helpers.sighting import (
    sightings_q_by_search_query,
    sightings_q_by_state_name_exact,
    sightings_q_by_state_exact,
    sightings_q_by_city_exact,
    sightings_q_by_country_exact,
)


class SightingsDistanceFromFilter(BaseFilter):
    """
    Filter sightings by distance within or beyond a circle drawn around a particular location
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
            raise SightingInputValidationException(
                f'Invalid latitude and longitude: ({self.latitude}, {self.longitude})'
            )
        if self.arc_length <= 0:
            raise SightingInputValidationException(
                f'Invalid arcLength: {self.arc_length}'
            )

        return True

    def get_query(
        self, sightings: QuerySet[Sighting], latitude: float, longitude: float, arc_length: float
    ) -> Q:
        if self.inside_circle:
            return sightings_distance_within_q(
                sightings, self.latitude, self.longitude, self.arc_length
            )
        else:
            return sightings_distance_outside_q(
                sightings, self.latitude, self.longitude, self.arc_length
            )

    def filter_qs(self, query_set: QuerySet[Sighting]) -> QuerySet[Sighting]:
        if not query_set.exists():
            return query_set

        return query_set.filter(self.get_query(
            sightings=query_set,
            latitude=self.latitude,
            longitude=self.longitude,
            arc_length=self.arc_length,
        ))


class SightingsLocationQueryStringFilter(BaseFilter):
    """
    Filter sightings by location query
    """
    def __init__(self, q: Optional[str] = None):
        self.q = q

    def validate(self) -> bool:
        return True

    def get_query(self) -> Q:
        if self.q is None or self.q.strip() == "":
            return Q()

        return sightings_q_by_search_query(self.q)

    def filter_qs(self, query_set: QuerySet[Sighting]) -> QuerySet[Sighting]:
        if not query_set.exists():
            return query_set

        return query_set.filter(self.get_query())


class SightingsLocationExactFilter(BaseFilter):
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
            raise SightingInputValidationException('Cannot specify both stateExact and stateNameExact')

        return True

    def get_query(self) -> Q:
        query = Q()

        if all(i is None or i.strip() == "" for i in
           [self.city_exact, self.state_exact, self.state_name_exact, self.country_exact]
        ):
            return query

        if self.state_name_exact:
            query &= sightings_q_by_state_name_exact(self.state_name_exact)
        if self.country_exact:
            query &= sightings_q_by_country_exact(self.country_exact)
        if self.state_exact:
            query &= sightings_q_by_state_exact(self.state_exact)
        if self.city_exact:
            query &= sightings_q_by_city_exact(self.city_exact)

        return query

    def filter_qs(self, query_set: QuerySet[Sighting]) -> QuerySet[Sighting]:
        if not query_set.exists():
            return query_set

        return query_set.filter(self.get_query())


class SightingsDateFilter(BaseFilter):
    def __init__(
        self,
        datetime_after: Optional[datetime],
        datetime_before: Optional[datetime],
        datetime_exact: Optional[datetime],
    ):
        self.datetime_after = datetime_after
        self.datetime_before = datetime_before
        self.datetime_exact = datetime_exact

    def validate(self) -> bool:
        if self.datetime_exact and (self.datetime_before or self.datetime_after):
            raise DatetimeInputValidationException('If datetimeExact is specified, no other datetime filters can be '
                                                   'specified.')
        if (self.datetime_before and self.datetime_after) and self.datetime_before <= self.datetime_after:
            raise DatetimeInputValidationException('datetimeBefore must be greater than datetimeAfter.')

        return True


    def get_query(self) -> Q:
        if self.datetime_exact:
            return Q()


class SightingsTimeFilter(BaseFilter):
    pass

