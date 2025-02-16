# main.py

from modules.translation import extract_and_translate
from modules.moderation import moderate_content
from modules.fact_check import fact_check_translation
from modules.seo import generate_seo_title, generate_excerpt, assign_category
from modules.thumbnail import generate_thumbnail
from modules.wordpress import publish_to_wordpress, map_category_to_id  # Ensure correct import

import sys

# Ensure a URL is provided
if len(sys.argv) < 2:
    print("❌ Error: Please provide a URL to process.")
    sys.exit(1)

url = sys.argv[1]

# Step 1: Extract and translate
translated_text = extract_and_translate(url)

# Step 2: Moderate content to remove hallucinations
safe_text = moderate_content(translated_text)

# Step 3: Compare AI output with the original for factual accuracy
original_text = extract_and_translate(url)
final_checked_text = fact_check_translation(original_text, safe_text)  # ✅ Fixed unpacking issue

# Step 4: Generate SEO metadata
seo_title = generate_seo_title(final_checked_text)
excerpt = generate_excerpt(final_checked_text)
category_name = assign_category(final_checked_text)  # Get category name

# Convert category name to WordPress category ID
category_id = map_category_to_id(category_name)  # ✅ Fixed category assignment

# Step 5: Publish to WordPress with SEO details
publish_to_wordpress(seo_title, final_checked_text, excerpt, category_id)

print(f"✅ Process completed successfully! Published with SEO title: {seo_title}")
print(f"📌 Assigned Category: {category_name} (ID: {category_id})")
