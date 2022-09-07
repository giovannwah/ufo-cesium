import strawberry

from sightings.gql.types.sighting import Sighting


@strawberry.type
class Post:
    user: str
    sighting: Sighting
    ufo_shape: str
    duration: str
    description: str
    created_datetime: str
    modified_datetime: str
