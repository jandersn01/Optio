from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('preferencias/', views.preferences, name='preferences'),
    path('apagar-historico/', views.delete_search_history, name='delete_search_history'),
]
