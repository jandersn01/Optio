from rest_framework import viewsets, permissions
from search.models import SearchRequest, Course, Favorite
from .serializers import SearchRequestSerializer, CourseSerializer, FavoriteSerializer

class SearchRequestViewSet(viewsets.ModelViewSet):
    serializer_class = SearchRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Usa o seu manager customizado 'for_user'
        return SearchRequest.objects.for_user(self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Filtra cursos pelo usuário dono da requisição de busca original
        return Course.objects.filter(search_request__user=self.request.user)

class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)