import sys
from youtube_updater import get_authenticated_service

def set_thumbnail(youtube, video_id, thumbnail_path):
    print(f"Uploading thumbnail for video {video_id}...")
    try:
        response = youtube.thumbnails().set(
            videoId=video_id,
            media_body=thumbnail_path
        ).execute()
        print(f"Thumbnail uploaded successfully for video ID: {video_id}")
    except Exception as e:
        print(f"Error uploading thumbnail: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python youtube_thumbnail_updater.py <video_id> <thumbnail_path>")
        sys.exit(1)
        
    v_id = sys.argv[1]
    thumb_path = sys.argv[2]
    
    yt = get_authenticated_service()
    set_thumbnail(yt, v_id, thumb_path)
