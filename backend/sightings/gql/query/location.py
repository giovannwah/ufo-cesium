from typing import Optional, Iterable
from strawberry_django_plus import gql
from sightings.gql.types.location import (
    LocationNode,
    LocationFilterInput,
)
from sightings.helpers.locations import (
    locations_filter_sort,
)
from sightings.gql.types.sorting import SortInput


@gql.type
class Query:
    location: Optional[LocationNode] = gql.relay.node(
        description="A node representing a geographic location",
    )

    @gql.relay.connection(
        description="A collection of nodes representing geographic locations",
    )
    def location_connection(
        self,
        location_filter: Optional[LocationFilterInput] = None,
        sort: Optional[SortInput] = None
    ) -> Iterable[LocationNode]:
        """
        Filterable location connection
        :param location_filter: LocationFilterInput object
        :param sort: SortInput object
        """
        # validate location filter input
        if location_filter:
            location_filter.validate()

        return locations_filter_sort(
            location_filter=location_filter,
            sort=sort
        )
