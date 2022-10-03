from typing import Optional
from strawberry_django_plus import gql
from strawberry.types import Info
from sightings.gql.types.location import (
    LocationType,
)
from sightings.models import Location
from sightings.helpers.locations import create_location
from sightings.helpers.geocoding import validate_location_coordinates
from sightings.exceptions import LocationValidationException


@gql.type
class Mutation:
    @gql.relay.input_mutation
    def create_new_location(
            info: Info, longitude: float, latitude: float, country: str, city: str, state: Optional[str]
    ) -> LocationType:
        """

        :return:
        """
        location_type = create_location({
            "latitude": latitude,
            "longitude": longitude,
            "country": country,
            "state": state,
            "city": city,
        })

        if location_type is not None:
            return location_type
        else:
            msg = f'Could not validate that coordinates ({latitude}, {longitude}) match location {city}, {country}' \
                  f'{f" ({state})" if state else ""}.'
            raise LocationValidationException(msg)
