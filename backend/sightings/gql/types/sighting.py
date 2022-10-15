from typing import Optional
from strawberry import auto
from strawberry_django_plus import gql
from sightings.models import Sighting
from sightings.gql.types.location import LocationNode, LocationFilterInput
from sightings.gql.types.datetime import DateTimeFilterInput
from sightings.exceptions import SightingInputValidationException


@gql.input
class SightingFilterInput:
    """
    GQL input type for filtering Sightings
    """
    location_filter: Optional[LocationFilterInput] = None
    sighting_datetime_filter: Optional[DateTimeFilterInput] = None
    created_datetime_filter: Optional[DateTimeFilterInput] = None
    location_ids: Optional[str] = None  # filter by a list of location global ids

    def validate(self) -> bool:
        """
        Return True if SightingFilterInput is valid, raise exception otherwise
        """
        if self.location_filter and self.location_ids:
            raise SightingInputValidationException("Cannot specify both locationFilter and locationIds")

        if self.datetime_filter:
            return self.datetime_filter.validate()

        return True


@gql.django.type(Sighting)
class SightingNode(gql.relay.Node):
    """
    GQL type definition for Sighting Nodes
    """
    location: LocationNode
    sighting_datetime: auto
    created_datetime: auto
    modified_datetime: auto
