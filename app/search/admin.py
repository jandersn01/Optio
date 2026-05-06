from django.contrib import admin
from .models import SearchRequest

# Register your models here.
@admin.register(SearchRequest)
class SearchRequestAdmin(admin.ModelAdmin):
    list_display = ['keywords', 'user', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'area', 'modality']
    search_fields = ['keywords', 'user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Informações da Pesquisa', {
            'fields': ('user', 'keywords', 'area', 'modality', 'state')
        }),
        ('Status', {
            'fields': ('status', 'results_count')
        }),
        ('Datas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
