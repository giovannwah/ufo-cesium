from strawberry import auto
from strawberry_django_plus import gql
from django.contrib.auth.models import User


@gql.django.type(User)
class UserNode(gql.relay.Node):
    """
    GQL type definition for User Nodes
    """
    username: auto
    email: auto
    first_name: auto
    last_name: auto


@gql.input
class UserInput:
    username: str
    password: str
    email: str
    first_name: str
    last_name: str


@gql.django.type(User)
class UserType:
    id: str
    username: str
    email: str
    first_name: str
    last_name: str
