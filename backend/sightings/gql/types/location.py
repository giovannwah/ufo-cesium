from strawberry import auto
from strawberry_django_plus import gql
from sightings.models import Location


@gql.django.type(Location)
class LocationType:
    """
    Location Output type for "create" mutation
    """
    longitude: float
    latitude: float
    country: str
    city: str
    state: str
    state_name: str


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


