from typing import Optional
from strawberry_django_plus import gql
from sightings.gql.types.location import LocationType


@gql.type
class Query:
    location: Optional[LocationType] = gql.relay.node()
    location_connection: gql.relay.Connection[LocationType] = gql.relay.connection()
