from strawberry_django_plus import gql
from strawberry.types import Info
from sightings.gql.types.user import UserInput, UserType
from sightings.helpers.user import create_user_type


@gql.type
class Mutation:

    @gql.relay.input_mutation(
        description="Create a new user and user profile"
    )
    def create_new_user(info: Info, user: UserInput) -> UserType:
        return create_user_type(user_input=user.__dict__)
