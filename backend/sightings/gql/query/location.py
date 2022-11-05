from typing import Optional, Iterable
from strawberry_django_plus import gql
from sightings.gql.types.location import (
    LocationNode,
    LocationFilterInput,
)
from sightings.helpers.common import sort_qs
from sightings.gql.types.sorting import SortInput
from sightings.models import Location
from sightings.filters.resolvers.and_resolver import AndResolver
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
        resolver = AndResolver(filters=filters)
        resolver.validate_filters()
        locations = resolver.resolve(qs=Location.objects.all())

        if sort:
            locations = sort_qs(qs=locations, sort_input=sort)

        return locations
