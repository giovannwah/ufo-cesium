from typing import Optional
from strawberry_django_plus import gql
from sightings.gql.types.sighting import SightingNode


@gql.type
class Query:
    sighting: Optional[SightingNode] = gql.relay.node()
    sighting_connection: gql.relay.Connection[SightingNode] = gql.relay.connection()
