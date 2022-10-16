from typing import Optional
from strawberry import auto
from strawberry_django_plus import gql
from sightings.models import Sighting
from sightings.gql.types.location import LocationNode, LocationFilterInput
from sightings.gql.types.datetime import DateTimeFilterInput


@gql.input
class SightingFilterInput:
    """
    GQL input type for filtering Sightings
    """
    location_filter: Optional[LocationFilterInput] = None
    sighting_datetime_filter: Optional[DateTimeFilterInput] = None
    location_ids: Optional[str] = None  # filter by a list of location global ids


@gql.django.type(Sighting)
class SightingNode(gql.relay.Node):
    """
    GQL type definition for Sighting Nodes
    """
    location: LocationNode
    sighting_datetime: auto
    created_datetime: auto
    modified_datetime: auto
