from django.contrib import admin
from .models import Channel

@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ("handle", "youtube_id")
    search_fields = ("handle", "youtube_id")
