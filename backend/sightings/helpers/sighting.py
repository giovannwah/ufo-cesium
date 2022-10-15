from datetime import datetime
from django.db.models.query import QuerySet
from django.db.models import Q
from sightings.gql.types.sighting import SightingFilterInput
from sightings.gql.types.location import LocationFilterInput
from sightings.gql.types.sorting import SortInput
from sightings.models import Sighting
from sightings.helpers.common import get_order_by_field
# from sightings.helpers.locations import locations_filter_sort
from sightings.helpers.geocoding import (
    find_sightings_by_distance_outside,
    find_sightings_by_distance_within,
)
from sightings.helpers.common import generate_search_query


def filter_sightings_by_location(
    location_filter: LocationFilterInput,
    sightings: QuerySet = None
):
    """
    Filter sighting objects by location filter
    :param location_filter: LocationFilterInput object
    :param sightings: QuerySet of Sightings
    """
    # locations = locations_filter_sort(location_filter=location_filter)
    # lids = [location.id for location in locations]
    #
    # if sightings:
    #     return sightings.filter(location__id__in=lids)
    #
    # return Sighting.objects.all().filter(location__id__in=lids)
    return Sighting.objects.all()


def sightings_q_by_state_exact(state_exact: str):
    return Q(location__state__iexact=state_exact) if state_exact else Q()


def sightings_q_by_state_name_exact(state_name_exact: str):
    return Q(location__state_name__iexact=state_name_exact) if state_name_exact else Q()


def sightings_q_by_city_exact(city_exact: str):
    return Q(location__city__iexact=city_exact) if city_exact else Q()


def sightings_q_by_country_exact(country_exact: str):
    return Q(location__country__iexact=country_exact) if country_exact else Q()


def sightings_q_by_state_contains(state_contains: str):
    return Q(location__state__icontains=state_contains) if state_contains else Q()


def sightings_q_by_city_contains(city_contains: str):
    return Q(location__city__icontains=city_contains) if city_contains else Q()


def sightings_q_by_country_contains(country_contains: str):
    return Q(location__country__icontains=country_contains) if country_contains else Q()


def sightings_q_by_state_name_contains(state_name_contains: str):
    return Q(location__state_name__icontains=state_name_contains) if state_name_contains else Q()


def contains_query(q: str):
    return (
        sightings_q_by_country_contains(q) |
        sightings_q_by_state_contains(q) |
        sightings_q_by_city_contains(q) |
        sightings_q_by_state_name_contains(q)
    )


def sightings_q_by_search_query(q: str):
    return generate_search_query(q, contains_query)


def sightings_filter_sort(
    sighting_filter: SightingFilterInput = None,
    sort: SortInput = None,
):
    """
    Given a sighting filter and sort input, filter and sort Sightings
    :param sighting_filter: SightingFilterInput object
    :param sort: SortInput object
    :return: Sighting queryset
    """
    sightings = Sighting.objects.all()
    # no filter or sort input provided, return all Sightings
    if not sighting_filter and not sort:
        return sightings

    if sighting_filter:
        location_filter = sighting_filter.location_filter
        datetime_filter = sighting_filter.datetime_filter
        location_ids = sighting_filter.location_ids
    else:
        location_filter = datetime_filter = location_ids = None

    if location_filter:
        sightings = filter_sightings_by_location(location_filter)

    elif location_ids:
        sightings = Sighting.objects.all().filter(location__id__in=location_ids)

    if datetime_filter:
        pass

    if sort:
        pass
