from typing import List
from django.db import models
from django.db.models import Q, QuerySet


class BaseFilter:
    """
    Base filter class

    TODO: Update to allow for filter composition?
    """

    def validate(self) -> bool:
        """
        Return True if the filter instance is configured correctly, false otherwise.

        :return:
        """
        raise NotImplementedError

    def filter_qs(self, query_set: QuerySet, **kwargs) -> QuerySet:
        """
        Filter a query_set, returning a filtered version of the input query_set

        :param query_set:
        :return:
        """
        raise NotImplementedError

    def get_query(self, **kwargs) -> Q:
        """
        Return a Q object to use to filter a model's items

        :param kwargs:
        :return:
        """
        return Q()


class SimpleFilter(BaseFilter):
    """
    Simple filter implementation
    """
    def validate(self) -> bool:
        return True

    def filter_qs(self, query_set: QuerySet, **kwargs) -> QuerySet:
        if not query_set.exists():
            return query_set

        return query_set.filter(self.get_query(**kwargs))


class BaseFilterResolver:
    """
    Base filter resolver class
    """
    filters: List[BaseFilter]

    def resolve(self, filters: List[BaseFilter] = None, qs: QuerySet = None) -> QuerySet:
        """
        Resolve an array of filters to produce a query_set on a given model.
        For example:

        Given a list of Filter1, Filter2, Filter3, and Filter4 instances, you could resolve them like so:

        items = model.objects.all()
        query_set[model] =
        items.filter((Filter1.get_query() & Filter2.get_query()) | (Filter3.get_query() & Filter4.get_query()))

        :param filters: a list of BaseFilter instances
        :param model: the model.Model instance whose items you want to filter
        :return:
        """
        raise NotImplementedError

    def validate_filters(self, filters: List[BaseFilter] = None, model: models.Model = None) -> bool:
        """
        Validate all filters in a list of filters to ensure no issues occur while resolving them.

        :param filters:
        :param model:
        :return:
        """
        raise NotImplementedError

    def aggregate_filters(self, filters: List[BaseFilter] = None) -> List[BaseFilter]:
        """
        Transform filter values based on some rules.

        For instance, if two different filters in a list contain values in a "location_ids" field,
        it may be preferable to nullify or transform one or both of the lists instead of invalidating
        the entire list of filters.

        :param filters:
        :return:
        """
        return filters
