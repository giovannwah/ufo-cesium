from typing import Optional, List
from datetime import datetime
from strawberry import auto
from strawberry_django_plus import gql
from sightings.models import Sighting
from sightings.gql.types.location import (
    LocationNode, LocationFilterInput, LocationInput,
)
from sightings.gql.types.datetime import DateTimeFilterInput


@gql.input
class SightingFilterInput:
    """
    GQL input type for filtering Sightings
    """
    sighting_datetime_filter: Optional[DateTimeFilterInput] = None
    location_filter: Optional[LocationFilterInput] = None
    location_ids: Optional[List[str]] = None  # filter by a list of location global ids
    sighting_ids: Optional[List[str]] = None  # filter by a list of sighting global ids


@gql.django.type(Sighting)
class SightingNode(gql.relay.Node):
    """
    GQL type definition for Sighting Nodes
    """
    location: LocationNode
    sighting_datetime: auto
    created_datetime: auto
    modified_datetime: auto


@gql.django.type(Sighting)
class SightingType:
    id: str
    location: LocationNode
    sighting_datetime: datetime
    created_datetime: datetime
    modified_datetime: datetime


@gql.input
class SightingInput:
    location: Optional[LocationInput] = None
    sighting_datetime: Optional[str] = None
    sighting_id: Optional[str] = None
