from typing import Optional
from strawberry_django_plus import gql
from sightings.gql.types.profile import ProfileType


@gql.type
class Query:
    profile: Optional[ProfileType] = gql.relay.node()
    profile_connection: gql.relay.Connection[ProfileType] = gql.relay.connection()
