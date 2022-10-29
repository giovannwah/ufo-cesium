from typing import Iterable
from django.db.models import Model, Q
from django.db.models.query import QuerySet
from sightings.filters.base import BaseFilterResolver, BaseFilter


class OrResolver(BaseFilterResolver):
    """
    Combine filters by ORing their results and return the resulting queryset.
    """
    def resolve(self, filters: Iterable[BaseFilter] = None, model: Model = None) -> QuerySet:
        qs = model.objects.all()
        query = Q()
        for f in filters:
            query |= f.get_query()

        return qs.filter(query)

    def validate_filters(self, filters: Iterable[BaseFilter] = None, model: Model = None) -> bool:
        return True
