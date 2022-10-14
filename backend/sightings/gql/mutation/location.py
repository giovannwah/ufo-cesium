from typing import Optional
from strawberry_django_plus import gql
from strawberry.types import Info
from sightings.gql.types.location import (
    LocationType,
)
from sightings.helpers.locations import create_location
from sightings.exceptions import LocationInputValidationException


@gql.type
class Mutation:
    @gql.relay.input_mutation(
        description="Create a new Location object"
    )
    def create_new_location(
        info: Info,
        longitude: float,
        latitude: float,
        country: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None
    ) -> LocationType:
        """
        Create a new Location object
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
            msg = f'Could not validate coordinates ({latitude}, {longitude})'
            raise LocationInputValidationException(msg)
