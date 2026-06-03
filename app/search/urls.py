from django.urls import path

from . import views


app_name = "search"

urlpatterns = [
    path("request/", views.search_request_create, name="request_create"),
    path("list/", views.search_list, name='request_list'),
    path("<int:pk>/results/", views.search_results, name="search_results"),
    path("favoritos/", views.favorites_list, name="favorites_list"),
    path("favorito/<int:pk>/remover/", views.favorite_remove, name="favorite_remove"),
]