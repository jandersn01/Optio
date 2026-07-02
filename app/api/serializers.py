from rest_framework import serializers
from search.models import SearchRequest, Course, Favorite

class SearchRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchRequest
        exclude = ['is_deleted', 'deleted_at'] # Campos internos de soft-delete não expostos
        read_only_fields = ('user',)

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'

class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = '__all__'
        read_only_fields = ('user',)