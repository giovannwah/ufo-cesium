from typing import Optional, Iterable
from strawberry_django_plus import gql
from sightings.gql.types.location import (
    LocationNode,
    LocationFilterInput,
)
from sightings.helpers.common import get_order_by_field
from sightings.gql.types.sorting import SortInput
from sightings.models import Location
from sightings.filters.resolvers.and_resolver import AndResolver
from sightings.filters.validate import validate_filters
from sightings.filters.locations import get_location_filters


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
        filters = get_location_filters(linput=location_filter)
        validate_filters(filters)

        locations = AndResolver().resolve(filters=filters, model=Location)

        if sort:
            order = get_order_by_field(sort.order, sort.field)
            locations = locations.order_by(order)

        return locations
