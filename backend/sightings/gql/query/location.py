from typing import Optional, Iterable
from strawberry_django_plus import gql
from sightings.gql.types.location import (
    LocationNode,
    DistanceFromInput,
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
        city_exact: Optional[str] = None,
        state_exact: Optional[str] = None,
        state_name_exact: Optional[str] = None,
        country_exact: Optional[str] = None,
        distance_from: Optional[DistanceFromInput] = None,
        q: Optional[str] = None,
        sort: Optional[SortInput] = None
    ) -> Iterable[LocationNode]:
        """
        Filterable location connection
        :param city_exact: city name, case-insensitive
        :param state_exact: state abbreviation, case-insensitive
        :param state_name_exact: exact state name, case-insensitive
        :param country_exact: exact country name, case-insensitive
        :param distance_from: input type specifying a range of locations within or outside of some radius around a central
        location
        :param q: query string, space separated
        :param sort: SortInput object
        """
        return locations_filter_sort(
            city_exact=city_exact,
            state_exact=state_exact,
            state_name_exact=state_name_exact,
            country_exact=country_exact,
            distance_from=distance_from,
            q=q,
            sort=sort
        )
