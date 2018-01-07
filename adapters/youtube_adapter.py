import os

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser

from constants import developer_key

youtube_api_service_name = "youtube"
youtube_api_version = "v3"

def get_first_href(query):
  global developer_key
  global youtube_api_service_name
  global youtube_api_version

  youtube = build(youtube_api_service_name, youtube_api_version, developerKey = developer_key)

  search_response = youtube.search().list( q = query, part = "id,snippet", maxResults = 5).execute()

  result = search_response.get("items", [])

  for search_result in result:
    if search_result["id"]["kind"] == "youtube#video":
      return 'https://youtu.be/' + search_result["id"]["videoId"]

def get_trailer(title):
    return get_first_href(title + ' trailer')
