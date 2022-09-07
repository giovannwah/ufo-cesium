import strawberry

from sightings.gql.types.location import Location
from sightings.gql.resolvers.location import get_location


@strawberry.type
class Query:
    location: Location = strawberry.field(resolver=get_location)
