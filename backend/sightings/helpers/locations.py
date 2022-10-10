from typing import Optional
from strawberry_django_plus.relay import to_base64
from django.db.models import Q
from sightings.gql.types.sorting import SortInput
from sightings.helpers.common import get_order_by_field
from sightings.gql.types.location import (
    LocationType,
    LocationNode,
    LocationFilterInput,
)
from sightings.models import Location
from sightings.helpers.geocoding import (
    verify_location_coordinates,
    create_and_validate_location,
    find_locations_by_distance_within,
    find_locations_by_distance_outside
)


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
    location_filter: LocationFilterInput = None,
    sort: SortInput = None
):
    """
    Given filter values city_exact, state_exact, state_name_exact, and country_exact, query string q, and sort object,
    filter and sort Locations
    :param location_filter: LocationFilterInput object
    :param sort: SortInput object
    :return: Locations queryset
    """
    if location_filter:
        city_exact = location_filter.city_exact
        state_exact = location_filter.state_exact
        state_name_exact = location_filter.state_name_exact
        country_exact = location_filter.country_exact
        distance_from = location_filter.distance_from
        q = location_filter.q
    else:
        city_exact = state_exact = state_name_exact = country_exact = q = distance_from = None

    # the assumption is that an intentional search for an empty string in any of these fields should yield no results
    if any(i.strip() == "" for i in [city_exact, state_exact, state_name_exact, country_exact, q] if i is not None):
        return Location.objects.none()

    # the assumption is that if all filter options are None, then just return all locations with no filtering
    if all(i is None for i in [city_exact, state_exact, state_name_exact, country_exact, distance_from, q]):
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

    if distance_from:
        # Filter found locations
        if distance_from.inside_circle:
            locations = find_locations_by_distance_within(
                locations, distance_from.latitude, distance_from.longitude, distance_from.arc_length
            )
        else:
            locations = find_locations_by_distance_outside(
                locations, distance_from.latitude, distance_from.longitude, distance_from.arc_length
            )

    if sort:
        order = get_order_by_field(sort.order, sort.field)
        locations = locations.order_by(order)

    return locations


def create_location(location_input: dict) -> Optional[LocationType]:
    """
    Create a new Location object in the database, and return a LocationType, if input passes validation and

    input: dict - dictionary containing parameters to create a new Location

    {
        "latitude": float,
        "longitude": float,
        "country": Union[str, None],
        "city": Union[str, None],
        "state": Union[str, None]
    }
    :return: LocationType
    """

    if verify_location_coordinates(**location_input):
        location = create_and_validate_location(**location_input)
        location.save()
        return LocationType(
            id=to_base64(LocationNode.__name__, location.pk),
            latitude=location.latitude,
            longitude=location.longitude,
            city=location.city,
            state=location.state,
            state_name=location.state_name,
            country=location.country,
        )

    return None
