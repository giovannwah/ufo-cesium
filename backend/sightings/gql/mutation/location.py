from strawberry_django_plus import gql
from sightings.gql.types.location import (
    LocationNode,
    LocationCreateInput,
)


@gql.type
class Mutation:

    @gql.mutation
    def create_location(self) -> LocationNode:
        pass
