from strawberry import auto
from strawberry_django_plus import gql
from sightings.models import Location


@gql.django.type(Location)
class LocationType(gql.relay.Node):
    """
    GQL type definition for Location Nodes
    """
    longitude: auto
    latitude: auto
    country: auto
    city: auto
    state: auto
    state_name: auto
