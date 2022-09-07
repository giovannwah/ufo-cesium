from django.contrib import admin
from django.urls import path
from strawberry.django.views import GraphQLView
from .schema import schema


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', GraphQLView.as_view(schema=schema))
]
