from typing import Optional, Iterable
from strawberry_django_plus import gql
from sightings.gql.types.sighting import SightingNode
from sightings.gql.types.sighting import SightingFilterInput
from sightings.gql.types.sorting import SortInput
from sightings.helpers.sighting import sightings_filter_sort
from sightings.filters.validate import validate_filters


@gql.type
class Query:
    sighting: Optional[SightingNode] = gql.relay.node(
        description="A node representing a single ufo sighting"
    )

    @gql.relay.connection(
        description="A collection of nodes representing ufo sightings"
    )
    def sighting_connection(
        self,
        sighting_filter: Optional[SightingFilterInput] = None,
        sort: Optional[SortInput] = None
    ) -> Iterable[SightingNode]:
        """
        Filterable sighting connection
        :param sighting_filter: SightingFilterInput object
        :param sort: SortInput object
        """
