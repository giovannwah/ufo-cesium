from strawberry_django_plus import gql
from strawberry.types import Info
from sightings.gql.types.post import PostType
from sightings.gql.types.sighting import SightingInput
from sightings.helpers.post import verify_and_create_post


@gql.type
class Mutation:

    @gql.relay.input_mutation(
        description="Create a new Post"
    )
    def create_new_post(
        info: Info,
        user_id: str,
        sighting: SightingInput,
        ufo_shape: str,
        duration: str,
        description: str,
    ) -> PostType:
        post_args = {
            'user_id': user_id,
            'sighting': sighting.__dict__,
            'ufo_shape': ufo_shape,
            'duration': duration,
            'description': description
        }
        return verify_and_create_post(post_args)
