from typing import Optional, List
from strawberry import auto
from strawberry_django_plus import gql
from sightings.gql.types.sighting import (
    SightingFilterInput,
    SightingNode
)
from sightings.gql.types.datetime import DateTimeFilterInput
from sightings.gql.types.user import UserNode
from sightings.models import Post


@gql.input
class PostFilterInput:
    """
    Input type for filtering posts
    """
    ufo_shape: Optional[str] = None
    q: Optional[str] = None
    post_created_datetime: Optional[DateTimeFilterInput] = None
    sighting_filter: Optional[SightingFilterInput] = None
    sighting_ids: Optional[List[str]] = None
    user_ids: Optional[List[str]] = None
    post_ids: Optional[List[str]] = None
    location_ids: Optional[List[str]] = None


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

