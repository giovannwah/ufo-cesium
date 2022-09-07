import strawberry

from sightings.gql.query.sighting import Query as SightingQuery
from sightings.gql.query.location import Query as LocationQuery


@strawberry.type
class RootQuery(SightingQuery, LocationQuery):
    pass


schema = strawberry.Schema(query=RootQuery)
