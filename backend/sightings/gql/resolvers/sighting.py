from sightings.models import Sighting as SightingModel
from sightings.gql.types.sighting import Sighting as SightingType
from sightings.gql.types.location import Location


def get_sighting(sighting_id: str) -> SightingType:
    """
    Get an individual sighting based on id
    :param sighting_id:
    :return:
    """
    ex_location = Location(
        longitude='1.23',
        latitude='2.34',
        country='United States',
        city='Atlanta',
        state='Georgia'
    )
    return SightingType(
        location=ex_location,
        sighting_datetime='today',
        created_datetime='today',
        modified_datetime='today',
    )
