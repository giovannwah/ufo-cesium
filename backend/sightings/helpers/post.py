from datetime import date, time
from django.db.models.query import Q
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


def posts_q_by_state_exact(state_exact: str):
    return locations_q_by_state_exact(state_exact=state_exact, posts=True)


def posts_q_by_state_name_exact(state_name_exact: str):
    return locations_q_by_state_name_exact(state_name_exact=state_name_exact, posts=True)


def posts_q_by_city_exact(city_exact: str):
    return locations_q_by_city_exact(city_exact=city_exact, posts=True)


def posts_q_by_country_exact(country_exact: str):
    return locations_q_by_country_exact(country_exact=country_exact, posts=True)


def posts_q_by_state_contains(state_contains: str):
    return locations_q_by_state_contains(state_contains=state_contains, posts=True)


def posts_q_by_city_contains(city_contains: str):
    return locations_q_by_city_contains(city_contains=city_contains, posts=True)


def posts_q_by_country_contains(country_contains: str):
    return locations_q_by_country_contains(country_contains=country_contains, posts=True)


def posts_q_by_state_name_contains(state_name_contains: str):
    return locations_q_by_state_name_contains(state_name_contains=state_name_contains, posts=True)


def posts_q_by_description_contains(q: str):
    return Q(description__icontains=q) if q else Q()


def posts_q_by_ufo_shape(shape: str):
    return Q(ufo_shape__iexact=shape) if shape else Q()


def location_contains_query(q: str):
    return (
            posts_q_by_country_contains(q) |
            posts_q_by_state_contains(q) |
            posts_q_by_city_contains(q) |
            posts_q_by_state_name_contains(q)
    )


def post_q_by_query_string(q: str):
    return location_contains_query(q) | Q(description__icontains=q)


def posts_q_by_search_query(q: str):
    if not q:
        return Q()

    return generate_search_query(q, post_q_by_query_string)


def posts_q_by_date_exact(date_exact: date):
    if not date_exact:
        return Q()

    return (Q(created_datetime__year=date_exact.year) &
            Q(created_datetime__month=date_exact.month) &
            Q(created_datetime__day=date_exact.day))


def posts_q_by_date_before(date_before: date):
    if not date_before:
        return Q()

    return Q(created_datetime__lt=date_before)


def posts_q_by_date_after(date_after: date):
    if not date_after:
        return Q()

    return Q(created_datetime__gt=date_after)


def posts_q_by_time_exact(time_exact: time):
    if not time_exact:
        return Q()

    return (Q(created_datetime__hour=time_exact.hour) &
            Q(created_datetime__minute=time_exact.minute) &
            Q(created_datetime__second=time_exact.second))


def posts_q_by_time_after(time_after: time):
    if not time_after:
        return Q()

    return Q(created_datetime__time__gt=time_after)


def posts_q_by_time_before(time_before: time):
    if not time_before:
        return Q()

    return Q(created_datetime__time__lt=time_before)


def posts_q_by_sighting_date_exact(date_exact: date):
    if not date_exact:
        return Q()

    return (Q(sighting__created_datetime__year=date_exact.year) &
            Q(sighting__created_datetime__month=date_exact.month) &
            Q(sighting__created_datetime__day=date_exact.day))


def posts_q_by_sighting_date_before(date_before: date):
    if not date_before:
        return Q()

    return Q(sighting__created_datetime__lt=date_before)


def posts_q_by_sighting_date_after(date_after: date):
    if not date_after:
        return Q()

    return Q(sighting__created_datetime__gt=date_after)


def posts_q_by_sighting_time_exact(time_exact: time):
    if not time_exact:
        return Q()

    return (Q(sighting__created_datetime__hour=time_exact.hour) &
            Q(sighting__created_datetime__minute=time_exact.minute) &
            Q(sighting__created_datetime__second=time_exact.second))


def posts_q_by_sighting_time_after(time_after: time):
    if not time_after:
        return Q()

    return Q(sighting__created_datetime__time__gt=time_after)


def posts_q_by_sighting_time_before(time_before: time):
    if not time_before:
        return Q()

    return Q(sighting__created_datetime__time__lt=time_before)