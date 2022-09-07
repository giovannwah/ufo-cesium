from sightings.models import Location as LocationModel
from sightings.gql.types.location import Location as LocationType


def get_location(location_id: str) -> LocationType:
    """
    Get an individual location
    :param location_id:
    :return:
    """
    return LocationType(
        longitude='1.23',
        latitude='2.34',
        country='Egypt',
        city='Cairo',
        state='Texas'
    )
