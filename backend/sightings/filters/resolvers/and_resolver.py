from typing import Iterable
from django.db.models import Model
from django.db.models.query import QuerySet
from sightings.filters.base import BaseFilterResolver, BaseFilter


class AndResolver(BaseFilterResolver):
    """
    Combine filters by ANDing their results and return the resulting queryset.
    """
    def resolve(self, filters: Iterable[BaseFilter], model: Model) -> QuerySet:
        qs = model.objects.all()
        for f in filters:
            qs = f.filter_qs(query_set=qs)

        return qs
