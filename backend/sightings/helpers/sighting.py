from datetime import date, time
from django.db.models import Q
from sightings.helpers.common import generate_search_query


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


def sightings_q_by_date_exact(date_exact: date):
    return Q(
       sighting_datetime__year=date_exact.year,
       sighting_datetime__month=date_exact.month,
       sighting_datetime__day=date_exact.day,
    ) if date_exact else Q()


def sightings_q_by_date_after(date_after: date):
    return Q(sighting_datetime__gt=date_after) if date_after else Q()


def sightings_q_by_date_before(date_before: date):
    return Q(sighting_datetime__lt=date_before) if date_before else Q()


def sightings_q_by_time_exact(time_exact: time):
    return Q(
        sighting_datetime__hour=time_exact.hour,
        sighting_datetime__minute=time_exact.minute,
        sighting_datetime__second=time_exact.second,
    ) if time_exact else Q()


def sightings_q_by_time_after(time_after: time):
    return Q(sighting_datetime__time__gt=time_after) if time_after else Q()


def sightings_q_by_time_before(time_before: time):
    return Q(sighting_datetime__time__lt=time_before) if time_before else Q()


def contains_query(q: str):
    return (
        sightings_q_by_country_contains(q) |
        sightings_q_by_state_contains(q) |
        sightings_q_by_city_contains(q) |
        sightings_q_by_state_name_contains(q)
    )


def sightings_q_by_search_query(q: str):
    return generate_search_query(q, contains_query)
