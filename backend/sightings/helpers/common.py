from typing import Callable
from django.db.models.query import Q
from sightings.gql.types.sorting import SortOrder


def get_order_by_field(order: SortOrder, field: str):
    dec = '-' if order == SortOrder.DES else ''
    return f'{dec}{field}'


def generate_search_query(q: str, callback: Callable):
    """
    Split up query string and turn each into a separate Q() object to be combined
    into a single "&" query.
    :param q: query string, space separated
    :return: django Q object
    """
    query_terms = list(map(callback, q.split(' ')))
    query = Q()
    for term in query_terms:
        query &= term

    return query
