from typing import Optional, List
from strawberry_django_plus.relay import from_base64
from django.db.models.query import Q
from sightings.filters.base import SimpleFilter
from sightings.filters.datetime import (
    DateFilter,
    TimeFilter
)
from sightings.filters.locations import DistanceFromFilter
from sightings.helpers.sighting import (
    sightings_q_by_search_query,
)
from sightings.gql.types.sighting import SightingFilterInput
from sightings.filters.locations import LocationExactFilter


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

    if sfi:
        loc_input = getattr(sfi, "location_filter", None)
        sdt_input = getattr(sfi, "sighting_datetime_filter", None)
        loc_ids = getattr(sfi, "location_ids", None)

        if loc_input:
            if loc_input.city_exact or loc_input.state_exact or loc_input.country_exact or loc_input.state_name_exact:
                ret.append(
                    LocationExactFilter(
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
