from django.contrib import admin
from .models import Course, SearchRequest


@admin.register(SearchRequest)
class SearchRequestAdmin(admin.ModelAdmin):
    list_display = ['keywords', 'user', 'status', 'is_deleted', 'created_at']
    list_filter = ['status', 'is_deleted', 'created_at', 'area', 'modality']
    search_fields = ['keywords', 'user__email', 'user__first_name']
    readonly_fields = ['created_at', 'updated_at', 'deleted_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Informações da Pesquisa', {
            'fields': ('user', 'keywords', 'area', 'modality', 'state')
        }),
        ('Status', {
            'fields': ('status', 'results_count')
        }),
        ('Exclusão', {
            'fields': ('is_deleted', 'deleted_at'),
            'classes': ('collapse',),
        }),
        ('Datas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return SearchRequest.all_objects.all()


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'institution', 'modality', 'state', 'search_request']
    list_filter = ['modality', 'state']
    search_fields = ['name', 'institution']
    raw_id_fields = ['search_request']
