from typing import Optional
from strawberry_django_plus import gql
from sightings.gql.types.post import PostNode


@gql.type
class Query:
    post: Optional[PostNode] = gql.relay.node()
    post_connection: gql.relay.Connection[PostNode] = gql.relay.connection()
