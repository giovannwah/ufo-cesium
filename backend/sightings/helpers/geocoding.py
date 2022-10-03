from typing import Optional
from geopy.geocoders import (
    get_geocoder_for_service,
    GeocoderNotFound,
)
from sightings.exceptions import LocationValidationException


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
        services: list, query: str, city: str, country: str, state: str = None
) -> bool:
    """
    Evaluate whether a location query, "<latitude>, <longitude>", corresponds to an existing
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
            print(f'Config: {config}')
            print(f'Query: {query}')
            print(f'City: {city}')
            print(f'Country: {country}')
            print(f'State: {state}')

            geolocator = cls(**config)
            location = geolocator.reverse(query, language='en', zoom=10)

            address = location.raw['address']
            print(f'location raw: {location.raw}')
            print(f'location address: {address}')
            found_city = address['city'] if 'city' in address else address['town']

            if city.lower() == found_city.lower() and \
                    country.lower() == address['country'].lower():
                print('City matches')
                if state and state.lower() != address['state'] and STATE_MAP.get(state.upper()) != address['state']:
                    return False

                print('State matches')
                return True

        except GeocoderNotFound:
            print('Geocoder Not found...')
            continue

    return False


def validate_location_coordinates(
    latitude: float, longitude: float, city: str, country: str, state: str=None
) -> bool:
    """
    Verify that the latitude and longitude values provided correspond to accurately to the
    provided country/city/state values
    """
    query = f"{latitude}, {longitude}"

    if not validate_longitude_latitude(longitude=longitude, latitude=latitude):
        msg = f'Invalid latitude, longitude: ({query})'
        raise LocationValidationException(msg)

    # geocoder services to loop through in order to validate address
    geocoder_services = ['nominatim']

    return evaluate_query(
        services=geocoder_services, query=query, city=city, country=country, state=state,
    )
