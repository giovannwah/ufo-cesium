from sightings.gql.types.sorting import SortOrder


def get_order_by_field(order: SortOrder, field: str):
    dec = '-' if order == SortOrder.DES else ''
    return f'{dec}{field}'
