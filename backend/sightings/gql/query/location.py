from typing import Optional, Iterable
from strawberry_django_plus import gql
from sightings.gql.types.location import LocationType
from sightings.helpers.locations import (
    locations_filter_sort,
)
from sightings.gql.types.sorting import SortInput


@gql.type
class Query:
    location: Optional[LocationType] = gql.relay.node(
        description="A node representing a geographic location",
    )

    @gql.relay.connection(
        description="A collection of nodes representing geographic locations",
    )
    def location_connection(
            self,
            city_exact: Optional[str] = None,
            state_exact: Optional[str] = None,
            state_name_exact: Optional[str] = None,
            country_exact: Optional[str] = None,
            q: Optional[str] = None,
            sort: Optional[SortInput] = None
    ) -> Iterable[LocationType]:
        """
        Filterable location connection
        """
        return locations_filter_sort(
            city_exact=city_exact,
            state_exact=state_exact,
            state_name_exact=state_name_exact,
            country_exact=country_exact,
            q=q,
            sort=sort
        )
