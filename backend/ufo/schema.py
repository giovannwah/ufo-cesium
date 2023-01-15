import strawberry
from strawberry_django_plus.optimizer import DjangoOptimizerExtension
from sightings.gql.query import (
    LocationQuery,
    SightingQuery,
    PostQuery,
    ProfileQuery,
    UserQuery,
)
from sightings.gql.mutation import (
    LocationMutation,
    SightingMutation,
    ProfileMutation,
    PostMutation,
    UserMutation,
)


@strawberry.type
class RootQuery(
    LocationQuery,
    SightingQuery,
    PostQuery,
    ProfileQuery,
    UserQuery,
):
    """
    Root GQL query, inherits from all other queries
    """
    pass


@strawberry.type
class RootMutation(
    LocationMutation,
    SightingMutation,
    PostMutation,
    ProfileMutation,
    UserMutation,
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
