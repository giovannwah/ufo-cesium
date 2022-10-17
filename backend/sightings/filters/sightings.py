from typing import Optional, List
from strawberry_django_plus.relay import from_base64
from datetime import date, time
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
    sightings_q_by_date_exact,
    sightings_q_by_date_after,
    sightings_q_by_date_before,
    sightings_q_by_time_exact,
    sightings_q_by_time_after,
    sightings_q_by_time_before,
)
from sightings.gql.types.sighting import SightingFilterInput


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


class SightingsLocationIds(BaseFilter):
    def __init__(self, location_ids: List[str]):
        self.location_ids = location_ids

    def validate(self) -> bool:
        return True

    def get_query(self) -> Q:
        # assuming location_ids are relay global ids
        return Q(location__id__in=[from_base64(loc)[1] for loc in self.location_ids])

    def filter_qs(self, query_set: QuerySet[Sighting]) -> QuerySet[Sighting]:
        if not query_set.exists():
            return query_set

        return query_set.filter(self.get_query())


class SightingsDateFilter(BaseFilter):
    def __init__(
        self,
        date_after: Optional[date],
        date_before: Optional[date],
        date_exact: Optional[date],
    ):
        self.date_after = date_after
        self.date_before = date_before
        self.date_exact = date_exact

    def validate(self) -> bool:
        if not self.date_exact and not self.date_before and not self.date_after:
            msg = 'Must provide either dateExact or dateBefore/dateAfter arguments'
            raise DatetimeInputValidationException(msg)

        if self.date_exact and (self.date_before or self.date_after):
            msg = 'If dateExact is specified, no other date arguments can be specified.'
            raise DatetimeInputValidationException(msg)

        if (self.date_before and self.date_after) and self.date_before <= self.date_after:
            msg = 'dateBefore must be greater than dateAfter.'
            raise DatetimeInputValidationException(msg)

        return True

    def get_query(self) -> Q:
        if self.date_exact:
            return sightings_q_by_date_exact(self.date_exact)
        elif self.date_after:
            return sightings_q_by_date_after(self.date_after) if not self.date_before else \
                (
                    sightings_q_by_date_after(self.date_after)
                    & sightings_q_by_date_before(self.date_before)
                )
        else:
            return sightings_q_by_date_before(self.date_before)

    def filter_qs(self, query_set: QuerySet[Sighting]) -> QuerySet[Sighting]:
        if not query_set.exists():
            return query_set

        return query_set.filter(self.get_query())


class SightingsTimeFilter(BaseFilter):
    def __init__(
        self,
        time_after: Optional[time],
        time_before: Optional[time],
        time_exact: Optional[time],
    ):
        self.time_after = time_after
        self.time_before = time_before
        self.time_exact = time_exact

    def validate(self) -> bool:
        if not self.time_exact and not self.time_before and not self.time_after:
            msg = 'Must provide either timeExact or timeBefore/timeAfter arguments'
            raise DatetimeInputValidationException(msg)

        if self.time_exact and (self.time_before or self.time_after):
            msg = 'If timeExact is specified, no other time arguments can be specified.'
            raise DatetimeInputValidationException(msg)

        if (self.time_before and self.time_after) and self.time_before <= self.time_after:
            msg = 'timeBefore must be greater than timeAfter.'
            raise DatetimeInputValidationException(msg)

        return True

    def get_query(self) -> Q:
        if self.time_exact:
            return sightings_q_by_time_exact(self.time_exact)
        elif self.time_after:
            return sightings_q_by_time_after(self.time_after) if not self.time_before else \
                (
                    sightings_q_by_time_after(self.time_after)
                    & sightings_q_by_time_before(self.time_before)
                )
        else:
            return sightings_q_by_time_before(self.time_before)

    def filter_qs(self, query_set: QuerySet[Sighting]) -> QuerySet[Sighting]:
        if not query_set.exists():
            return query_set

        return query_set.filter(self.get_query())


def get_sighting_filters(sfi: SightingFilterInput):
    ret = []
    loc_input = sfi.location_filter if sfi else None
    sdt_input = sfi.sighting_datetime_filter if sfi else None
    loc_ids = sfi.location_ids if sfi else None

    if loc_input:
        if loc_input.city_exact or loc_input.state_exact or loc_input.country_exact or loc_input.state_name_exact:
            ret.append(
                SightingsLocationExactFilter(
                    city_exact=loc_input.city_exact,
                    state_exact=loc_input.state_exact,
                    state_name_exact=loc_input.state_name_exact,
                    country_exact=loc_input.country_exact
                )
            )

        if loc_input.q:
            ret.append(
                SightingsLocationQueryStringFilter(
                    q=loc_input.q
                )
            )

        if loc_input.distance_from:
            ret.append(
                SightingsDistanceFromFilter(
                    longitude=loc_input.distance_from.longitude,
                    latitude=loc_input.distance_from.latitude,
                    arc_length=loc_input.distance_from.arc_length,
                    inside_circle=loc_input.distance_from.inside_circle,
                )
            )

    if sdt_input:
        if sdt_input.date_before or sdt_input.date_after or sdt_input.date_exact:
            ret.append(
                SightingsDateFilter(
                    date_after=sdt_input.date_after,
                    date_before=sdt_input.date_before,
                    date_exact=sdt_input.date_exact,
                )
            )

        if sdt_input.time_before or sdt_input.time_after or sdt_input.time_exact:
            ret.append(
                SightingsTimeFilter(
                    time_after=sdt_input.time_after,
                    time_before=sdt_input.time_before,
                    time_exact=sdt_input.time_exact,
                )
            )

    if loc_ids:
        ret.append(
            SightingsLocationIds(
                location_ids=loc_ids
            )
        )

    return ret
