from strawberry import auto
from strawberry_django_plus import gql
from sightings.models import Location


@gql.django.input(Location)
class LocationCreateInput:
    """
    Location Input type for "create" mutation
    """
    longitude: auto
    latitude: auto
    country: auto
    city: auto
    state: auto


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


