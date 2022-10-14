from datetime import datetime
from django.db.models.query import QuerySet
from django.db.models import Q
from sightings.gql.types.sighting import SightingFilterInput
from sightings.gql.types.location import LocationFilterInput
from sightings.gql.types.sorting import SortInput
from sightings.models import Sighting
from sightings.helpers.common import get_order_by_field
from sightings.helpers.locations import locations_filter_sort
from sightings.helpers.geocoding import (
    find_sightings_by_distance_outside,
    find_sightings_by_distance_within,
)


def sightings_q_by_datetime_exact(dt: datetime):
    return Q()


def filter_sightings_by_location(
    location_filter: LocationFilterInput,
    sightings: QuerySet = None
):
    """
    Filter sighting objects by location filter
    :param location_filter: LocationFilterInput object
    :param sightings: QuerySet of Sightings
    """
    locations = locations_filter_sort(location_filter=location_filter)
    lids = [location.id for location in locations]

    if sightings:
        return sightings.filter(location__id__in=lids)

    return Sighting.objects.all().filter(location__id__in=lids)


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

