from typing import List
from strawberry_django_plus import gql
from sightings.models import Profile
from sightings.gql.types.user import UserType
from sightings.gql.types.post import PostType


@gql.django.type(Profile)
class ProfileType(gql.relay.Node):
    """
    GQL type definition for user Profiles
    """
    user: UserType
    favorites: List[PostType]
