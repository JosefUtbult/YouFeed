from django.contrib.auth.models import User
from django.db import models


class Channel(models.Model):
    handle = models.CharField(max_length=255, unique=True)
    youtube_id = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.handle} ({self.youtube_id or 'No ID'})"


class Video(models.Model):
    channel = models.ForeignKey("Channel", on_delete=models.CASCADE, related_name="videos")
    video_id = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"{self.video_id} ({self.channel.handle})"
