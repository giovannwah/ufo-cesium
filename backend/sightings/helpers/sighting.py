from datetime import date, time
from django.db.models import Q
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
