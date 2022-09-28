import strawberry
from strawberry_django_plus.optimizer import DjangoOptimizerExtension
# from sightings.gql.query.location import Query as LocationQuery
# from sightings.gql.query.sighting import Query as SightingQuery
# from sightings.gql.query.post import Query as PostQuery
# from sightings.gql.query.profile import Query as ProfileQuery
from sightings.gql.query import (
    LocationQuery,
    SightingQuery,
    PostQuery,
    ProfileQuery,
)
from sightings.gql.mutation import (
    LocationMutation,
    SightingMutation,
    PostMutation,
    ProfileMutation,
    UserMutation,
)


@strawberry.type
class RootQuery(
    LocationQuery, SightingQuery, PostQuery, ProfileQuery
):
    """
    Root GQL query, inherits from all other queries
    """
    pass


@strawberry.type
class RootMutation(
    LocationMutation, SightingMutation, PostMutation, ProfileMutation, UserMutation
):
    """
    Root GQL mutation, inherits from all other mutations
    """
    pass


schema = strawberry.Schema(
    query=RootQuery,
    mutation=RootMutation,
    extensions=[
        DjangoOptimizerExtension
    ]
)
