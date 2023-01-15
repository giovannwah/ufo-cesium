from django.contrib.auth.models import User
from strawberry_django_plus.relay import to_base64
from sightings.gql.types.user import UserType, UserNode
from sightings.models import Profile


def create_user(user_input: dict) -> User:
    user = User.objects.create_user(**user_input)
    user.save()
    profile = Profile(user=user)
    profile.save()

    return user


def create_user_type(user_input: dict) -> UserType:
    user = create_user(user_input)

    return UserType(
        id=to_base64(UserNode.__name__, user.pk),
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
    )
