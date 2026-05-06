from django.urls import path

from . import views


app_name = "search"

urlpatterns = [
    path("request/", views.search_request_create, name="request_create"),
]