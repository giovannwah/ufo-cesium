from strawberry import auto
from strawberry_django_plus import gql
from sightings.gql.types.sighting import SightingType
from sightings.gql.types.user import UserType
from sightings.models import Post


@gql.django.type(Post)
class PostType(gql.relay.Node):
    """
    GQL type definition for a Post Node
    """
    user: UserType
    sighting: SightingType
    ufo_shape: auto
    duration: auto
    description: auto
    created_datetime: auto
    modified_datetime: auto
