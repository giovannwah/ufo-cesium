from typing import Optional
from strawberry_django_plus.relay import to_base64
from django.db.models import Q
from sightings.models import Location
from sightings.gql.types.location import (
    LocationType,
    LocationNode,
)
from sightings.helpers.geocoding import (
    verify_location_coordinates,
    get_or_create_location,
)
from sightings.helpers.common import (
    generate_search_query,
    update_filter_args,
)


def locations_q_by_state_exact(state_exact: str, sightings=False, posts=False):
    if not state_exact:
        return Q()

    args = update_filter_args(
        {"state__iexact": state_exact},
        sightings=sightings,
        posts=posts,
    )

    return Q(**args)


def locations_q_by_state_name_exact(state_name_exact: str, sightings=False, posts=False):
    if not state_name_exact:
        return Q()

    args = update_filter_args(
        {"state_name__iexact": state_name_exact},
        sightings=sightings,
        posts=posts,
    )

    return Q(**args)


def locations_q_by_city_exact(city_exact: str, sightings=False, posts=False):
    if not city_exact:
        return Q()

    args = update_filter_args(
        {"city__iexact": city_exact},
        sightings=sightings,
        posts=posts,
    )

    return Q(**args)


def locations_q_by_country_exact(country_exact: str, sightings=False, posts=False):
    if not country_exact:
        return Q()

    args = update_filter_args(
        {"country__iexact": country_exact},
        sightings=sightings,
        posts=posts,
    )

    return Q(**args)


def locations_q_by_state_contains(state_contains: str, sightings=False, posts=False):
    if not state_contains:
        return Q()

    args = update_filter_args(
        {"state__icontains": state_contains},
        sightings=sightings,
        posts=posts,
    )

    return Q(**args)


def locations_q_by_city_contains(city_contains: str, sightings=False, posts=False):
    if not city_contains:
        return Q()

    args = update_filter_args(
        {"city__icontains": city_contains},
        sightings=sightings,
        posts=posts,
    )

    return Q(**args)


def locations_q_by_country_contains(country_contains: str, sightings=False, posts=False):
    if not country_contains:
        return Q()

    args = update_filter_args(
        {"country__icontains": country_contains},
        sightings=sightings,
        posts=posts,
    )

    return Q(**args)


def locations_q_by_state_name_contains(state_name_contains: str, sightings=False, posts=False):
    if not state_name_contains:
        return Q()

    args = update_filter_args(
        {"state_name__icontains": state_name_contains},
        sightings=sightings,
        posts=posts,
    )

    return Q(**args)


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
    return generate_search_query(q, contains_query)


def verify_and_create_location(location_input: dict) -> Optional[LocationType]:
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
        location = get_or_create_location(**location_input)
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
