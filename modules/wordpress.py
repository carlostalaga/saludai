import requests
from requests.auth import HTTPBasicAuth
from modules.thumbnail import generate_thumbnail

WP_URL = "https://guiacirugiaestetica.com/wp-json/wp/v2/posts"
MEDIA_URL = "https://guiacirugiaestetica.com/wp-json/wp/v2/media"
WP_USER = "dev"  # Your WordPress admin username
WP_APP_PASSWORD = "W6sb rzY1 s9rS SsCi NAj0 Y75l"

def upload_thumbnail(image_url):
    """Downloads the image and uploads it to WordPress as a media attachment."""
    if not image_url:
        print("❌ No image URL provided. Skipping thumbnail upload.")
        return None

    try:
        response = requests.get(image_url)
        if response.status_code != 200:
            print("❌ Failed to download the image from OpenAI.")
            return None

        image_data = response.content
        headers = {
            "Content-Disposition": "attachment; filename=thumbnail.jpg",
            "Authorization": f"Basic {WP_USER}:{WP_APP_PASSWORD}",
            "Content-Type": "image/jpeg"
        }

        media_response = requests.post(MEDIA_URL, auth=HTTPBasicAuth(WP_USER, WP_APP_PASSWORD), headers=headers, files={'file': ('thumbnail.jpg', image_data, 'image/jpeg')})

        if media_response.status_code == 201:
            media_id = media_response.json()["id"]
            print(f"✅ Thumbnail uploaded successfully! Media ID: {media_id}")
            return media_id
        else:
            print(f"❌ Failed to upload thumbnail: {media_response.json()}")
            return None

    except Exception as e:
        print(f"❌ Error in thumbnail upload: {e}")
        return None

def publish_to_wordpress(title, content, excerpt, category_id):
    """Publishes content to WordPress with an SEO title, excerpt, and assigned category."""

    # Generate a thumbnail and upload it
    image_url = generate_thumbnail()
    media_id = upload_thumbnail(image_url) if image_url else None

    post_data = {
        "title": title,
        "content": content,
        "status": "publish",
        "excerpt": excerpt,
        "categories": [category_id] if category_id else [],
        "featured_media": media_id  # ✅ Attach the uploaded image as the featured thumbnail
    }

    headers = {
        "Authorization": f"Basic {WP_USER}:{WP_APP_PASSWORD}",
        "Content-Type": "application/json"
    }

    response = requests.post(WP_URL, auth=HTTPBasicAuth(WP_USER, WP_APP_PASSWORD), headers=headers, json=post_data)

    if response.status_code == 201:
        print(f"✅ Successfully published! Post ID: {response.json()['id']}")
        print(f"📌 View Post: {response.json()['link']}")
    else:
        print(f"❌ Failed to publish: {response.json()}")
