import strawberry

from sightings.gql.query.location import Query as LocationQuery
from sightings.gql.query.sighting import Query as SightingQuery
from sightings.gql.query.post import Query as PostQuery
from sightings.gql.query.profile import Query as ProfileQuery


@strawberry.type
class RootQuery(LocationQuery, SightingQuery, PostQuery, ProfileQuery):
    """
    Root GQL query, inherits from all other queries
    """
    pass


schema = strawberry.Schema(query=RootQuery)
