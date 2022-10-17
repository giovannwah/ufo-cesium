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


def update_filter_args(args: dict, sightings: bool = False, posts: bool = False):
    """
    Updates filter args for usage against Sightings and Posts models
    """
    if not sightings and not posts:
        return args

    if sightings:
        return {f"location__{k}": v for (k, v) in args.items()}
    else:
        return {f"sighting__location__{k}": v for (k, v) in args.items()}
