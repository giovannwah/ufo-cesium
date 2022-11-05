from typing import Optional, Iterable
from strawberry_django_plus import gql
from sightings.models import Post
from sightings.helpers.common import sort_qs
from sightings.gql.types.post import PostNode
from sightings.gql.types.post import PostFilterInput
from sightings.gql.types.sorting import SortInput
from sightings.filters.posts import get_post_filters
from sightings.filters.resolvers.and_resolver import AndResolver

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
        filters = get_post_filters(pfi=post_filter)
        resolver = AndResolver(filters=filters)
        resolver.validate_filters()
        posts = resolver.resolve(qs=Post.objects.all())

        if sort:
            posts = sort_qs(qs=posts, sort_input=sort)

        return posts
