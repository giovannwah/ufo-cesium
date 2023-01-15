from typing import Optional
from strawberry_django_plus import gql
from sightings.gql.types.user import UserNode


@gql.type
class Query:
    user: Optional[UserNode] = gql.relay.node(description="Relay node representing a user")
    user_connection: gql.relay.Connection[UserNode] = gql.relay.connection()
