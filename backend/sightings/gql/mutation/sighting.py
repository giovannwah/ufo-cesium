from strawberry_django_plus import gql
from strawberry.types import Info
from sightings.gql.types.sighting import SightingType
from sightings.gql.types.location import LocationInput
from sightings.helpers.sighting import verify_and_create_sighting


@gql.type
class Mutation:
    @gql.relay.input_mutation(
        description="Create a new Sighting"
    )
    def create_new_sighting(
        info: Info,
        location: LocationInput,
        sighting_datetime: str,
    ) -> SightingType:
        sighting_args = {
            'location': location.__dict__,
            'sighting_datetime': sighting_datetime
        }
        return verify_and_create_sighting(sighting_args)
