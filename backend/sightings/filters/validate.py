from typing import List
from sightings.filters.base import BaseFilter
from sightings.filters.locations import (
    LocationExactFilter,
    LocationQueryStringFilter,
    DistanceFromFilter
)
from sightings.gql.types.location import LocationFilterInput


def validate_filters(filters: List[BaseFilter]) -> bool:
    """
    Validate a list of filter instances
    :param filters:
    :return:
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
