from django.contrib import admin
from .models import Category, ChannelGroup, UserChannelConfig
from index.models import Channel


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "get_user")
    search_fields = ("name", "userconfig__user__username")

    def get_user(self, obj):
        return obj.userconfig.user.username
    get_user.short_description = "User"


class ChannelInline(admin.TabularInline):
    model = ChannelGroup.channels.through
    extra = 1


@admin.register(ChannelGroup)
class ChannelGroupAdmin(admin.ModelAdmin):
    inlines = [ChannelInline]
    list_display = ("get_category_name", "get_user", "order")
    list_filter = ("category",)
    search_fields = ("category__name", "userconfig__user__username")
    filter_horizontal = ("channels",)

    def get_category_name(self, obj):
        return obj.category.name
    get_category_name.short_description = "Category"

    def get_user(self, obj):
        return obj.userconfig.user.username
    get_user.short_description = "User"


@admin.register(UserChannelConfig)
class UserChannelConfigAdmin(admin.ModelAdmin):
    list_display = ("get_user", "display_categories")
    search_fields = ("user__username", "owned_categories__name")
    filter_horizontal = ("categories", "viewed_videos")
    ordering = ("user__username",)

    def get_user(self, obj):
        return obj.user.username
    get_user.short_description = "User"

    def display_categories(self, obj):
        return ", ".join([c.name for c in obj.owned_categories.all()])
    display_categories.short_description = "Owned Categories"

