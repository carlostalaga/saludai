import requests
from requests.auth import HTTPBasicAuth
from langdetect import detect

WP_URL = "https://guiacirugiaestetica.com/wp-json/wp/v2/posts"
WP_USER = "dev"  # Your WordPress admin username
WP_APP_PASSWORD = "W6sb rzY1 s9rS SsCi NAj0 Y75l"

def publish_to_wordpress(title, content, excerpt, category_id):
    """Publishes content to WordPress with an SEO title, excerpt, and assigned category."""

    # Ensure content exists before running language detection
    if not content:
        print("❌ Error: No content received. Check the translation pipeline.")
        return

    # Debugging: Check the language before publishing
    detected_lang = detect(content)
    print(f"🔎 Checking content language before publishing: {detected_lang}")
    print(f"📝 Content Preview: {content[:200]}...")  # Print first 200 characters to check

    if detected_lang != "es":
        print("❌ Warning: The content is NOT in Spanish! Debug the translation process.")

    post_data = {
        "title": title,
        "content": content,
        "status": "publish",
        "excerpt": excerpt,
        "categories": [category_id]  # ✅ Uses correctly assigned category ID
    }

    response = requests.post(WP_URL, auth=HTTPBasicAuth(WP_USER, WP_APP_PASSWORD), json=post_data)

    if response.status_code == 201:
        print(f"✅ Successfully published! Post ID: {response.json()['id']}")
        print(f"📌 View Post: {response.json()['link']}")
    else:
        print(f"❌ Failed to publish: {response.json()}")

def map_category_to_id(category_name):
    """Maps category names to WordPress category IDs. If not found, returns a default category."""
    category_mapping = {
        "Medicina Estetica": 1,
        "Inteligencia Artificial": 1002,
        "Tecnologia Medica": 1003,
        "Fitness": 1001,
        "Biotecnologia": 999,
        "Economia": 1000,
        "Nanotecnologia": 840
    }
    return category_mapping.get(category_name, 1)  # ✅ Default to "Medicina Estetica" if not found

