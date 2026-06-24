# Blog syndication

Cross-posts `content/blog/*.md` to other platforms on every push to `master`,
**always linking back to the original on e-mahmoudi.me** — `canonical_url` for
SEO credit, plus a visible backlink for human click-through. The point is
portfolio traffic, not handing the article to dev.to.

| Platform | How | Links home |
|---|---|---|
| dev.to | full article via API | `canonical_url` + top/bottom backlink |
| Hashnode | full article via API | `originalArticleURL` + top/bottom backlink |
| Mastodon | auto-posted hook (LLM or template) | URL in the post |
| LinkedIn / X | copy + pre-filled submit link in a GitHub issue | URL in copy & link |
| Hacker News / Reddit / Lobsters | pre-filled submit link in a GitHub issue | the submitted URL |

HN/Reddit/Lobsters have no safe write API and auto-submission risks bans, so the
workflow opens a **GitHub issue** with one-click pre-filled submit links and
ready-to-paste LinkedIn/X copy for you to review and post.

## Triggers

- **Push to `master`** touching `content/blog/**` — publishes/updates everything.
- **Manual** (Actions → "Syndicate blog posts" → Run workflow) — toggle
  `announce` off for a quiet run.

Publishing is **idempotent**: dev.to matches by `canonical_url`, Hashnode by
slug — existing posts are updated, not duplicated. Social announce + the share
issue fire **once per post**, tracked in `.github/syndication-state.json`.

### First run

The first run finds no state file, so it **seeds** `syndication-state.json` with
the current back-catalogue and **skips** social announcements (no flood). It
still publishes everything to dev.to/Hashnode. To re-announce a specific post
later, remove its slug from the state file.

## Secrets / variables

All optional — anything unset is skipped. Add under **Settings → Secrets and
variables → Actions**.

### Secrets

| Name | Platform | Where to get it |
|---|---|---|
| `DEVTO_API_KEY` | dev.to | dev.to → Settings → Extensions → "DEV Community API Keys" |
| `HASHNODE_TOKEN` | Hashnode | Hashnode → Settings → Developer → Personal Access Token |
| `HASHNODE_PUBLICATION_ID` | Hashnode | Your blog dashboard URL, or GraphQL `me { publications }` |
| `MASTODON_INSTANCE` | Mastodon | e.g. `https://mastodon.social` |
| `MASTODON_TOKEN` | Mastodon | Instance → Preferences → Development → New app (scope `write:statuses`) |
| `LLM_API_KEY` | LLM copy | Hugging Face → Settings → Access Tokens (default), or any provider key |

`GITHUB_TOKEN` is provided automatically (the workflow grants it `issues: write`
and `contents: write`).

### Variables (non-secret, optional)

| Name | Default | Notes |
|---|---|---|
| `LLM_BASE_URL` | `https://router.huggingface.co/v1` | Any OpenAI-compatible endpoint |
| `LLM_MODEL` | `Qwen/Qwen2.5-72B-Instruct` | Use an ungated instruct model |

The LLM step only writes the **short social copy** (Mastodon/LinkedIn/X hooks),
never the long-form articles. Because it's OpenAI-compatible, point `LLM_BASE_URL`
+ `LLM_MODEL` + `LLM_API_KEY` at any provider (e.g. the Anthropic API for higher
quality). If `LLM_API_KEY` is unset, a plain title+link template is used.

## Run locally

```bash
pip install -r .github/scripts/requirements.txt
DEVTO_API_KEY=... python .github/scripts/syndicate.py   # from repo root
```

With no secrets set it makes no network calls — it just seeds/updates the state
file, which is handy for a dry run.
