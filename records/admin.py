from django.contrib import admin

from records.models import Record

@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'type', 'cat', 'amt', 'date', 'del_flag', 'created_at']
    list_filter = ['type', 'cat', 'del_flag', 'date']
    search_fields = ['user__email', 'user__username', 'cat', 'desc']
    ordering = ['-date', '-created_at']
