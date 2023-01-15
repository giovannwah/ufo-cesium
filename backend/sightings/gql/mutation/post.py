from strawberry_django_plus import gql
from strawberry.types import Info
from sightings.gql.types.post import PostType
from sightings.helpers.post import verify_and_create_post


@gql.type
class Mutation:

    def create_new_post(
        info: Info,
        user_id: str,

    ) -> PostType:
        # TODO: implement
        return verify_and_create_post(dict())
