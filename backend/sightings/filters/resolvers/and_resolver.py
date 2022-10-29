from typing import Iterable
from django.db.models import Model
from django.db.models.query import QuerySet
from sightings.filters.base import BaseFilterResolver, BaseFilter
from sightings.filters.sightings import (
    SightingsLocationIdsFilter,
    SightingsLocationQueryStringFilter,
    SightingsLocationExactFilter
)
from sightings.exceptions import FilterValidationException


class AndResolver(BaseFilterResolver):
    """
    Combine filters by ANDing their results and return the resulting queryset.
    """
    def __init__(self, filters: Iterable[BaseFilter] = None):
        self.filters = filters

    def resolve(self, filters: Iterable[BaseFilter] = None, model: Model = None) -> QuerySet:
        resolve_filters = filters or self.filters
        qs = model.objects.all()

        if resolve_filters is None:
            return qs

        for f in resolve_filters:
            qs = f.filter_qs(query_set=qs)

        return qs

    def validate_filters(self, filters: Iterable[BaseFilter] = None, model: Model = None) -> bool:
        val_filters = filters or self.filters

        if val_filters is None:
            return True

        if (any(isinstance(fil, SightingsLocationQueryStringFilter) for fil in val_filters) or
            any(isinstance(fil, SightingsLocationExactFilter) for fil in val_filters)) and \
                any(isinstance(fil, SightingsLocationIdsFilter) for fil in val_filters):
            msg = 'Cannot specify both locationIds filter and locationFilter in sightingFilter'
            raise FilterValidationException(msg)

        return all([fil.validate() for fil in filters])
