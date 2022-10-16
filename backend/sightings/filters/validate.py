from typing import List
from sightings.filters.base import BaseFilter
from sightings.filters.locations import (
    LocationExactFilter,
    LocationQueryStringFilter,
    DistanceFromFilter
)
from sightings.filters.sightings import (
    SightingsDistanceFromFilter,
    SightingsLocationExactFilter,
    SightingsLocationQueryStringFilter,
    SightingsDateFilter,
    SightingsTimeFilter,
)
from sightings.gql.types.location import LocationFilterInput
from sightings.gql.types.sighting import SightingFilterInput


def validate_filters(filters: List[BaseFilter]) -> bool:
    """
    Validate a list of filter instances
    """
    for filtuh in filters:
        filtuh.validate()

    return True


def get_location_filters(linput: LocationFilterInput):
    ret = []
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

    return ret


def get_sighting_filters(sfi: SightingFilterInput):
    ret = []
    loc_input = sfi.location_filter if sfi else None
    sdt_input = sfi.sighting_datetime_filter

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

    return ret
