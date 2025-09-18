import os

import requests
import dotenv
from flask import Flask, jsonify, render_template, request
import nest_asyncio
nest_asyncio.apply()

import asyncio
import aiohttp

dotenv.load_dotenv()
API_KEY = os.getenv("API_KEY")

async def fetch_channel_id(session: aiohttp.ClientSession, handle: str):
    url = f"https://www.googleapis.com/youtube/v3/channels?part=id&forHandle={handle}&key={API_KEY}"
    async with session.get(url) as resp:
        data = await resp.json()
        if "items" in data and len(data["items"]) > 0:
            return data["items"][0]["id"], None
        return None, f'Invalid channel handle "{handle}"'


async def populate_channel_ids(channels: list):
    errors = []

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_channel_id(session, ch["handle"]) for ch in channels]
        results = await asyncio.gather(*tasks)

        for ch, (channel_id, error) in zip(channels, results):
            if channel_id:
                ch["id"] = channel_id
            if error:
                errors.append(error)

    return errors


async def fetch_latest_videos(session: aiohttp.ClientSession, channel_id: str):
    url = (
        f"https://www.googleapis.com/youtube/v3/search?"
        f"part=snippet&channelId={channel_id}&order=date&maxResults=10&key={API_KEY}"
    )
    async with session.get(url) as resp:
        data = await resp.json()

        if "items" not in data:
            return [], f"Failed to fetch videos for channel {channel_id}"

        videos = [
            {
                "title": item["snippet"]["title"],
                "video_id": item["id"]["videoId"],
                "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                "published_at": item["snippet"]["publishedAt"],
                "thumbnail": item["snippet"]["thumbnails"].get("high", {}).get("url")
                           or item["snippet"]["thumbnails"].get("medium", {}).get("url")
                           or item["snippet"]["thumbnails"].get("default", {}).get("url"),
            }
            for item in data["items"]
            if item["id"]["kind"] == "youtube#video"
        ]
        return videos, None


async def populate_latest_videos(channels: list):
    errors = []

    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_latest_videos(session, ch["id"]) if ch.get("id") else ([], f'Missing id for "{ch["handle"]}"')
            for ch in channels
        ]

        results = await asyncio.gather(*tasks)

        for ch, (videos, error) in zip(channels, results):
            if videos:
                ch["videos"] = videos
            if error:
                errors.append(error)

    return errors

