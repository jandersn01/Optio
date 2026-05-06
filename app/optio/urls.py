"""
URL configuration for optio project.
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Autenticação (usando views built-in do Django)
    path('login/', auth_views.LoginView.as_view(), name='login'),

    # App Core (dashboard, pesquisas e logout)
    path("core/", include("core.urls")),
    path("search/", include("search.urls")),
]
