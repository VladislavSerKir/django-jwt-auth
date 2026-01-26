from django.contrib import admin
from .models import Note


class NoteAdmin(admin.ModelAdmin):
    """Admin for Note"""

    list_display = ('name', 'user', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at', 'user')
    search_fields = ('name', 'description', 'user__email', 'user__name')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'user')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.user = request.user
        super().save_model(request, obj, form, change)


admin.site.register(Note, NoteAdmin)
