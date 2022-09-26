from django.db.models import Q
from sightings.gql.types.sorting import SortInput, SortOrder
from sightings.models import Location
from sightings.helpers.common import get_order_by_field


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


def locations_q_by_search_query(q: str):
    return (
        locations_q_by_country_contains(q) |
        locations_q_by_state_contains(q) |
        locations_q_by_city_contains(q) |
        locations_q_by_state_name_contains(q)
    )


def locations_filter_sort(
    city_exact: str = None,
    state_exact: str = None,
    state_name_exact: str = None,
    country_exact: str = None,
    q: str = None,
    sort: SortInput = None
):

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
