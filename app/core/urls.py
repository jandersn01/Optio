from django.urls import path
from . import views
from django.views.generic import TemplateView

app_name = 'core'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('preferencias/', views.preferences, name='preferences'),
    path('apagar-historico/', views.delete_search_history, name='delete_search_history'),
    path('politica-de-privacidade', TemplateView.as_view(template_name='core/privacy.html'), name= 'privacy_policy'),
    path('metricas/', views.metrics_dashboard, name='metrics_dashboard')
]
