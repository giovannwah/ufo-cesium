from typing import Optional
from strawberry_django_plus.relay import from_base64, to_base64
from datetime import datetime, date, time, timedelta
from django.db.models import Q
from django.conf import settings
from sightings.models import Sighting, Location
from sightings.helpers.common import (
    generate_search_query,
    update_filter_args,
)
from sightings.helpers.locations import (
    locations_q_by_state_contains,
    locations_q_by_state_name_contains,
    locations_q_by_city_contains,
    locations_q_by_country_contains,
    locations_q_by_state_exact,
    locations_q_by_state_name_exact,
    locations_q_by_city_exact,
    locations_q_by_country_exact,
)
from sightings.gql.types.sighting import SightingType, SightingNode
from sightings.helpers.geocoding import get_or_create_location


def sightings_q_by_state_exact(state_exact: str):
    return locations_q_by_state_exact(state_exact=state_exact, sightings=True)


def sightings_q_by_state_name_exact(state_name_exact: str):
    return locations_q_by_state_name_exact(state_name_exact=state_name_exact, sightings=True)


def sightings_q_by_city_exact(city_exact: str):
    return locations_q_by_city_exact(city_exact=city_exact, sightings=True)


def sightings_q_by_country_exact(country_exact: str):
    return locations_q_by_country_exact(country_exact=country_exact, sightings=True)


def sightings_q_by_state_contains(state_contains: str):
    return locations_q_by_state_contains(state_contains=state_contains, sightings=True)


def sightings_q_by_city_contains(city_contains: str):
    return locations_q_by_city_contains(city_contains=city_contains, sightings=True)


def sightings_q_by_country_contains(country_contains: str):
    return locations_q_by_country_contains(country_contains=country_contains, sightings=True)


def sightings_q_by_state_name_contains(state_name_contains: str):
    return locations_q_by_state_name_contains(state_name_contains=state_name_contains, sightings=True)


def sightings_q_by_date_exact(date_exact: date, posts: bool = False):
    if not date_exact:
        return Q()

    args = update_filter_args(
        {
            "sighting_datetime__year": date_exact.year,
            "sighting_datetime__month": date_exact.month,
            "sighting_datetime__day": date_exact.day,
        },
        posts=posts
    )

    return Q(**args)


def sightings_q_by_date_after(date_after: date, posts: bool = False):
    if not date_after:
        return Q()

    args = update_filter_args(
        {"sighting_datetime__gt": date_after},
        posts=posts
    )

    return Q(**args)


def sightings_q_by_date_before(date_before: date, posts: bool = False):
    if not date_before:
        return Q()

    args = update_filter_args(
        {"sighting_datetime__lt": date_before},
        posts=posts
    )

    return Q(**args)


def sightings_q_by_time_exact(time_exact: time, posts: bool = False):
    if not time_exact:
        return Q()

    args = update_filter_args(
        {
            "sighting_datetime__hour": time_exact.hour,
            "sighting_datetime__minute": time_exact.minute,
            "sighting_datetime__second": time_exact.second
        },
        posts=posts
    )

    return Q(**args)


def sightings_q_by_time_after(time_after: time, posts: bool = False):
    if not time_after:
        return Q()

    args = update_filter_args(
        {"sighting_datetime__time__gt": time_after},
        posts=posts
    )

    return Q(**args)


def sightings_q_by_time_before(time_before: time, posts: bool = False):
    if not time_before:
        return Q()

    args = update_filter_args(
        {"sighting_datetime__time__lt": time_before},
        posts=posts
    )

    return Q(**args)


def contains_query(q: str):
    return (
        sightings_q_by_country_contains(q) |
        sightings_q_by_state_contains(q) |
        sightings_q_by_city_contains(q) |
        sightings_q_by_state_name_contains(q)
    )


def sightings_q_by_search_query(q: str):
    return generate_search_query(q, contains_query)


def get_or_create_sighting(
    sighting_id: str = None,
    location: Location = None,
    sighting_datetime: datetime = None,
) -> Optional[Sighting]:
    """
    Verify that new Sighting can be added given existing Sightings.
    :param sighting_id:
    :param location:
    :param sighting_datetime:
    :return:
    """

    if sighting_id:
        sighting = Sighting.objects.filter(pk=from_base64(sighting_id)[1]).first()
    else:
        start_dt = sighting_datetime - timedelta(seconds=settings.SIGHTING_TIME_THRESHOLD)
        end_dt = sighting_datetime + timedelta(seconds=settings.SIGHTING_TIME_THRESHOLD)
        # get all sightings near the proposed new sighting
        nearby_sightings = Sighting.objects.filter(
            location=location,
            sighting_datetime__range=(start_dt, end_dt)
        )
        if nearby_sightings:
            # get the sighting that is closest in time to the proposed new sighting
            sighting = nearby_sightings.first()
            thresh = abs((sighting.sighting_datetime-sighting_datetime).seconds)
            for s in nearby_sightings:
                secs = abs((s.sighting_datetime-sighting_datetime).seconds)
                if secs < thresh:
                    sighting = s
                    thresh = secs
        else:
            sighting = None

    if sighting is None:
        # create a brand-new sighting, since the proposed datetime and location seem to be new
        sighting = Sighting(
            location=location,
            sighting_datetime=sighting_datetime,
        )
        sighting.save()

    return sighting


def verify_and_create_sighting(sighting_input: dict) -> SightingType:
    location_input = sighting_input.get('location_input')
    sighting_datetime = sighting_input.get('sighting_datetime')

    location = get_or_create_location(**location_input)
    sighting_dt = datetime.fromisoformat(sighting_datetime)

    sighting = get_or_create_sighting(
        location=location,
        sighting_datetime=sighting_dt
    )

    return SightingType(
        id=to_base64(SightingNode.__name__, sighting.pk),
        location=location,
        sighting_datetime=sighting.sighting_datetime,
        created_datetime=sighting.created_datetime,
        modified_datetime=sighting.modified_datetime,
    )
