# fact_check.py

from config import get_openai_api_key, get_model_for_module
from openai import OpenAI

client = OpenAI(api_key=get_openai_api_key())

SYSTEM_PROMPT = (
    "You are verifying a Spanish translation of an English text. "
    "You will receive two versions: first the English (original), then the Spanish (translated). "
    "Perform a side-by-side comparison for factual accuracy, missing details, or hallucinations. "
    "Your final output must be the corrected Spanish text ONLY, preserving paragraphs and structure. "
    "Do not include commentary, instructions, directives, or summary in English or Spanish. "
    "Do not re-translate everything back to English. "
    "Do not begin your response with any instruction, label, or meta-commentary — start immediately with the Spanish text. "
    "If the Spanish text is already fully accurate, return it verbatim. "
    "Otherwise, make only minimal corrections in Spanish where you find factual or translational errors."
)

# Max chars per side before splitting into chunks
CHUNK_MAX_CHARS = 3000


def _fact_check_chunk(model, orig_chunk, trans_chunk, fallback):
    """Fact-checks a single pair of original/translated chunks. Returns fallback on failure."""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"**Original (English)**:\n{orig_chunk}\n\n"
                        f"**Translated (Spanish)**:\n{trans_chunk}"
                    )
                }
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"❌ Fact-check chunk error: {e}. Keeping translated text unchanged.")
        return fallback


def fact_check_translation(original_text, translated_text):
    """
    Compares the Spanish translation with the original English text chunk by chunk
    and returns a final, fact-checked Spanish version.
    Chunks are paired by proportional position to avoid context limit failures.
    """
    model = get_model_for_module("fact_check")

    # If both texts fit comfortably in one call, process directly
    if len(original_text) + len(translated_text) <= 8000:
        return _fact_check_chunk(model, original_text, translated_text, fallback=translated_text)

    # Split translated text into chunks
    words = translated_text.split()
    chunks = []
    current = []
    for word in words:
        current.append(word)
        if len(" ".join(current)) > CHUNK_MAX_CHARS:
            chunks.append(" ".join(current))
            current = []
    if current:
        chunks.append(" ".join(current))

    orig_len = len(original_text)
    trans_len = len(translated_text)
    results = []
    pos = 0

    print(f"ℹ️ Fact-checking {len(chunks)} chunks...")
    for i, chunk in enumerate(chunks):
        # Map each translated chunk to a proportional slice of the original
        start_ratio = pos / trans_len
        end_ratio = min((pos + len(chunk)) / trans_len, 1.0)
        orig_chunk = original_text[int(start_ratio * orig_len):int(end_ratio * orig_len)]

        print(f"⚙️ Fact-checking chunk {i+1}/{len(chunks)}...")
        result = _fact_check_chunk(model, orig_chunk, chunk, fallback=chunk)
        results.append(result)
        pos += len(chunk)

    return "\n\n".join(results)
