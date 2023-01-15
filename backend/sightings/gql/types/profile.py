from typing import List
from strawberry_django_plus import gql
from sightings.models import Profile
from sightings.gql.types.user import UserNode, UserType
from sightings.gql.types.post import PostNode, PostType


@gql.django.type(Profile)
class ProfileNode(gql.relay.Node):
    """
    GQL type definition for user Profiles
    """
    user: UserNode
    favorites: List[PostNode]


@gql.django.type(Profile)
class ProfileType:
    id: str
    user: UserType
    favorites: List[PostType]
