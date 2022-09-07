import strawberry

from sightings.gql.types.location import Location


@strawberry.type
class Sighting:
    location: Location
    sighting_datetime: str
    created_datetime: str
    modified_datetime: str
