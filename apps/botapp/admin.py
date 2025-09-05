from apps.botapp.models import BotUser
from django.contrib import admin

@admin.register(BotUser)
class BotUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'first_name', 'last_name', 'created_at')
    search_fields = ('username', 'first_name', 'last_name')
    list_filter = ('created_at',)
