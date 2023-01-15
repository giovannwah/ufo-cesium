from typing import Iterable
from strawberry_django_plus import gql
from strawberry_django_plus.relay import from_base64, to_base64
from strawberry.types import Info
from sightings.gql.types.profile import ProfileType, ProfileNode
from sightings.models import Profile
from sightings.exceptions import ProfileInputValidationException


@gql.type
class Mutation:
    @gql.relay.input_mutation(
        description="Add posts to user's favorites"
    )
    def add_to_favorites(
        info: Info,
        profile_id: str,
        post_ids: Iterable[str]  # post ids
    ) -> ProfileType:
        profile = Profile.objects.filter(id=from_base64(profile_id)[1]).first()
        if profile:
            profile.favorites.add(*[from_base64(post_id)[1] for post_id in post_ids])

            return ProfileType(
                id=to_base64(ProfileNode.__name__, profile.pk),
                user=profile.user,
                favorites=profile.favorites,
            )

        raise ProfileInputValidationException(f"Cannot find profile with id {profile_id}")

    @gql.relay.input_mutation(
        description="Remove posts from user's favorites"
    )
    def remove_from_favorites(
        info: Info,
        profile_id: str,
        post_ids: Iterable[str]
    ) -> ProfileType:
        profile = Profile.objects.filter(id=from_base64(profile_id)[1]).first()
        if profile:
            profile.favorites.remove(*[from_base64(post_id)[1] for post_id in post_ids])

            return ProfileType(
                id=to_base64(ProfileNode.__name__, profile.pk),
                user=profile.user,
                favorites=profile.favorites,
            )

        raise ProfileInputValidationException(f"Cannot find profile with id {profile_id}")
