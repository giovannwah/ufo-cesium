from typing import Optional, List
from strawberry_django_plus.relay import from_base64
from django.db.models.query import Q
from sightings.filters.base import SimpleFilter
from sightings.filters.datetime import (
    DateFilter,
    TimeFilter
)
from sightings.filters.locations import DistanceFromFilter
from sightings.exceptions import (
    SightingInputValidationException,
)
from sightings.helpers.sighting import (
    sightings_q_by_search_query,
    sightings_q_by_state_name_exact,
    sightings_q_by_state_exact,
    sightings_q_by_city_exact,
    sightings_q_by_country_exact,
)
from sightings.gql.types.sighting import SightingFilterInput


class SightingsLocationQueryStringFilter(SimpleFilter):
    """
    Filter sightings by location query
    """
    def __init__(self, q: Optional[str] = None):
        self.q = q

    def get_query(self) -> Q:
        if self.q is None or self.q.strip() == "":
            return Q()

        return sightings_q_by_search_query(self.q)


class SightingsLocationExactFilter(SimpleFilter):
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


class SightingsLocationIdsFilter(SimpleFilter):
    def __init__(self, location_ids: List[str]):
        self.location_ids = location_ids

    def get_query(self) -> Q:
        return Q(location__id__in=[from_base64(loc)[1] for loc in self.location_ids])


class SightingsSightingIdsFilter(SimpleFilter):
    def __init__(self, sighting_ids: List[str]):
        self.sighting_ids = sighting_ids

    def get_query(self) -> Q:
        return Q(id__in=[from_base64(sighting)[1] for sighting in self.sighting_ids])


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
                    pre="sighting_datetime"
                )
            )

        if sdt_input.time_before or sdt_input.time_after or sdt_input.time_exact:
            ret.append(
                TimeFilter(
                    time_after=sdt_input.time_after,
                    time_before=sdt_input.time_before,
                    time_exact=sdt_input.time_exact,
                    pre="sighting_datetime"
                )
            )

    if loc_ids:
        ret.append(
            SightingsLocationIdsFilter(
                location_ids=loc_ids
            )
        )

    return ret
