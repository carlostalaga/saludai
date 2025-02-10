# translation.py 

import requests
from bs4 import BeautifulSoup
import openai

openai.api_key = "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"

client = openai.OpenAI(api_key=openai.api_key)

def split_text(text, max_length=3000):
    """Splits text into chunks for better AI processing."""
    words = text.split()
    chunks = []
    chunk = []
    
    for word in words:
        chunk.append(word)
        if len(" ".join(chunk)) > max_length:
            chunks.append(" ".join(chunk))
            chunk = []

    if chunk:
        chunks.append(" ".join(chunk))
    
    return chunks

def extract_and_translate(url):
    """Extracts and translates an article detecting the body of the article in the page and avoiding other articles headlines or advertising."""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    paragraphs = soup.find_all("p")
    content = " ".join([p.get_text() for p in paragraphs])

    chunks = split_text(content)

    translated_chunks = []
    for chunk in chunks:
        ai_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": 
                    "You are a professional journalist specializing in medical technology. "
                    "The tone is like if you are the author of the article."
                    "Your audience consists of health industry professionals and experts. "
                    "Translate the article maintaining factual integrity. "
                    "Do NOT add any information that is not explicitly stated in the original text. "
                    "Do NOT fabricate sources, statistics, or claims. "
                    "Maintain the structure and paragraph separation of the original article."
                    "Use titles, headings, and bullet points where appropriate."
                    "Ensure the translation is accurate, professional, and informative."
                    "Cite sources where necessary."
                    "Credit authors and publications where applicable."
                    },
                {"role": "user", "content": chunk}
            ]
        )
        translated_chunks.append(ai_response.choices[0].message.content)

    return "\n\n".join(translated_chunks)  # Recombine chunks
