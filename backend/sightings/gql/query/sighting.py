from typing import Optional, Iterable
from strawberry_django_plus import gql
from sightings.models import Sighting
from sightings.helpers.common import get_order_by_field
from sightings.gql.types.sighting import SightingNode
from sightings.gql.types.sighting import SightingFilterInput
from sightings.gql.types.sorting import SortInput
from sightings.filters.validate import (
    validate_filters,
    get_sighting_filters,
)
from sightings.filters.resolvers.and_resolver import AndResolver


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
        filters = get_sighting_filters(sfi=sighting_filter)
        validate_filters(filters)

        sightings = AndResolver().resolve(filters=filters, model=Sighting)

        if sort:
            order = get_order_by_field(sort.order, sort.field)
            sightings = sightings.order_by(order)

        return sightings
