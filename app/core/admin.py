from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, NotificationSent


@admin.register(NotificationSent)
class NotificationSentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course_name', 'course_institution', 'sent_at')
    search_fields = ('user__email', 'course_name', 'course_institution')
    list_filter = ('sent_at',)
    readonly_fields = ('sent_at',)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    ordering = ('email',)
    list_display = ('email', 'first_name', 'is_staff', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informações pessoais', {'fields': ('first_name', 'last_name')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas importantes', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
