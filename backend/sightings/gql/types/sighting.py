from strawberry import auto
from strawberry_django_plus import gql
from sightings.gql.types.location import LocationNode
from sightings.models import Sighting


@gql.django.type(Sighting)
class SightingNode(gql.relay.Node):
    """
    GQL type definition for Sighting Nodes
    """
    location: LocationNode
    sighting_datetime: auto
    created_datetime: auto
    modified_datetime: auto
