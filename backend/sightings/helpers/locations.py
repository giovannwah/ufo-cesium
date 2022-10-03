from typing import Optional
from django.db.models import Q
from sightings.gql.types.sorting import SortInput
from sightings.models import Location
from sightings.helpers.common import get_order_by_field
from sightings.gql.types.location import LocationType
from sightings.models import Location
from sightings.helpers.geocoding import validate_location_coordinates, STATE_MAP


def locations_q_by_state_exact(state_exact: str):
    return Q(state__iexact=state_exact) if state_exact else Q()


def locations_q_by_state_name_exact(state_name_exact: str):
    return Q(state_name__iexact=state_name_exact) if state_name_exact else Q()


def locations_q_by_city_exact(city_exact: str):
    return Q(city__iexact=city_exact) if city_exact else Q()


def locations_q_by_country_exact(country_exact: str):
    return Q(country__iexact=country_exact) if country_exact else Q()


def locations_q_by_state_contains(state_contains: str):
    return Q(state__icontains=state_contains) if state_contains else Q()


def locations_q_by_city_contains(city_contains: str):
    return Q(city__icontains=city_contains) if city_contains else Q()


def locations_q_by_country_contains(country_contains: str):
    return Q(country__icontains=country_contains) if country_contains else Q()


def locations_q_by_state_name_contains(state_name_contains: str):
    return Q(state_name__icontains=state_name_contains) if state_name_contains else Q()


def contains_query(q: str):
    return (
            locations_q_by_country_contains(q) |
            locations_q_by_state_contains(q) |
            locations_q_by_city_contains(q) |
            locations_q_by_state_name_contains(q)
    )


def locations_q_by_search_query(q: str):
    """
    Split up query string and turn each into a separate Q() object to be combined
    into a single "&" query.
    :param q: query string, space separated
    :return: django Q object
    """
    query_terms = list(map(contains_query, q.split(' ')))
    query = Q()
    for term in query_terms:
        query &= term

    return query


def locations_filter_sort(
    city_exact: str = None,
    state_exact: str = None,
    state_name_exact: str = None,
    country_exact: str = None,
    q: str = None,
    sort: SortInput = None
):
    """
    Given filter values city_exact, state_exact, state_name_exact, and country_exact, query string q, and sort object,
    filter and sort Locations
    :param city_exact: city name, case-insensitive
    :param state_exact: state abbreviation, case-insensitive
    :param state_name_exact: exact state name, case-insensitive
    :param country_exact: exact country name, case-insensitive
    :param q: query string, space separated
    :param sort: SortInput object
    :return: Locations queryset
    """
    if any(i.strip() == "" for i in [city_exact, state_exact, state_name_exact, country_exact, q] if i is not None):
        return Location.objects.none()

    if all(i is None for i in [city_exact, state_exact, state_name_exact, country_exact, q]):
        locations = Location.objects.all()

    elif q:
        query = (
            locations_q_by_search_query(q) &
            locations_q_by_state_name_exact(state_name_exact) &
            locations_q_by_country_exact(country_exact) &
            locations_q_by_state_exact(state_exact) &
            locations_q_by_city_exact(city_exact)
        )
        locations = Location.objects.all().filter(query)

    else:
        query = (
            locations_q_by_state_name_exact(state_name_exact) &
            locations_q_by_country_exact(country_exact) &
            locations_q_by_state_exact(state_exact) &
            locations_q_by_city_exact(city_exact)
        )
        locations = Location.objects.all().filter(query)

    if sort:
        order = get_order_by_field(sort.order, sort.field)
        locations = locations.order_by(order)

    return locations


def map_state_abr_to_name(state_abr: str):
    """
    Maps a state abbreviation to the correct state name.
    :param state_abr:
    :return:
    """
    if state_abr is None:
        return None

    return STATE_MAP.get(state_abr.upper(), None)


def create_location(location_input: dict) -> Optional[LocationType]:
    """
    Create a new Location object in the database, and return a LocationType, if input passes validation and

    input: dict - dictionary containing parameters to create a new Location

    {
        "latitude": float,
        "longitude": float,
        "country": str,
        "city": str,
        "state": Optional[str]
    }
    :return:
    """
    if validate_location_coordinates(**location_input):
        return LocationType(
            **location_input,
            state_name=map_state_abr_to_name(location_input["state"])
        )

    return None
