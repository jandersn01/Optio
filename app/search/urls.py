from django.urls import path

from . import views

app_name = "search"

urlpatterns = [
    path("request/", views.search_request_create, name="request_create"),
    path("list/", views.search_list, name="request_list"),
    path("<int:pk>/results/", views.search_results, name="search_results"),
    path("<int:pk>/delete/", views.search_delete, name="search_delete"),
    path("<int:pk>/repeat/", views.search_repeat, name="search_repeat"),
    path("favoritos/", views.favorites_list, name="favorites_list"),
    path("favorito/<int:pk>/adicionar/", views.favorite_add, name="favorite_add"),
    path("favorito/<int:pk>/remover/", views.favorite_remove, name="favorite_remove"),
    path("alertas/", views.alerts_list, name="alerts_list"),
    path("alerta/<int:pk>/toggle/", views.alert_toggle, name="alert_toggle"),
    path("alerta/<int:pk>/apagar/", views.alert_delete, name="alert_delete"),
]
