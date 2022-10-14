from typing import Iterable
from django.db import models
from django.db.models import Q


class BaseFilter:
    """
    Base filter class
    """

    def validate(self) -> bool:
        raise NotImplementedError

    def filter_qs(self, query_set: models.query.QuerySet) -> models.query.QuerySet:
        raise NotImplementedError

    def get_query(self, **kwargs) -> models.Q:
        return Q()


class BaseFilterResolver:
    """
    Base filter resolver class
    """

    def resolve(self, filters: Iterable[BaseFilter], model: models.Model) -> models.query.QuerySet:
        raise NotImplementedError
