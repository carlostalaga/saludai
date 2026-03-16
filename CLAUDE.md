# SaludAI

Automated pipeline that translates English health content into Spanish, verifies accuracy, optimizes for SEO, and publishes to WordPress.

## Running the pipeline

```bash
# Activate virtual environment
source venv/bin/activate

# Process a URL
python main.py https://example.com/health-article

# Process raw text
python main.py "Your English health content here"
```

## Architecture

Sequential pipeline orchestrated by `main.py`:

```
Input (URL or text)
  → extract_original_text()       [BeautifulSoup4, if URL]
  → extract_and_translate()       [GPT-4]
  → moderate_content()            [GPT-4]
  → fact_check_translation()      [GPT-4]
  → generate_excerpt()            [GPT-3.5-Turbo]
  → assign_category()             [GPT-3.5-Turbo]
  → format_content_as_html()      [GPT-3.5-Turbo]
  → generate_thumbnail()          [DALL-E 3]
  → publish_to_wordpress()
```

## Modules

| File | Responsibility |
|------|---------------|
| `main.py` | Pipeline controller |
| `config.py` | API keys and model mapping |
| `modules/translation.py` | English → Spanish via GPT-4, chunk-based (3000–4000 chars) |
| `modules/moderation.py` | Content safety review |
| `modules/fact_check.py` | Verify translation against original English |
| `modules/seo.py` | Generate 160-char excerpt + assign category |
| `modules/formatting.py` | Convert to HTML, extract title |
| `modules/thumbnail.py` | Generate image via DALL-E 3 |
| `modules/wordpress.py` | Publish via WordPress REST API |

## Environment variables

Required in `.env`:

```
OPENAI_API_KEY=
WP_URL=           # WordPress REST API posts endpoint
MEDIA_URL=        # WordPress media endpoint
WP_USER=
WP_APP_PASSWORD=
```

## Model mapping

Defined in `config.py → get_model_for_module()`:

- `translation`, `moderation`, `fact_check` → `gpt-4`
- `seo`, `formatting` → `gpt-3.5-turbo`
- `thumbnail` → DALL-E 3 (via `client.images.generate`)

## WordPress categories

Predefined in `modules/wordpress.py`:
- Medicina Estetica
- Inteligencia Artificial
- Tecnologia Medica
- Fitness
- Biotecnologia
- Economia

## Key conventions

- English technical acronyms are preserved in Spanish output (not translated)
- Citations are removed during translation
- Long texts are chunked (3000–4000 chars) for API calls
- `DEBUG = True` in `main.py` enables verbose step-by-step logging
- Error handling: fallback to original content if API calls fail; chunk processing continues on individual chunk failure

## Dependencies

```
openai
requests
python-dotenv
beautifulsoup4
```

## Optimization goal

The pipeline currently runs all steps sequentially. Steps 5–7 (`generate_excerpt`, `assign_category`, `format_content_as_html`) are independent and are candidates for parallelization.
