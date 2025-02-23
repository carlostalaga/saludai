# thumbnail.py

import requests
from config import get_openai_api_key
from openai import OpenAI

# Create the OpenAI client instance with your API key
client = OpenAI(api_key=get_openai_api_key())

IMAGE_PROMPT = (
    "A soft, pastel-colored abstract painting with smooth gradients and gentle brushstrokes. "
    "The composition features a harmonious blend of pastel pinks, blues, yellows, and greens, evoking a dreamy and calming atmosphere. "
    "Subtle organic patterns emerge, delicately hinting at biological structures such as DNA strands dissolving into fluid forms, "
    "synaptic connections weaving through the composition, or neuron-like branches subtly blending into the background. "
    "Each image integrates one or two elements—like the gentle curves of nerve pathways or the faint presence of cellular textures—"
    "ensuring an abstract and artistic representation rather than a literal depiction. "
    "The texture appears slightly grainy, resembling watercolor on paper, with an organic and flowing aesthetic that bridges science and art in a harmonious way."
)

def generate_thumbnail():
    """
    Generates an abstract science-inspired thumbnail
    using an OpenAI image generation endpoint.
    """
    try:
        response = client.images.generate(
            model="dall-e-3",  # Ensure your account has access to DALL-E 3
            prompt=IMAGE_PROMPT,
            size="1792x1024"
        )

        image_url = response.data[0].url
        return image_url  # ✅ Returns the generated image URL

    except Exception as e:
        print(f"❌ Thumbnail Generation Failed: {e}")
        return None
