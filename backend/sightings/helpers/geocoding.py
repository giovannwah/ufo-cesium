from typing import Optional
from django.db.models import Q
from django.db.models.query import QuerySet
from django.conf import settings
from geopy.geocoders import (
    get_geocoder_for_service,
    GeocoderNotFound,
)
from geopy import distance
from sightings.exceptions import LocationInputValidationException
from sightings.models import (
    Location,
    Sighting,
)


STATE_MAP = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming"
}


def generate_geocoder_config_for_service(service: str) -> Optional[dict]:
    """
    Return service config for a given geocoding service
    :param service:
    :return:
    """
    if service == 'nominatim':
        return {
            "user_agent": "ufo-cesium"
        }

    return None


def validate_longitude_latitude(longitude: float, latitude: float) -> bool:
    """
    Verify that longitude and latitude values are valid
    """
    return abs(longitude) <= 180 and abs(latitude) <= 90


def evaluate_query(
    services: list, query: str, city: str = None, country: str = None, state: str = None
) -> bool:
    """
    Evaluate whether a location query, "<latitude>, <longitude>", corresponds to an existing
    location, using geocoders listed in services
    :param services: list of services to use to build geocoders
    :param query: string, "<latitude>, <longitude>"
    :param city:
    :param country:
    :param state:
    """
    for service in services:
        try:
            cls = get_geocoder_for_service(service)
            config = generate_geocoder_config_for_service(service)

            geolocator = cls(**config)
            location = geolocator.reverse(query, language='en', zoom=10)

            address = location.raw.get('address')
            city_or_town = address.get('city') if 'city' in address else address.get('town', "")

            if city and city.lower() != city_or_town.lower():
                continue

            if country and country.lower() != address.get('country', "").lower():
                continue

            if state and state.lower() != address.get('state', "").lower() and \
                    STATE_MAP.get(state.upper()) != address.get('state', "").lower():
                continue

            return True

        except GeocoderNotFound:
            continue

    return False


def verify_location_coordinates(
    latitude: float, longitude: float, city: str = None, country: str = None, state: str = None
) -> bool:
    """
    Verify that the latitude and longitude values provided correspond to accurately to the
    provided country/city/state values
    """
    query = f"{latitude}, {longitude}"

    if not validate_longitude_latitude(longitude=longitude, latitude=latitude):
        msg = f'Invalid latitude, longitude: ({query})'
        raise LocationInputValidationException(msg)

    if country is None and state is None and city is None:
        return True

    # geocoder services to loop through in order to validate address
    geocoder_services = ['nominatim']

    return evaluate_query(
        services=geocoder_services, query=query, city=city, country=country, state=state,
    )


def generate_lat_lon_nearby_query(latitude: float, longitude: float, precision: float):
    """
    Generate a simple location-based query given the precision error value
    """
    return Q(
        latitude__lt=latitude + precision,
        latitude__gt=latitude - precision,
        longitude__lt=longitude + precision,
        longitude__gt=longitude - precision,
    )


def find_closest_location(locations: QuerySet, latitude: float, longitude: float):
    """
    Find location in locations that is closest in distance to latitude and longitude, and within
    the LOCATION_DISTANCE_THRESHOLD
    """
    diff = float('inf')
    nearest = None
    for location in locations:
        dist = distance.distance((location.latitude, location.longitude), (latitude, longitude)).meters
        if dist <= settings.LOCATION_DISTANCE_THRESHOLD and dist < diff:
            diff = dist
            nearest = location

    return nearest


def map_state_abr_to_name(state_abr: str):
    """
    Maps a state abbreviation to the correct state name.
    """
    if state_abr is None:
        return None

    return STATE_MAP.get(state_abr.upper(), None)


def create_and_validate_location(
    latitude: float, longitude: float, city: str = None, country: str = None, state: str = None
) -> Optional[Location]:
    """
    Verify the new Location can be added given existing Locations. If the new location is
    within a certain distance threshold of an existing location, return the nearest location.
    Otherwise, return new Location.
    :return:
    """
    query = generate_lat_lon_nearby_query(latitude, longitude, 0.001)  # 0.001 is an arbitrary precision value
    locations = Location.objects.filter(query)
    nl = find_closest_location(locations, latitude, longitude)

    if nl is None:
        state_name = map_state_abr_to_name(state.upper()) if state else None
        loc = Location(
            latitude=latitude,
            longitude=longitude,
            city=city,
            country=country,
            state=state.upper() if state else None,
            state_name=state_name
        )
        return loc

    return nl


def locations_distance_within_q(
    locations: QuerySet, latitude: float, longitude: float, arc_length: float
):
    ids = []
    for location in locations:
        dist = distance.distance((location.latitude, location.longitude), (latitude, longitude)).meters
        if dist <= arc_length:
            ids.append(location.id)

    return Q(id__in=ids)


def find_locations_by_distance_within(
    locations: QuerySet, latitude: float, longitude: float, arc_length: float
):
    """
    Return all locations within a given distance in meters from a point
    :param locations:
    :param latitude:
    :param longitude:
    :param arc_length:
    :return:
    """
    query = locations_distance_within_q(
        locations, latitude, longitude, arc_length
    )
    return locations.filter(query)


def locations_distance_outside_q(
    locations: QuerySet, latitude: float, longitude: float, arc_length: float
):
    ids = []
    for location in locations:
        dist = distance.distance((location.latitude, location.longitude), (latitude, longitude)).meters
        if dist > arc_length:
            ids.append(location.id)

    return Q(id__in=ids)


def find_locations_by_distance_outside(
    locations: QuerySet, latitude: float, longitude: float, arc_length: float
):
    """
    Return all locations outside a given distance in meters from a certain point
    :param locations:
    :param latitude:
    :param longitude:
    :param arc_length: distance in meters
    :return:
    """
    query = locations_distance_within_q(
        locations, latitude, longitude, arc_length,
    )
    return locations.filter(query)


def sightings_distance_within_q(
    sightings: QuerySet, latitude: float, longitude: float, arc_length: float
):
    ids = []
    for sighting in sightings:
        dist = distance.distance(
            (sighting.location.latitude, sighting.location.longitude),
            (latitude, longitude)
        ).meters
        if dist <= arc_length:
            ids.append(sighting.location.id)

    return Q(id__in=ids)


def find_sightings_by_distance_within(
    sightings: QuerySet, latitude: float, longitude: float, arc_length: float
):
    """
    Return all sightings within a given distance in meters from a point
    :param sightings:
    :param latitude:
    :param longitude:
    :param arc_length: distance in meters
    :return:
    """
    query = sightings_distance_within_q(
        sightings, latitude, longitude, arc_length,
    )
    return sightings.filter(query)


def sightings_distance_outside_q(
    sightings: QuerySet, latitude: float, longitude: float, arc_length: float
):
    ids = []
    for sighting in sightings:
        dist = distance.distance(
            (sighting.location.latitude, sighting.location.longitude),
            (latitude, longitude)
        ).meters
        if dist > arc_length:
            ids.append(sighting.location.id)

    return Q(id__in=ids)


def find_sightings_by_distance_outside(
    sightings: QuerySet, latitude: float, longitude: float, arc_length: float
):
    """
    Return all sightings outside a given distance in meters from a point
    :param sightings:
    :param latitude:
    :param longitude:
    :param arc_length: distance in meters
    """
    query = sightings_distance_outside_q(
        sightings, latitude, longitude, arc_length,
    )
    return sightings.filter(query)
