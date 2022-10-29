from typing import Optional, Iterable
from strawberry_django_plus import gql
from sightings.gql.types.post import PostNode
from sightings.gql.types.post import PostFilterInput
from sightings.gql.types.sorting import SortInput


@gql.type
class Query:
    post: Optional[PostNode] = gql.relay.node(
        description="A node representing a post referencing a ufo sighting"
    )

    @gql.relay.connection(
        description="A collection of nodes representing posts referencing ufo sightings"
    )
    def post_connection(
        self,
        post_filter: Optional[PostFilterInput] = None,
        sort: Optional[SortInput] = None,
    ) -> Iterable[PostNode]:
        pass
