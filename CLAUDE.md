# SaludAI

Automated pipeline that translates English health articles into Spanish, verifies accuracy, optimizes for SEO, and publishes to WordPress.

## Running the pipeline

```bash
source venv/bin/activate

# Full run (translates + publishes to WordPress)
python main.py "Article text here..."

# Dry run (all processing steps, skips WordPress publish — use for testing)
python main.py "Article text here..." --dry-run

# From a file
python main.py "$(cat /tmp/article.txt)"
```

## Pipeline architecture

Sequential steps in `main.py`:

```
Input (URL or raw text)
  → extract_original_text()       [BeautifulSoup4, only if URL]
  → extract_and_translate()       [gpt-4o]        modules/translation.py
  → moderate_content()            [gpt-4o]        modules/moderation.py
  → fact_check_translation()      [gpt-4o]        modules/fact_check.py
  → generate_seo_data()           [gpt-4o-mini]   modules/seo.py         ← 1 call, returns excerpt + category
  → format_content_as_html()      [gpt-4o-mini]   modules/formatting.py
  → generate_thumbnail()          [gpt-image-1-mini] modules/thumbnail.py
  → publish_to_wordpress()                        modules/wordpress.py
```

## Current model configuration (`config.py`)

| Module | Model | Reason |
|--------|-------|--------|
| translation | gpt-4o | Complex instruction-following required (acronym rules) |
| moderation | gpt-4o | Medical knowledge + Spanish comprehension |
| fact_check | gpt-4o | Bilingual EN/ES comparison |
| seo | gpt-4o-mini | Simple JSON output, low complexity |
| formatting | gpt-4o-mini | HTML structuring, low complexity |
| thumbnail | gpt-image-1-mini | Image generation |

**Do not downgrade translation below gpt-4o** — the prompt has strict acronym formatting rules that smaller models drop.

## Cost per article (estimated, ~4000 char article)

| Item | Cost |
|------|------|
| gpt-4o input (~6,800 tokens) | $0.017 |
| gpt-4o output (~4,900 tokens) | $0.049 |
| gpt-4o-mini (SEO + formatting) | ~$0.001 |
| DALL-E 3 (1792×1024) | $0.080 |
| **Total** | **~$0.15** |

DALL-E is ~53% of total cost. At 100 articles/month ≈ $15.

**Previous cost with gpt-4:** ~$0.56/article. Tier 1 upgrade saved ~73%.

## Optimisations already applied

1. **SEO: 2 calls → 1 call** — `generate_excerpt()` + `assign_category()` merged into `generate_seo_data()`, input truncated to 2000 chars
2. **Fact-check chunking** — was sending full original + full translated in one call (context limit risk); now chunks with proportional original slices + error fallback
3. **Moderation error handling** — added try/except to short-text path (was crashing silently)
4. **Fail-fast after translation** — pipeline aborts if all chunks fail, preventing token waste on downstream steps
5. **Model upgrade** — gpt-4 → gpt-4o (-92% cost), gpt-3.5-turbo → gpt-4o-mini (off deprecated model)
6. **WordPress error handling** — non-JSON responses no longer crash the process
7. **`--dry-run` flag** — skip WordPress publish for testing

## Known issues

- **Title extraction**: if input text has no explicit title as first line, `formatting.py` uses the first paragraph as title → very long post slug. Fix: always include a short title as the first line of input, or pass `--title "..."` (not yet implemented).

## Environment variables (`.env`)

```
OPENAI_API_KEY=
WP_URL=https://saludai.app/wp-json/wp/v2/posts
MEDIA_URL=https://saludai.app/wp-json/wp/v2/media
WP_USER=dev
WP_APP_PASSWORD=
```

## WordPress categories

Predefined in `modules/seo.py` prompt:
`Medicina Estetica` · `Inteligencia Artificial` · `Tecnologia Medica` · `Fitness` · `Biotecnologia` · `Economia`

## Translation conventions

- English technical acronyms preserved: `Aprendizaje Automático (Machine Learning - ML)`
- Citations/footnote markers removed during translation
- Text chunked at 3000 chars for translation, 4000 chars for moderation
- Fact-check chunks paired by proportional position to original

## Next optimisation candidates

- **Tier 2**: Test DeepSeek-V3 for translation + fact-check (~99% cheaper than gpt-4o, needs validation on acronym rules)
- **DALL-E cost**: reuse a pool of pre-generated thumbnails or make thumbnail optional to cut 53% of per-article cost
- **Title input**: add `--title` flag to avoid the long-slug problem
- **Parallelise**: SEO + formatting steps are independent and could run concurrently

## Dependencies

```
openai / requests / python-dotenv / beautifulsoup4
```

---

## Coding guidelines (Karpathy principles)

Behavioral guidelines to reduce common LLM coding mistakes.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

### 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

### 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

### 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it — don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

### 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```
