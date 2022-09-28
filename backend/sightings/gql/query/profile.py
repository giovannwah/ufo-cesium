from typing import Optional
from strawberry_django_plus import gql
from sightings.gql.types.profile import ProfileNode


@gql.type
class Query:
    profile: Optional[ProfileNode] = gql.relay.node()
    profile_connection: gql.relay.Connection[ProfileNode] = gql.relay.connection()
