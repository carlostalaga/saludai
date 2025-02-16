import openai
import requests

openai.api_key = "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"

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
    """Generates a 1280x600 px abstract science-inspired thumbnail."""
    try:
        response = openai.Image.create(
            model="dall-e-3",  # Ensure DALL-E 3 is supported in your API access
            prompt=IMAGE_PROMPT,
            size="1280x600"
        )
        
        image_url = response["data"][0]["url"]
        return image_url  # ✅ Returns the generated image URL

    except Exception as e:
        print(f"❌ Thumbnail Generation Failed: {e}")
        return None
