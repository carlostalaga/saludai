# wordpress.py

import requests
from requests.auth import HTTPBasicAuth
from modules.thumbnail import generate_thumbnail
from config import get_wordpress_credentials
import json
import os # Import os to help extract filename
from urllib.parse import urlparse # Import urlparse

# Retrieve WordPress credentials and URLs
credentials = get_wordpress_credentials()
WP_URL = credentials["wp_url"]
MEDIA_URL = credentials["media_url"]
WP_USER = credentials["wp_user"]
WP_APP_PASSWORD = credentials["wp_app_password"]

def upload_thumbnail(image_url):
    """
    Downloads the image from the given URL
    and uploads it to WordPress as a media attachment.
    Uses Content-Type from download response.
    Adds detailed logging for debugging.
    """
    if not image_url:
        print("❌ No image URL provided. Skipping thumbnail upload.")
        return None

    print(f"ℹ️ Attempting to download thumbnail from: {image_url}")

    try:
        # Download the image
        response = requests.get(image_url, stream=True)
        print(f"ℹ️ Download request status code: {response.status_code}")

        if response.status_code != 200:
            print(f"❌ Failed to download the image from URL. Status: {response.status_code}")
            try:
                print(f"❌ Download error details: {response.text}")
            except Exception as e:
                print(f"❌ Could not get error details from download response: {e}")
            return None

        response.raise_for_status()
        image_data = response.content
        print(f"✅ Image downloaded successfully ({len(image_data)} bytes).")

        # --- Get Content-Type and Filename --- 
        content_type = response.headers.get('Content-Type', 'image/png') # Default to png if header missing
        print(f"ℹ️ Detected Content-Type: {content_type}")

        # Try to get a filename from the URL or Content-Disposition header
        filename = "thumbnail.png" # Default filename
        if 'Content-Disposition' in response.headers:
            # Try parsing filename from Content-Disposition, e.g., attachment; filename="fname.ext"
            disposition = response.headers['Content-Disposition']
            parts = disposition.split(';')
            for part in parts:
                if 'filename=' in part:
                    filename = part.split('=')[1].strip('" ')
                    break
        else:
            # Fallback: try getting filename from URL path
            parsed_url = urlparse(image_url)
            path_filename = os.path.basename(parsed_url.path)
            if path_filename:
                filename = path_filename
        
        print(f"ℹ️ Using filename: {filename}")
        # --- End Get Content-Type and Filename ---

        headers = {
            "Content-Disposition": f"attachment; filename={filename}",
            # Content-Type is set within the 'files' tuple below
        }
        # Use the detected content_type and filename
        files = {'file': (filename, image_data, content_type)}

        print(f"ℹ️ Attempting to upload thumbnail to: {MEDIA_URL}")

        # Upload to WordPress
        media_response = requests.post(
            MEDIA_URL,
            auth=HTTPBasicAuth(WP_USER, WP_APP_PASSWORD),
            headers=headers, # Headers might still be useful for Content-Disposition
            files=files
        )

        print(f"ℹ️ Upload request status code: {media_response.status_code}")

        if media_response.status_code == 201:
            media_id = media_response.json()["id"]
            print(f"✅ Thumbnail uploaded successfully! Media ID: {media_id}")
            return media_id
        else:
            print(f"❌ Failed to upload thumbnail. Status: {media_response.status_code}")
            try:
                print(f"❌ Upload error details: {json.dumps(media_response.json(), indent=2)}")
            except json.JSONDecodeError:
                print(f"❌ Upload error details (non-JSON): {media_response.text}")
            except Exception as e:
                print(f"❌ Could not get error details from upload response: {e}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Network error during thumbnail processing: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error in thumbnail upload/download: {e}")
        return None

def publish_to_wordpress(title, content, excerpt, category_id):
    """
    Publishes content to WordPress with an SEO title, excerpt, 
    and assigned category. Also attempts to generate & upload a thumbnail.
    """
    # Generate a thumbnail and upload it
    image_url = generate_thumbnail()
    media_id = upload_thumbnail(image_url) if image_url else None

    post_data = {
        "title": title,
        "content": content,
        "status": "publish",
        "excerpt": excerpt,
        # "categories": [category_id] if category_id else [],
        "featured_media": media_id  # Attach the uploaded image as the featured thumbnail
    }

    headers = {
        "Authorization": f"Basic {WP_USER}:{WP_APP_PASSWORD}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        WP_URL,
        auth=HTTPBasicAuth(WP_USER, WP_APP_PASSWORD),
        headers=headers,
        json=post_data
    )

    if response.status_code == 201:
        json_resp = response.json()
        print(f"✅ Successfully published! Post ID: {json_resp['id']}")
        print(f"📌 View Post: {json_resp['link']}")
    else:
        print(f"❌ Failed to publish: {response.json()}")

def map_category_to_id(category_name):
    """
    Maps a category name (e.g. 'Tecnologia Medica') to an integer ID 
    recognized by WordPress. For now, returns a hard-coded '1'.
    """
    return 1  # Replace with actual logic later
