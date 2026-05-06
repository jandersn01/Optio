from django.contrib import admin
from .models import SearchRequest


@admin.register(SearchRequest)
class SearchRequestAdmin(admin.ModelAdmin):
    list_display = ['query', 'user', 'status', 'results_count', 'created_at']
    list_filter = ['status', 'created_at', 'area', 'modality']
    search_fields = ['query', 'user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Informações da Pesquisa', {
            'fields': ('user', 'query', 'area', 'modality', 'state')
        }),
        ('Status', {
            'fields': ('status', 'results_count')
        }),
        ('Datas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
