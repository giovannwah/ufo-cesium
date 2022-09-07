import strawberry

from sightings.gql.types.sighting import Sighting
from sightings.gql.resolvers.sighting import get_sighting


@strawberry.type
class Query:
    sighting: Sighting = strawberry.field(resolver=get_sighting)
