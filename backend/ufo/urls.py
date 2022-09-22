from django.contrib import admin
from django.urls import path
from strawberry.django.views import AsyncGraphQLView
from .schema import schema


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', AsyncGraphQLView.as_view(schema=schema))
]
