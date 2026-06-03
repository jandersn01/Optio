from django.urls import path

from . import views

app_name = "search"

urlpatterns = [
    path("request/", views.search_request_create, name="request_create"),
    path("list/", views.search_list, name="request_list"),
    path("<int:pk>/results/", views.search_results, name="search_results"),
    path("<int:pk>/delete/", views.search_delete, name="search_delete"),
    path("<int:pk>/repeat/", views.search_repeat, name="search_repeat"),
]
