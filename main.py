# main.py

from dotenv import load_dotenv
import os
import sys

# Load environment variables from .env file
load_dotenv()

# -- Imports for your pipeline steps --
from modules.translation import extract_and_translate, extract_original_text
from modules.moderation import moderate_content
from modules.fact_check import fact_check_translation
from modules.seo import generate_seo_title, generate_excerpt, assign_category
# from modules.thumbnail import generate_thumbnail  # Temporarily disable if you want to skip images
from modules.wordpress import publish_to_wordpress, map_category_to_id

# Debug flag (turn to True when you want verbose output, False to silence)
DEBUG = True

# Ensure a URL is provided
if len(sys.argv) < 2:
    print("❌ Error: Please provide a URL to process.")
    sys.exit(1)

url = sys.argv[1]

# -----------------------------------------------------------------
# STEP 0: DEBUG/VERIFICATION BEFORE PROCEEDING
# -----------------------------------------------------------------
print(f"🔎 DEBUG: Processing URL => {url}")

original_text = extract_original_text(url)

if DEBUG:
    print("\n[DEBUG] Original text (first 500 chars):")
    print(original_text[:500])
    print("... [truncated] ...\n")

# -----------------------------------------------------------------
# STEP 1: TRANSLATE
# -----------------------------------------------------------------
translated_text = extract_and_translate(url)

if DEBUG:
    print("[DEBUG] Translated text (first 500 chars):")
    print(translated_text[:500])
    print("... [truncated] ...\n")

# -----------------------------------------------------------------
# STEP 2: MODERATE
# -----------------------------------------------------------------
safe_text = moderate_content(translated_text)

if DEBUG:
    print("[DEBUG] Safe (moderated) text (first 500 chars):")
    print(safe_text[:500])
    print("... [truncated] ...\n")

# -----------------------------------------------------------------
# STEP 3: FACT-CHECK
# -----------------------------------------------------------------
final_checked_text = fact_check_translation(original_text, safe_text)

if DEBUG:
    print("[DEBUG] Fact-checked final text (first 500 chars):")
    print(final_checked_text[:500])
    print("... [truncated] ...\n")

# -----------------------------------------------------------------
# STEP 4: SEO
# -----------------------------------------------------------------
seo_title = generate_seo_title(final_checked_text)
excerpt = generate_excerpt(final_checked_text)
category_name = assign_category(final_checked_text)
category_id = map_category_to_id(category_name)

if DEBUG:
    print(f"[DEBUG] SEO Title: {seo_title}")
    print(f"[DEBUG] Excerpt: {excerpt}")
    print(f"[DEBUG] Category Name: {category_name}")
    print(f"[DEBUG] Category ID: {category_id}\n")

# -----------------------------------------------------------------
# STEP 5: PUBLISH
# -----------------------------------------------------------------
publish_to_wordpress(seo_title, final_checked_text, excerpt, category_id)

print(f"✅ Process completed successfully! Published with SEO title: {seo_title}")
print(f"📌 Assigned Category: {category_name} (ID: {category_id})")
