"""
AI Music Studio - YouTube Data API v3 upload module.
Handles OAuth authentication and video uploading to YouTube.

IMPORTANT: No credentials are stored in source code. All secrets must be
provided via environment variables or GitHub Secrets.

Required environment variables:
  YOUTUBE_CLIENT_ID     - OAuth 2.0 Client ID from Google Cloud Console
  YOUTUBE_CLIENT_SECRET - OAuth 2.0 Client Secret from Google Cloud Console
  YOUTUBE_REFRESH_TOKEN - OAuth refresh token (obtained via initial auth flow)

Setup instructions are in YOUTUBE_SETUP.md.
"""

import os
import json
import argparse
import sys

try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaFileUpload
    HAS_GOOGLE_API = True
except ImportError:
    HAS_GOOGLE_API = False


SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"


def get_authenticated_service():
    """Build YouTube API client from OAuth credentials stored in env vars."""
    if not HAS_GOOGLE_API:
        raise RuntimeError(
            "google-auth and google-api-python-client are not installed. "
            "Install with: pip install google-auth google-auth-oauthlib "
            "google-auth-httplib2 google-api-python-client"
        )

    client_id = os.environ.get("YOUTUBE_CLIENT_ID")
    client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET")
    refresh_token = os.environ.get("YOUTUBE_REFRESH_TOKEN")

    if not all([client_id, client_secret, refresh_token]):
        raise RuntimeError(
            "Missing YouTube OAuth credentials. Set YOUTUBE_CLIENT_ID, "
            "YOUTUBE_CLIENT_SECRET, and YOUTUBE_REFRESH_TOKEN environment "
            "variables (or GitHub Secrets). See YOUTUBE_SETUP.md."
        )

    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=SCOPES,
    )

    return build(API_SERVICE_NAME, API_VERSION, credentials=creds)


def upload_video(youtube, file_path, title, description, tags,
                 category_id="22", privacy_status="private",
                 thumbnail_path=None):
    """
    Upload a video to YouTube.

    privacy_status: "private", "unlisted", or "public".
    Default is "private" - never public without explicit authorization.
    """
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": category_id,
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Upload progress: {int(status.progress() * 100)}%")

    print(f"Upload complete! Video ID: {response['id']}")
    print(f"Video URL: https://www.youtube.com/watch?v={response['id']}")
    print(f"Privacy: {privacy_status}")

    # Upload thumbnail if provided
    if thumbnail_path and os.path.exists(thumbnail_path):
        try:
            youtube.thumbnails().set(
                videoId=response["id"],
                media_body=MediaFileUpload(thumbnail_path),
            ).execute()
            print("Thumbnail uploaded.")
        except HttpError as e:
            print(f"Thumbnail upload failed: {e}")

    return response["id"]


def add_to_playlist(youtube, video_id, playlist_title="Quiet Frequencies"):
    """Add video to a playlist. Creates the playlist if it doesn't exist."""
    try:
        # Try to find existing playlist
        request = youtube.playlists().list(part="snippet", mine=True, maxResults=50)
        response = request.execute()

        playlist_id = None
        for item in response.get("items", []):
            if item["snippet"]["title"] == playlist_title:
                playlist_id = item["id"]
                break

        if not playlist_id:
            # Create the playlist
            create_request = youtube.playlists().insert(
                part="snippet,status",
                body={
                    "snippet": {"title": playlist_title},
                    "status": {"privacyStatus": "private"},
                },
            )
            create_response = create_request.execute()
            playlist_id = create_response["id"]
            print(f"Created playlist: {playlist_title}")

        # Add video to playlist
        youtube.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": video_id,
                    },
                },
            },
        ).execute()
        print(f"Added video to playlist: {playlist_title}")
    except HttpError as e:
        print(f"Playlist operation failed: {e}")


def main():
    p = argparse.ArgumentParser(description="Upload a video to YouTube")
    p.add_argument("--file", required=True, help="Path to MP4 video file")
    p.add_argument("--title", required=True, help="Video title")
    p.add_argument("--description", required=True, help="Video description")
    p.add_argument("--tags", default="ambient, focus music, relaxing music",
                   help="Comma-separated tags")
    p.add_argument("--thumbnail", default=None, help="Path to thumbnail JPG")
    p.add_argument("--privacy", default="private",
                   choices=["private", "unlisted", "public"],
                   help="Privacy status (default: private)")
    p.add_argument("--playlist", default="Quiet Frequencies",
                   help="Playlist name to add video to")
    args = p.parse_args()

    tags_list = [t.strip() for t in args.tags.split(",") if t.strip()]

    try:
        youtube = get_authenticated_service()
        video_id = upload_video(
            youtube=youtube,
            file_path=args.file,
            title=args.title,
            description=args.description,
            tags=tags_list,
            privacy_status=args.privacy,
            thumbnail_path=args.thumbnail,
        )
        add_to_playlist(youtube, video_id, args.playlist)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
