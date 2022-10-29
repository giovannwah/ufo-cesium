from typing import Optional
from strawberry import auto
from strawberry_django_plus import gql
from sightings.models import Location
#
#
# NORTHERN = 'northern'
# SOUTHERN = 'southern'
# EASTERN = 'eastern'
# WESTERN = 'western'
#
# HEMISPHERES = {
#     NORTHERN: {
#         "longitude": 0,
#         "latitude": 90,
#         "arc_length": 10001965.729,
#         "inside_circle": True,
#     },
#     SOUTHERN: {
#         "longitude": 0,
#         "latitude": 90,
#         "arc_length": 10001965.729,
#         "inside_circle": False,
#     },
#     EASTERN: {
#         "longitude": 90,
#         "latitude": 0,
#         "arc_length": 10018754.25,
#         "inside_circle": True,
#     },
#     WESTERN: {
#         "longitude": 90,
#         "latitude": 0,
#         "arc_length": 10018754.25,
#         "inside_circle": False,
#     },
# }


@gql.input
class DistanceFromInput:
    """
    Input object used to filter a list of locations in some way based on position relative to the circumference of a
    circle defined by a center of (latitude, longitude), and an arc drawn from that center.
    latitude - central location's latitude
    longitude - central location's longitude
    arc_length - distance, in meters, from the central location
    inside_circle - boolean, True if targeting locations inside the circle, False otherwise.
    """
    longitude: float
    latitude: float
    arc_length: float
    inside_circle: bool


@gql.input
class LocationFilterInput:
    """
    Input type for filtering locations
    """
    city_exact: Optional[str] = None
    state_exact: Optional[str] = None
    state_name_exact: Optional[str] = None
    country_exact: Optional[str] = None
    distance_from: Optional[DistanceFromInput] = None
    q: Optional[str] = None


@gql.django.type(Location)
class LocationType:
    """
    Location Output type for "create" mutation
    """
    id: str
    longitude: float
    latitude: float
    country: Optional[str]
    city: Optional[str]
    state: Optional[str]
    state_name: Optional[str]


@gql.django.type(Location)
class LocationNode(gql.relay.Node):
    """
    GQL type definition for Location Nodes
    """
    longitude: auto
    latitude: auto
    country: auto
    city: auto
    state: auto
    state_name: auto
