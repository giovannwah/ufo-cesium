from typing import Optional
from strawberry_django_plus.relay import from_base64
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
    Post
)
from sightings.helpers.common import update_filter_args


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

CLOSE_ENOUGH = 0.001  # an arbitrary latitude/longitude precision threshold value


def distance_to_degrees(meters: float) -> float:
    if meters > 100000:
        msg = f"meters argument must be less than 100000. meters = {meters}"
        raise ValueError(msg)

    if 100000 >= meters > 10000:
        return 1.0
    elif 10000 >= meters > 1000:
        return 0.1
    elif 1000 >= meters > 100:
        return 0.01
    elif 100 >= meters > 10:
        return 0.001

    return 0.0001


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
    Evaluate whether a location query, "<latitude>, <longitude>", corresponds to real
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

            try:
                address = location.raw.get('address')
            except AttributeError as e:
                raise LocationInputValidationException(
                    f'Unable to validate latitude and longitude ({query}): {e}'
                )
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


def generate_lat_lon_nearby_query(
        latitude: float, longitude: float, precision: float, sightings: bool = False, posts: bool = False
):
    """
    Generate a simple location-based query given the precision error value
    """
    args = update_filter_args(
        args={
            "latitude__lt": latitude + precision,
            "latitude__gt": latitude - precision,
            "longitude__lt": longitude + precision,
            "longitude__gt": longitude - precision,
        },
        sightings=sightings,
        posts=posts,
    )

    return Q(**args)


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


def get_nearby_location(latitude: float, longitude: float) -> Location:
    """
    Return existing location that is within LOCATION_DISTANCE_THRESHOLD of (latitude, longitude),
    or return None
    :param latitude:
    :param longitude:
    :return:
    """
    query = generate_lat_lon_nearby_query(latitude, longitude, CLOSE_ENOUGH)
    locations = Location.objects.filter(query)
    nl = find_closest_location(locations, latitude, longitude)
    return nl


def get_or_create_location(
    location_id: str = None,
    latitude: float = None,
    longitude: float = None,
    city: str = None,
    country: str = None,
    state: str = None
) -> Optional[Location]:
    """
    Verify the new Location can be added given existing Locations. If the new location is
    within a certain distance threshold of an existing location, return the nearest location.
    Otherwise, return new Location.
    :return:
    """

    if location_id:
        location = Location.objects.filter(pk=from_base64(location_id)[1]).first()
    else:
        location = get_nearby_location(latitude, longitude)

    if location is None and latitude and longitude:
        state_name = map_state_abr_to_name(state.upper()) if state else None
        location = Location(
            latitude=latitude,
            longitude=longitude,
            city=city,
            country=country,
            state=state.upper() if state else None,
            state_name=state_name
        )
        location.save()

    return location


def locations_distance_within_q(
    locations: QuerySet, latitude: float, longitude: float, arc_length: float
):
    precision = distance_to_degrees(arc_length)
    locations = locations.filter(
        generate_lat_lon_nearby_query(
            latitude=latitude,
            longitude=longitude,
            precision=precision,
        )
    )
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
    precision = distance_to_degrees(arc_length)
    locations = locations.filter(
        generate_lat_lon_nearby_query(
            latitude=latitude,
            longitude=longitude,
            precision=precision,
        )
    )
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
    precision = distance_to_degrees(arc_length)
    sightings = sightings.filter(
        generate_lat_lon_nearby_query(
            latitude=latitude,
            longitude=longitude,
            precision=precision,
            sightings=True
        )
    )
    ids = []
    for sighting in sightings:
        dist = distance.distance(
            (sighting.location.latitude, sighting.location.longitude),
            (latitude, longitude)
        ).meters
        if dist <= arc_length:
            ids.append(sighting.location.id)

    return Q(location__id__in=ids)


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
    precision = distance_to_degrees(arc_length)
    sightings = sightings.filter(
        generate_lat_lon_nearby_query(
            latitude=latitude,
            longitude=longitude,
            precision=precision,
            sightings=True
        )
    )
    ids = []
    for sighting in sightings:
        dist = distance.distance(
            (sighting.location.latitude, sighting.location.longitude),
            (latitude, longitude)
        ).meters
        if dist > arc_length:
            ids.append(sighting.location.id)

    return Q(location__id__in=ids)


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


def posts_distance_within_q(
    posts: QuerySet, latitude: float, longitude: float, arc_length: float
):
    precision = distance_to_degrees(arc_length)
    posts = posts.filter(
        generate_lat_lon_nearby_query(
            latitude=latitude,
            longitude=longitude,
            precision=precision,
            posts=True
        )
    )
    ids = []
    for post in posts:
        dist = distance.distance(
            (post.sighting.location.latitude, post.sighting.location.longitude),
            (latitude, longitude)
        ).meters
        if dist <= arc_length:
            ids.append(post.sighting.location.id)

    return Q(sighting__location__id__in=ids)


def posts_distance_outside_q(
    posts: QuerySet, latitude: float, longitude: float, arc_length: float
):
    precision = distance_to_degrees(arc_length)
    posts = posts.filter(
        generate_lat_lon_nearby_query(
            latitude=latitude,
            longitude=longitude,
            precision=precision,
            posts=True
        )
    )
    ids = []
    for post in posts:
        dist = distance.distance(
            (post.sighting.location.latitude, post.sighting.location.longitude),
            (latitude, longitude)
        ).meters
        if dist > arc_length:
            ids.append(post.sighting.location.id)

    return Q(sighting__location__id__in=ids)


def generic_distance_outside_q(
    qs: QuerySet, latitude: float, longitude: float, arc_length: float
):
    if qs.model is Location:
        return locations_distance_outside_q(
            locations=qs, latitude=latitude, longitude=longitude, arc_length=arc_length
        )

    elif qs.model is Sighting:
        return sightings_distance_outside_q(
            sightings=qs, latitude=latitude, longitude=longitude, arc_length=arc_length
        )

    elif qs.model is Post:
        return posts_distance_outside_q(
            posts=qs, latitude=latitude, longitude=longitude, arc_length=arc_length
        )

    return Q()


def generic_distance_within_q(
    qs: QuerySet, latitude: float, longitude: float, arc_length: float
):
    if qs.model is Location:
        return locations_distance_within_q(
            locations=qs, latitude=latitude, longitude=longitude, arc_length=arc_length
        )

    elif qs.model is Sighting:
        return sightings_distance_within_q(
            sightings=qs, latitude=latitude, longitude=longitude, arc_length=arc_length
        )

    elif qs.model is Post:
        return posts_distance_within_q(
            posts=qs, latitude=latitude, longitude=longitude, arc_length=arc_length
        )

    return Q()
