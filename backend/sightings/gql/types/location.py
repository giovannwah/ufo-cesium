from typing import Optional
from strawberry import auto
from strawberry_django_plus import gql
from sightings.models import Location


@gql.django.type(Location)
class LocationType:
    """
    Location Output type for "create" mutation
    """
    id: str
    longitude: float
    latitude: float
    country: Optional[str]
    city: Optional[str]
    state: Optional[str]
    state_name: Optional[str]


@gql.django.type(Location)
class LocationNode(gql.relay.Node):
    """
    GQL type definition for Location Nodes
    """
    longitude: auto
    latitude: auto
    country: auto
    city: auto
    state: auto
    state_name: auto


