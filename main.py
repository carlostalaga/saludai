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
# from modules.seo import generate_seo_title # No longer needed
from modules.seo import generate_excerpt, assign_category # Keep other SEO functions
from modules.formatting import format_content_as_html # Import the updated formatting function
from modules.thumbnail import generate_thumbnail  # Temporarily disable if you want to skip images
from modules.wordpress import publish_to_wordpress, map_category_to_id

# Debug flag (turn to True when you want verbose output, False to silence)
DEBUG = True

# Ensure a URL is provided
if len(sys.argv) < 2:
    print("❌ Error: Please provide a URL to process.")
    sys.exit(1)

url_or_text = sys.argv[1]

# -----------------------------------------------------------------
# STEP 0: DEBUG/VERIFICATION BEFORE PROCEEDING
# -----------------------------------------------------------------
print(f"🔎 DEBUG: Received input => {url_or_text}")

# Decide if we have a URL or raw text
if url_or_text.startswith("http://") or url_or_text.startswith("https://"):
    original_text = extract_original_text(url_or_text)
else:
    original_text = url_or_text

if DEBUG:
    print("\n[DEBUG] Original text (first 500 chars):")
    print(original_text[:500])
    print("... [truncated] ...\n")

# -----------------------------------------------------------------
# STEP 1: TRANSLATE
# -----------------------------------------------------------------
# Pass the original_text directly to the translation function
translated_text = extract_and_translate(original_text)

if DEBUG:
    print("[DEBUG STEP 1: TRANSLATE] Translated text (first 500 chars):")
    print(translated_text[:500])
    print("... [truncated] ...\n")

# -----------------------------------------------------------------
# STEP 2: MODERATE
# -----------------------------------------------------------------
safe_text = moderate_content(translated_text)

if DEBUG:
    print("[DEBUG STEP 2: MODERATE] Safe (moderated) text (first 500 chars):")
    print(safe_text[:500])
    print("... [truncated] ...\n")

# -----------------------------------------------------------------
# STEP 3: FACT-CHECK
# -----------------------------------------------------------------
final_checked_text = fact_check_translation(original_text, safe_text)

if DEBUG:
    print("[DEBUG STEP 3: FACT-CHECK] Fact-checked final text (first 500 chars):")
    print(final_checked_text[:500])
    print("... [truncated] ...\n")

# -----------------------------------------------------------------
# STEP 4: SEO (Excerpt and Category only)
# -----------------------------------------------------------------
# seo_title = generate_seo_title(final_checked_text) # Removed
excerpt = generate_excerpt(final_checked_text)
category_name = assign_category(final_checked_text)
category_id = map_category_to_id(category_name)

if DEBUG:
    print(f"[DEBUG STEP 4: SEO] Excerpt: {excerpt}")
    print(f"[DEBUG STEP 4: SEO] Category Name: {category_name}")
    print(f"[DEBUG STEP 4: SEO] Category ID: {category_id}\n")

# -----------------------------------------------------------------
# STEP 4.5: EXTRACT TITLE AND FORMAT CONTENT AS HTML
# -----------------------------------------------------------------
# format_content_as_html now returns the title and the formatted body separately
article_title, formatted_html_body = format_content_as_html(final_checked_text)

if DEBUG:
    print(f"[DEBUG STEP 4.5: EXTRACT TITLE] Extracted Article Title: {article_title}") # New debug output
    print("[DEBUG STEP 4.5: FORMAT CONTENT AS HTML] Formatted HTML Body (first 500 chars):") # Updated label
    print(formatted_html_body[:500])
    print("... [truncated] ...\n")

# -----------------------------------------------------------------
# STEP 5: PUBLISH
# -----------------------------------------------------------------
# Pass the extracted title and the formatted HTML body (without title) to WordPress
publish_to_wordpress(article_title, formatted_html_body, excerpt, category_id)

print(f"✅ Process completed successfully! Published with title: {article_title}") # Updated print statement
print(f"📌 Assigned Category: {category_name} (ID: {category_id})")
