from strawberry import auto
from strawberry_django_plus import gql
from django.contrib.auth.models import User


@gql.django.type(User)
class UserType(gql.relay.Node):
    """
    GQL type definition for User Nodes
    """
    username: auto
    email: auto
    first_name: auto
    last_name: auto
