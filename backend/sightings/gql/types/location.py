import strawberry


@strawberry.type
class Location:
    longitude: float
    latitude: float
    country: str
    city: str
    state: str
