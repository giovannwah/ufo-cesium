from typing import List
from strawberry_django_plus import gql
from sightings.models import Profile
from sightings.gql.types.user import UserNode
from sightings.gql.types.post import PostNode


@gql.django.type(Profile)
class ProfileNode(gql.relay.Node):
    """
    GQL type definition for user Profiles
    """
    user: UserNode
    favorites: List[PostNode]
