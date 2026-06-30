from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SearchRequestViewSet, CourseViewSet, FavoriteViewSet

router = DefaultRouter()
router.register(r'search-requests', SearchRequestViewSet, basename='searchrequest')
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'favorites', FavoriteViewSet, basename='favorite')

urlpatterns = [
    path('', include(router.urls)),
]