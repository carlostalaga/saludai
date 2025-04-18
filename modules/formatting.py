# formatting.py

from config import get_openai_api_key
from openai import OpenAI
import re

# Create the OpenAI client instance with your API key
client = OpenAI(api_key=get_openai_api_key())

def format_content_as_html(text):
    """
    Takes plain text content, identifies the main title (likely the first significant heading),
    formats the rest of the content using appropriate HTML tags (e.g., <h2>, <p>, <ul>, <li>)
    for better readability on a webpage, excluding the main title from the body.
    Returns the extracted title and the formatted HTML body separately.
    """
    # First, try to extract a plausible title from the beginning of the text
    # This is a simple heuristic, assuming the title is the first line or heading.
    lines = text.strip().split('\n')
    potential_title = lines[0].strip() if lines else "Untitled Article" # Default title

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert web content formatter. Your task is to take the provided plain text article, "
                    "identify its main title (usually the first significant heading or line), and format the *rest* of the content "
                    "using appropriate HTML tags for optimal readability on a website. "
                    "Use headings (<h2>, <h3>, etc.) for sections *below* the main title. "
                    "Use paragraphs (<p>) for blocks of text. "
                    "Use unordered lists (<ul><li>...</li></ul>) or ordered lists (<ol><li>...</li></ol>) for bullet points or numbered items where appropriate. "
                    "Use bold (<strong>) or italics (<em>) for emphasis if needed, but use sparingly. "
                    f"The main title seems to be '{potential_title}'. Do NOT include this main title or an equivalent <h1> tag in your formatted output. "
                    "Focus only on formatting the body content that follows the title. "
                    "Ensure the output is valid HTML suitable for direct embedding into a webpage body. "
                    "Do not add any extra commentary, just return the formatted HTML body content."
                )
            },
            {
                "role": "user",
                "content": text
            }
        ],
    )

    formatted_body = response.choices[0].message.content.strip()

    # Attempt to extract a more definitive title if the initial guess was poor
    # or if the LLM included an H1 despite instructions.
    # We prioritize an H1 tag if found, otherwise stick to the initial guess.
    h1_match = re.search(r"<h1.*?>(.*?)</h1>", formatted_body, re.IGNORECASE | re.DOTALL)
    if h1_match:
        actual_title = h1_match.group(1).strip()
        # Remove the H1 tag from the body
        formatted_body = re.sub(r"<h1.*?>.*?</h1>", "", formatted_body, count=1, flags=re.IGNORECASE | re.DOTALL).strip()
    else:
        actual_title = potential_title # Use the initial guess if no H1 found/removed

    # Clean up potential leading/trailing whitespace artifacts
    formatted_body = formatted_body.strip()

    return actual_title, formatted_body
