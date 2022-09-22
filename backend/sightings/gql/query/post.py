from typing import Optional
from strawberry_django_plus import gql
from sightings.gql.types.post import PostType


@gql.type
class Query:
    post: Optional[PostType] = gql.relay.node()
    post_connection: gql.relay.Connection[PostType] = gql.relay.connection()
