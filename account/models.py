from django.contrib.auth.models import User
from django.db import models

from index.models import Channel, Video

class UserChannelConfig(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="channel_config")
    categories = models.ManyToManyField(
        "Category",
        related_name="configs_for_users",
        blank=True
    )
    viewed_videos = models.ManyToManyField(
        Video,
        related_name="viewed_by_users",
        blank=True
    )

    def __str__(self):
        return f"{self.user.username}'s Config"

    def delete(self, *args, **kwargs):
        # Delete related categories (cascade to channel groups)
        for category in self.categories.all():
            category.delete()
        super().delete(*args, **kwargs)


class Category(models.Model):
    name = models.CharField(max_length=255)
    userconfig = models.ForeignKey(
        UserChannelConfig,
        on_delete=models.CASCADE,
        related_name="owned_categories"
    )

    def __str__(self):
        return self.name


class ChannelGroup(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="groups")
    userconfig = models.ForeignKey(UserChannelConfig, on_delete=models.CASCADE, related_name="channel_groups")
    order = models.PositiveIntegerField()
    channels = models.ManyToManyField(Channel, related_name="groups")

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.category.name} - Group {self.order} ({self.userconfig.user.username})"

