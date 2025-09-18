import asyncio
import json
from datetime import datetime

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render
from django.db.models import Q
from django.contrib import messages

from account.models import UserChannelConfig, ChannelGroup, Channel, Video
from .youtube_requests import populate_channel_ids, populate_latest_videos
from .dummy_latest_videos import DUMMY_LATEST_VIDEOS

# USE_DUMMY = False
USE_DUMMY = True

# Filter all channels relevant to a user that doesn't have a youtube channel ID. Request IDs with youtubes API,
# and store the results to the database
def update_channel_id(user_config):
    none_id_query = Q(youtube_id__isnull=True) | Q(youtube_id="")
    channels = Channel.objects.filter(groups__userconfig=user_config).filter(none_id_query).distinct()

    channel_handles = [{'handle': channel.handle, 'id': None} for channel in channels]
    errors = asyncio.run(populate_channel_ids(channel_handles))

    for channel_handle in channel_handles:
        non_id_channel_handle_query = Q(handle=channel_handle['handle']) & (Q(youtube_id__isnull=True) | Q(youtube_id=""))
        channels = Channel.objects.filter(groups__userconfig=user_config).filter(non_id_channel_handle_query).distinct()
        for channel in channels:
            channel.youtube_id=channel_handle['id']
            channel.save()

    return errors


def get_latest_videos(user_config):
    none_id_query = Q(youtube_id__isnull=True) | Q(youtube_id="")
    channels = Channel.objects.filter(groups__userconfig=user_config).exclude(none_id_query).distinct()

    channel_handles = [{'handle': channel.handle, 'id': channel.youtube_id, 'videos': []} for channel in channels]
    errors = asyncio.run(populate_latest_videos(channel_handles))

    return (channel_handles, errors)


def filter_viewed_videos(user_config, channel_handles):
    # First, remove all videos that have already been viewed from the result
    for instance in channel_handles:
        if not instance['videos']:
            continue

        for video in instance['videos']:
            # Check if a videos ID matches any viewed
            filtered = user_config.viewed_videos.filter(video_id=video['video_id']).first()
            if filtered:
                # Remove the instance from the result
                instance['videos'].remove(video)

    # Clear old videos from the database by filtering out all video IDs that isn't in the channel_handles list
    all_ids = [video['video_id'] for video in instance['videos'] for instance in channel_handles]
    user_config.viewed_videos.filter(video_id__in=all_ids).delete()


def build_result_structure(user_config, channel_handles):
    result = {}
    for instance in channel_handles:
        if not instance['videos']:
            print(f"Got non video {instance}")
            continue

        channel_groups = ChannelGroup.objects.filter(userconfig=user_config).filter(channels__youtube_id=instance['id'])
        for channel_group in channel_groups:
            # Make sure that the dict key for the category exists in result
            category_string = str(channel_group.category)
            category = result[category_string] if category_string in result.keys() else []
            result[category_string] = category
            print(f"Category: {category}")

            # Make sure that the group order exists in the category
            while len(category) <= int(channel_group.order):
                category.append([])

            group = category[int(channel_group.order)]

            for video in instance['videos']:
                group.append({
                    'handle': instance['handle'],
                    **video
                })

    return result


# Sort each category/group from latest to earliest. Flatten the result into a single list
def sort_result_structure(result):
    for category_key in result:
        res = []
        for group in result[category_key]:
            group.sort(
                key=lambda video: datetime.strptime(video["published_at"], "%Y-%m-%dT%H:%M:%SZ"),
                reverse=True
            )

            res += group

        result[category_key] = res


@login_required
@require_POST
def update(request):
    try:
        user_config = UserChannelConfig.objects.get(user=request.user)
    except UserChannelConfig.DoesNotExist:
        return JsonResponse({"error": "UserChannelConfig does not exist"}, status=404)

    errors = []

    # Make sure that all channel ID's are updated
    id_errors = update_channel_id(user_config)
    errors += id_errors

    # Retrieve the latest videos
    if USE_DUMMY:
        channel_handles = DUMMY_LATEST_VIDEOS
    else:
        channel_handles, latest_video_errors = get_latest_videos(user_config)
        errors += latest_video_errors

    # Filter out all viewed videos
    filter_viewed_videos(user_config, channel_handles)

    # Build a structure, sort and flatten it
    result = build_result_structure(user_config, channel_handles)
    sort_result_structure(result)

    return JsonResponse({'result': result, 'errors': errors})


@login_required
@require_POST
def register_viewed(request):
    try:
        user_config = UserChannelConfig.objects.get(user=request.user)
    except UserChannelConfig.DoesNotExist:
        return JsonResponse({"error": "UserChannelConfig does not exist"}, status=404)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    video_id = data.get("video_id")
    handle = data.get("handle")

    if not video_id:
        return JsonResponse({"error": "Missing video_id"}, status=400)
    elif not handle:
        return JsonResponse({"error": "Missing handle"}, status=400)

    channel, _ = Channel.objects.get_or_create(handle=handle)
    video, _ = Video.objects.get_or_create(video_id=video_id, defaults={"channel": channel})
    user_config.viewed_videos.add(video)
    user_config.save()

    return JsonResponse({"status": "ok"})


@login_required
def index(request):
    # messages.success(request, "Hello there");
    # messages.warning(request, "Hello there");
    # messages.error(request, "Hello there");

    return render(request, "index.html")
