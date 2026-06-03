# SaludAI — Evolution Plan

## Current state

Sequential pipeline: every step always runs in order, no branching, no retries, no source discovery.

```
Input → Translate → Moderate → Fact-check → SEO → Format → Thumbnail → Publish
```

Cost: ~$0.15/article (thumbnail is 53% of total at $0.08).

---

## Goal

Evolve to an agentic system that:
- Discovers articles automatically (no manual paste)
- Makes decisions during processing (retry, skip, escalate)
- Runs independent steps in parallel
- Feeds quality failures back into earlier steps

---

## Target architecture (3 tiers)

### Tier 1 — Content Scout Agent
Runs on a schedule (e.g. nightly). Replaces manual article input.

- Monitors RSS feeds and health news sources
- Scores articles by relevance and freshness
- Deduplicates against already-published articles
- Queues candidates for processing

**Tech:** gpt-4o-mini + SQLite queue + cron/APScheduler

### Tier 2 — Orchestrator Agent
Replaces `main.py`. Has a goal and a set of tools; decides order, retries, and when to stop.

Key new behaviours vs. the current pipeline:
- **Parallel calls** — SEO + formatting run concurrently (~40% time saving, no cost change)
- **Quality gate** — if fact-check error count is high, trigger re-translation of flagged sections instead of publishing bad content
- **Skip decisions** — short/simple articles can bypass chunked moderation
- **Retry with escalation** — thumbnail fail → retry → publish without image → flag for review

**Model:** gpt-4o-mini (orchestrator only decides what to call next; heavy text work stays in specialist modules)

**Context management (critical for cost):** orchestrator passes summaries/pointers between steps, not full article text. Without this, the growing context window becomes the largest cost item.

### Tier 3 — Specialist agents
Each current module becomes a proper agent with its own system prompt:

| Agent | Replaces | New capability |
|-------|----------|----------------|
| Translation agent | `translation.py` | Receives error list from fact-check, re-translates flagged sections |
| Quality agent | `moderation.py` + `fact_check.py` | Iterates until satisfied or gives up after N passes |
| Publishing agent | `wordpress.py` | Can schedule posts vs. publish immediately |

### Feedback loop (the key quality gain)

```
Translate
  → Fact-check → score errors
      → few errors   : continue to publish
      → many errors  : send error list back to Translation agent → re-translate flagged sections
      → after 2 retries still failing : escalate to human review
```

This loop does not exist today and is the biggest quality improvement from going agentic.

### Human-in-the-loop checkpoint (optional)
Orchestrator pauses after formatting, sends title + excerpt for approval before paying for thumbnail and publishing. Useful while the system is gaining trust.

---

## Model migration plan

### Current models and costs per article (~4,000 char article)

| Module | Model | Cost |
|--------|-------|------|
| translation | gpt-4o | |
| moderation | gpt-4o | |
| fact_check | gpt-4o | |
| seo | gpt-4o-mini | |
| formatting | gpt-4o-mini | |
| thumbnail | gpt-image-1-mini | $0.080 |
| **gpt-4o total** | 6,800 in / 4,900 out tokens | **$0.066** |
| **gpt-4o-mini total** | | **$0.001** |
| **Grand total** | | **~$0.147** |

### Alternative model pricing (per 1M tokens)

| Model | Input | Output | vs. gpt-4o |
|-------|-------|--------|------------|
| gpt-4o (current) | $2.50 | $10.00 | baseline |
| DeepSeek-V3 | $0.27 | $1.10 | ~9x cheaper |
| Qwen2.5-72B | $0.40 | $0.40 | ~6x cheaper |
| Qwen3-235B | $0.50 | $1.50 | ~5x cheaper |

| Image model | Per image | vs. current |
|-------------|-----------|-------------|
| gpt-image-1-mini (current) | $0.080 | baseline |
| Flux Pro (fal.ai) | $0.050 | −37% |
| Flux Dev | $0.025 | −69% |
| Flux Schnell | $0.003 | −96% |

### Quality assessment for this use case

**Translation** (highest risk — strict acronym formatting rules):
- **Qwen** — best alternative. Strong multilingual including Spanish; solid instruction following.
- **DeepSeek-V3** — primarily Chinese/English; Spanish is decent but less reliable for acronym rules.
- **Recommendation:** validate Qwen3 on 5–10 articles in parallel with gpt-4o before switching.

**Moderation + fact-check** (lower risk — reasoning-heavy, not Spanish-fluency-heavy):
- **DeepSeek-V3** — strong fit. Matches gpt-4o on reasoning benchmarks at 9x lower cost.

**SEO + formatting** (already near-free on gpt-4o-mini):
- Switching gives negligible savings. Leave as-is.

**Images:**
- Flux Pro is a quality-parity swap at −37% cost.
- Flux Schnell is 96% cheaper but visibly lower quality — evaluate per use case.

### Cost scenarios

| Configuration | Text | Image | Total | vs. $0.147 |
|---------------|------|-------|-------|------------|
| Current | $0.067 | $0.080 | **$0.147** | baseline |
| DeepSeek-V3 all text | $0.007 | $0.080 | **$0.087** | −41% |
| DeepSeek-V3 text + Flux Pro | $0.007 | $0.050 | **$0.057** | −61% |
| DeepSeek-V3 text + Flux Schnell | $0.007 | $0.003 | **$0.010** | −93% |
| Qwen translation + DeepSeek moderation/fact-check + Flux Pro | $0.008 | $0.050 | **$0.058** | −61% |

> Note: agentic orchestrator overhead adds ~$0.008/article (gpt-4o-mini + context pruning). Included in the figures above.

---

## Implementation phases

### Phase 1 — Model swap (low risk, ~40% cost reduction)
- [ ] Swap `moderation` + `fact_check` to DeepSeek-V3 in `config.py` (OpenAI-compatible API — change base URL and key only)
- [ ] Swap thumbnail to Flux Pro in `thumbnail.py` (new client, isolated change)
- [ ] Run 10 articles, verify output quality

### Phase 2 — Validate translation model (~additional 5% reduction)
- [ ] Run 5–10 articles through Qwen3 in parallel with gpt-4o
- [ ] Compare acronym formatting manually
- [ ] If rules hold consistently, update `config.py` for translation

### Phase 3 — Parallel execution (time saving, no cost change)
- [ ] Run SEO + formatting as concurrent tool calls in the orchestrator
- [ ] Estimated time saving: ~40% of pipeline wall-clock time

### Phase 4 — Orchestrator agent (quality improvement)
- [ ] Wrap each module as a tool definition
- [ ] Build orchestrator with gpt-4o-mini + system prompt describing goal and quality criteria
- [ ] Implement context pruning (pass summaries, not full article text, between steps)
- [ ] Add quality gate: score fact-check errors → retry or continue

### Phase 5 — Feedback loop
- [ ] Translation agent accepts error list from quality agent
- [ ] Re-translates flagged sections only (not full article)
- [ ] Escalate to human review after 2 failed retries

### Phase 6 — Content Scout
- [ ] SQLite table for article queue
- [ ] RSS feed monitor (health news sources)
- [ ] Relevance scoring with gpt-4o-mini
- [ ] Deduplication against published posts (WordPress API query)
- [ ] Cron schedule (nightly)

---

## Portability — running on a new machine

The `venv/` folder is not portable (compiled binaries, absolute paths baked in). Everything else copies cleanly.

### What to copy

| Copy | Item |
|------|------|
| ✅ | `main.py`, `config.py`, `modules/`, `requirements.txt` |
| ✅ | `.env` (API keys + WP credentials — copy securely, not via email) |
| ✅ | `CLAUDE.md`, `PLAN.md`, `SaludAI_Diagram.md` |
| ✅ | `.git/` (full history) |
| ✅ | `.claude/` (Claude Code memory/settings) |
| ❌ | `venv/` (rebuild on target machine) |
| ❌ | `__pycache__/` (auto-generated) |

### Setup on target machine

```bash
# Verify Python 3.13 is installed
python3 --version

# Create fresh virtual environment
python3 -m venv venv

# Install dependencies
source venv/bin/activate && pip install -r requirements.txt
```

### Even easier: git clone

If the repo has a GitHub/GitLab remote, clone it on the target machine — no USB needed. Only `.env` needs to be transferred separately (it is in `.gitignore`).

```bash
git remote -v  # check if a remote exists
```

---

## Open questions

- Image quality threshold: is Flux Schnell acceptable for a featured medical blog image?
- Human review escalation: email, Slack, or a simple flag in the WordPress draft?
- Article queue: SQLite is fine for low volume; if Scout runs multiple feeds, evaluate Postgres.
- Data privacy: DeepSeek and Qwen are Chinese-company APIs — acceptable for public health articles, review if content becomes sensitive.
