import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render

from .models import UserChannelConfig, Category, ChannelGroup, Channel

def create_user_config_from_json(user: User, config_json: dict):
    user_config, _ = UserChannelConfig.objects.get_or_create(user=user)

    for category_name, groups in config_json["channels"].items():
        category, _ = Category.objects.get_or_create(
            userconfig=user_config,
            name=category_name
        )

        for group_index, group_channels in enumerate(groups):
            group = ChannelGroup.objects.create(
                userconfig=user_config,
                category=category,
                order=group_index
            )

            for channel_info in group_channels:
                if channel_info:
                    channel, _ = Channel.objects.get_or_create(handle=channel_info["handle"])

                    # If the ID of a channel already exists in the JSON config
                    if 'id' in channel_info.keys():
                        # If the channel ID isn't stored in the database, use the one from the JSON config
                        if not channel.id:
                            channel.id = channel_info["id"]
                            channel.save()
                        # If the ID already exists, but is a mismatch with the one in the JSON config.
                        # Just remove it so that it can be queried for later
                        elif channel.id != channel_info["id"]:
                            channel.id = None
                            channel.save()

                    group.channels.add(channel)


@login_required
def account(request):
    if request.method == "POST" and request.FILES.get("file"):
        uploaded_file = request.FILES["file"]
        try:
            data = json.load(uploaded_file)  # read JSON from uploaded file
            create_user_config_from_json(request.user, data)
            messages.success(request, "Config uploaded successfully!")
        except json.JSONDecodeError as e:
            messages.error(request, f"Invalid JSON: {e}")
    elif request.method == "POST":
        messages.error(request, "No file uploaded.")

    return render(request, "account.html")

