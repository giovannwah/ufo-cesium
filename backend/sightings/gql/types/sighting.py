from strawberry import auto
from strawberry_django_plus import gql
from sightings.gql.types.location import LocationType
from sightings.models import Sighting


@gql.django.type(Sighting)
class SightingType(gql.relay.Node):
    """
    GQL type definition for Sighting Nodes
    """
    location: LocationType
    sighting_datetime: auto
    created_datetime: auto
    modified_datetime: auto
