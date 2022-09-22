from typing import Optional
from strawberry_django_plus import gql
from sightings.gql.types.sighting import SightingType


@gql.type
class Query:
    sighting: Optional[SightingType] = gql.relay.node()
    sighting_connection: gql.relay.Connection[SightingType] = gql.relay.connection()
