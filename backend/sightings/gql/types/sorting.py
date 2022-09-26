from strawberry_django_plus import gql
from enum import Enum


@gql.enum
class SortOrder(Enum):
    ASC = "ASC"
    DES = "DES"


@gql.input
class SortInput:
    order: SortOrder
    field: str
