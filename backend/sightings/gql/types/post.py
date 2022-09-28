from strawberry import auto
from strawberry_django_plus import gql
from sightings.gql.types.sighting import SightingNode
from sightings.gql.types.user import UserNode
from sightings.models import Post


@gql.django.type(Post)
class PostNode(gql.relay.Node):
    """
    GQL type definition for a Post Node
    """
    user: UserNode
    sighting: SightingNode
    ufo_shape: auto
    duration: auto
    description: auto
    created_datetime: auto
    modified_datetime: auto
