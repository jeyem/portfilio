#!/usr/bin/env python3
"""Syndicate blog posts in content/blog/ to other platforms.

One rule: every surface links back to the original on e-mahmoudi.me
(canonical_url for SEO + a visible backlink for human click-through). The goal
is portfolio traffic, not giving the article away to dev.to.

    dev.to / Hashnode  -> full article + canonical_url + visible backlink
    Mastodon           -> auto-posted hook + link (LLM-written, template fallback)
    LinkedIn / X / HN
    Reddit / Lobsters  -> GitHub issue with ready-to-paste copy + pre-filled
                          submit links (these can't be auto-posted safely)

Every platform is optional: missing secret -> skipped. One platform failing
never blocks the others.

Run:  python .github/scripts/syndicate.py   (from the repo root)
Env:  see .github/SYNDICATION.md
"""

import json
import os
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import quote

import frontmatter
import requests

# Load a local .env when present (no-op in CI, which sets real env vars).
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

BLOG_DIR = Path("content/blog")
STATE_FILE = Path(".github/syndication-state.json")
BASE_URL = (os.environ.get("SITE_BASE_URL") or "https://e-mahmoudi.me/").rstrip("/") + "/"
ORIGIN = BASE_URL.rstrip("/")
HOST = re.sub(r"^https?://", "", ORIGIN)
ANNOUNCE = os.environ.get("ANNOUNCE") != "false"
# DRY_RUN: never call write APIs (no publishing, no toots, no issues). Previews
# what would happen and shows generated copy, so it's safe to run locally.
DRY_RUN = (os.environ.get("DRY_RUN") or "").lower() in ("1", "true", "yes")
TIMEOUT = 30


def preview(line):
    print(f"  [dry-run] {line}")


def env(key):
    return (os.environ.get(key) or "").strip()


# ---- Load posts ----------------------------------------------------------

def slugify(text):
    """Mirror Hugo's :slug permalink for ASCII titles: lowercase, runs of
    non-alphanumerics -> single hyphen, trimmed."""
    return re.sub(r"^-+|-+$", "", re.sub(r"[^a-z0-9]+", "-", str(text).lower()))


def load_posts():
    posts = []
    for path in sorted(BLOG_DIR.glob("*.md")):
        if path.name == "_index.md":
            continue
        post = frontmatter.load(path)
        data = post.metadata
        if data.get("draft") is True:
            continue
        # Hugo permalink is /blog/:slug/ where :slug = front-matter slug, else
        # the slugified TITLE (not the filename). Match that exactly so
        # canonical_url points at the real page.
        slug = str(data["slug"]).lower() if data.get("slug") else slugify(data.get("title") or path.stem)
        posts.append({
            "file": path.name,
            "data": data,
            "content": post.content,
            "slug": slug,
            "url": f"{BASE_URL}blog/{slug}/",
        })
    return posts


def absolutize(md):
    """Rewrite root-relative links/images to absolute so they resolve off-site."""
    md = re.sub(r"\]\(/(?!/)", f"]({ORIGIN}/", md)
    md = re.sub(r'(src|href)="/(?!/)', rf'\1="{ORIGIN}/', md)
    return md


def body_with_backlink(post):
    """Long-form body: visible backlink at top + CTA at bottom (canonical is set
    separately via the API). This is what turns a dev.to read into a site visit."""
    top = f"> 📌 Originally published at [{HOST}]({post['url']})\n\n"
    bottom = (
        f"\n\n---\n\n*Originally published at [{HOST}]({post['url']}). "
        f"I write about blockchain, backend, and software architecture — more at [{HOST}]({BASE_URL}).*"
    )
    return top + absolutize(post["content"]) + bottom


def devto_tags(tags):
    """dev.to tags: lowercase alphanumeric, max 4 (front matter is best-first)."""
    out = []
    for t in tags or []:
        clean = re.sub(r"[^a-z0-9]", "", str(t).lower())
        if clean:
            out.append(clean)
    return out[:4]


def hashnode_tags(tags):
    """Hashnode tags: {slug, name} objects, max 5."""
    out = []
    for t in tags or []:
        slug = re.sub(r"^-|-$", "", re.sub(r"[^a-z0-9]+", "-", str(t).lower()))
        if slug:
            out.append({"slug": slug, "name": str(t)})
    return out[:5]


# ---- State (which slugs have already been announced) ---------------------

def load_state():
    try:
        return set(json.loads(STATE_FILE.read_text()))
    except (FileNotFoundError, ValueError):
        return None  # None = first run


def save_state(slugs):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(sorted(slugs), indent=2) + "\n")


# ---- LLM: per-platform social copy (provider-agnostic, OpenAI-compatible) -

def template_copy(post):
    tags = " ".join("#" + re.sub(r"[^a-zA-Z0-9]", "", str(t)) for t in (post["data"].get("tags") or [])[:3])
    hook = post["data"].get("subtitle") or post["data"].get("description") or ""
    return {
        "x": f"{post['data']['title']}\n\n{post['url']} {tags}".strip(),
        "mastodon": f"{post['data']['title']}\n\n{hook}\n\n{post['url']}\n\n{tags}".strip(),
        "linkedin": f"{post['data']['title']}\n\n{hook}\n\nRead the full post: {post['url']}".strip(),
    }


def generate_copy(post):
    key = env("LLM_API_KEY")
    if not key:
        return template_copy(post)

    base = (env("LLM_BASE_URL") or "https://router.huggingface.co/v1").rstrip("/")
    model = env("LLM_MODEL") or "Qwen/Qwen2.5-72B-Instruct"
    article = absolutize(post["content"])[:6000]

    system = (
        "You write platform-native social posts that drive readers to a technical blog. "
        "Voice: first person, concrete, technical, no hype, minimal emoji. "
        "Every post MUST end with the original article URL. Return ONLY a JSON object, no prose."
    )
    user = (
        f"Original article URL (link to this in every post): {post['url']}\n"
        f"Title: {post['data']['title']}\n"
        f"Summary: {post['data'].get('description') or post['data'].get('subtitle') or ''}\n"
        f"Tags: {', '.join(map(str, post['data'].get('tags') or []))}\n\n"
        f'Article (markdown, may be truncated):\n"""\n{article}\n"""\n\n'
        'Return JSON with keys "linkedin", "x", "mastodon" (plain text, not markdown):\n'
        '- "x": <=270 chars including the URL, one strong hook + the URL, up to 3 hashtags.\n'
        '- "mastodon": <=480 chars, short hook + the URL, up to 4 hashtags.\n'
        '- "linkedin": 3-5 short paragraphs (blank line between), professional, ends with a call to read the full post and the URL.\n'
        f"The URL {post['url']} must appear in every value."
    )

    res = requests.post(
        f"{base}/chat/completions",
        headers={"authorization": f"Bearer {key}", "content-type": "application/json"},
        json={
            "model": model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "temperature": 0.7,
            "max_tokens": 1200,
        },
        timeout=TIMEOUT,
    )
    res.raise_for_status()
    text = res.json()["choices"][0]["message"]["content"]
    copy = json.loads(text[text.index("{"): text.rindex("}") + 1])

    fallback = template_copy(post)
    for k in ("linkedin", "x", "mastodon"):
        if not copy.get(k):
            copy[k] = fallback[k]
        elif post["url"] not in copy[k]:
            copy[k] += f"\n\n{post['url']}"
    return copy


# ---- dev.to --------------------------------------------------------------

def devto_existing_map(key):
    out = {}
    page = 1
    while True:
        res = requests.get(
            f"https://dev.to/api/articles/me/all?per_page=100&page={page}",
            headers={"api-key": key}, timeout=TIMEOUT,
        )
        res.raise_for_status()
        arr = res.json()
        for a in arr:
            if a.get("canonical_url"):
                out[a["canonical_url"]] = a["id"]
        if len(arr) < 100:
            break
        page += 1
    return out


def devto_sync(post, key, existing):
    article = {
        "title": post["data"]["title"],
        "body_markdown": body_with_backlink(post),
        "published": True,
        "canonical_url": post["url"],
        "description": post["data"].get("description") or "",
        "tags": devto_tags(post["data"].get("tags")),
    }
    article_id = existing.get(post["url"])
    if DRY_RUN:
        preview(f"dev.to would {'update' if article_id else 'create'}: {article['title']} "
                f"| tags={article['tags']} | canonical={article['canonical_url']}")
        return "dry-run"
    url = f"https://dev.to/api/articles/{article_id}" if article_id else "https://dev.to/api/articles"
    res = requests.request(
        "PUT" if article_id else "POST", url,
        headers={"api-key": key, "content-type": "application/json"},
        json={"article": article}, timeout=TIMEOUT,
    )
    res.raise_for_status()
    return "updated" if article_id else "created"


# ---- Hashnode ------------------------------------------------------------

def hashnode_gql(token, query, variables):
    res = requests.post(
        "https://gql.hashnode.com/",
        headers={"authorization": token, "content-type": "application/json"},
        json={"query": query, "variables": variables}, timeout=TIMEOUT,
    )
    body = res.json()
    if body.get("errors"):
        raise RuntimeError(f"Hashnode: {json.dumps(body['errors'])[:200]}")
    return body["data"]


def hashnode_existing_map(token, publication_id):
    data = hashnode_gql(
        token,
        "query($id:ObjectId!){ publication(id:$id){ posts(first:50){ edges{ node{ id slug } } } } }",
        {"id": publication_id},
    )
    edges = (data.get("publication") or {}).get("posts", {}).get("edges", [])
    return {e["node"]["slug"]: e["node"]["id"] for e in edges}


def hashnode_sync(post, token, publication_id, existing):
    post_id = existing.get(post["slug"])
    if DRY_RUN:
        preview(f"Hashnode would {'update' if post_id else 'create'}: {post['data']['title']} "
                f"| tags={[t['slug'] for t in hashnode_tags(post['data'].get('tags'))]} | original={post['url']}")
        return "dry-run"
    if post_id:
        hashnode_gql(
            token,
            "mutation($input:UpdatePostInput!){ updatePost(input:$input){ post{ id } } }",
            {"input": {
                "id": post_id,
                "title": post["data"]["title"],
                "contentMarkdown": body_with_backlink(post),
                "tags": hashnode_tags(post["data"].get("tags")),
            }},
        )
        return "updated"
    inp = {
        "title": post["data"]["title"],
        "contentMarkdown": body_with_backlink(post),
        "publicationId": publication_id,
        "slug": post["slug"],
        "tags": hashnode_tags(post["data"].get("tags")),
        "originalArticleURL": post["url"],
    }
    if post["data"].get("subtitle"):
        inp["subtitle"] = post["data"]["subtitle"]
    hashnode_gql(
        token,
        "mutation($input:PublishPostInput!){ publishPost(input:$input){ post{ id url } } }",
        {"input": inp},
    )
    return "created"


# ---- Mastodon ------------------------------------------------------------

def mastodon_announce(copy, instance, token):
    if DRY_RUN:
        preview("Mastodon would post:\n" + "\n".join("      " + l for l in copy["mastodon"].splitlines()))
        return
    res = requests.post(
        f"{instance.rstrip('/')}/api/v1/statuses",
        headers={"authorization": f"Bearer {token}", "content-type": "application/json"},
        json={"status": copy["mastodon"], "visibility": "public"}, timeout=TIMEOUT,
    )
    res.raise_for_status()


# ---- Manual share (GitHub issue) ----------------------------------------

def submit_links(post):
    u, t = quote(post["url"], safe=""), quote(post["data"]["title"], safe="")
    return {
        "Hacker News": f"https://news.ycombinator.com/submitlink?u={u}&t={t}",
        "Reddit": f"https://www.reddit.com/submit?url={u}&title={t}",
        "Lobsters": f"https://lobste.rs/stories/new?url={u}&title={t}",
        "X / Twitter": f"https://twitter.com/intent/tweet?text={t}&url={u}",
        "LinkedIn": f"https://www.linkedin.com/sharing/share-offsite/?url={u}",
    }


def open_share_issue(post, copy):
    links = "\n".join(f"- [ ] [{n}]({l})" for n, l in submit_links(post).items())
    body = (
        f"Promote **{post['data']['title']}** — every link points back to {post['url']}\n\n"
        f"### Submit (one-click, pre-filled)\n{links}\n\n"
        f"### LinkedIn copy (paste & edit)\n```\n{copy['linkedin']}\n```\n\n"
        f"### X copy (paste & edit)\n```\n{copy['x']}\n```\n"
    )
    if DRY_RUN:
        preview(f"GitHub issue 'Syndicate: {post['data']['title']}' would be opened with:\n"
                + "\n".join("      " + l for l in body.splitlines()))
        return True
    repo, token = env("GITHUB_REPOSITORY"), env("GITHUB_TOKEN")
    if not repo or not token:
        return False
    res = requests.post(
        f"https://api.github.com/repos/{repo}/issues",
        headers={"authorization": f"Bearer {token}", "accept": "application/vnd.github+json"},
        json={"title": f"Syndicate: {post['data']['title']}", "body": body, "labels": ["syndication"]},
        timeout=TIMEOUT,
    )
    res.raise_for_status()
    return True


# ---- Job summary ---------------------------------------------------------

def summary(line):
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a") as f:
            f.write(line + "\n")
    print(re.sub(r"[#*`>]", "", line))


# ---- Main ----------------------------------------------------------------

def main():
    posts = load_posts()
    seen = load_state()
    first_run = seen is None
    state = set(seen or [])

    devto_key = env("DEVTO_API_KEY")
    hashnode_token = env("HASHNODE_TOKEN")
    hashnode_pub = env("HASHNODE_PUBLICATION_ID")
    masto_instance = env("MASTODON_INSTANCE")
    masto_token = env("MASTODON_TOKEN")

    devto_existing = None
    if devto_key:
        if DRY_RUN:
            devto_existing = {}  # skip the network read; previews as "would create"
        else:
            try:
                devto_existing = devto_existing_map(devto_key)
            except Exception as e:
                print("dev.to list failed:", e)

    hashnode_existing = None
    if hashnode_token and hashnode_pub:
        if DRY_RUN:
            hashnode_existing = {}
        else:
            try:
                hashnode_existing = hashnode_existing_map(hashnode_token, hashnode_pub)
            except Exception as e:
                print("Hashnode list failed:", e)

    summary(f"## Syndication — {date.today().isoformat()}{' (DRY RUN)' if DRY_RUN else ''}")
    if first_run and not DRY_RUN:
        summary("> First run: seeding state, social announcements skipped for the back catalogue.")

    for post in posts:
        results = []

        if devto_key and devto_existing is not None:
            try:
                results.append(f"dev.to {devto_sync(post, devto_key, devto_existing)}")
            except Exception as e:
                results.append(f"dev.to failed ({str(e)[:80]})")

        if hashnode_token and hashnode_pub and hashnode_existing is not None:
            try:
                results.append(f"Hashnode {hashnode_sync(post, hashnode_token, hashnode_pub, hashnode_existing)}")
            except Exception as e:
                results.append(f"Hashnode failed ({str(e)[:80]})")

        # DRY_RUN previews social for every post; live runs only for genuinely
        # new posts (and never on the first/seed run).
        is_new = post["slug"] not in state
        if ANNOUNCE and (DRY_RUN or (is_new and not first_run)):
            try:
                copy = generate_copy(post)
            except Exception as e:
                results.append(f"LLM failed, used template ({str(e)[:60]})")
                copy = template_copy(post)

            if DRY_RUN or (masto_instance and masto_token):
                try:
                    mastodon_announce(copy, masto_instance, masto_token)
                    results.append("Mastodon announced")
                except Exception as e:
                    results.append(f"Mastodon failed ({str(e)[:80]})")
            try:
                if open_share_issue(post, copy):
                    results.append("share issue opened")
            except Exception as e:
                results.append(f"share issue failed ({str(e)[:80]})")

        state.add(post["slug"])
        summary(f"- **{post['data']['title']}** — {', '.join(results) if results else 'no platforms configured'}")

    if not DRY_RUN:
        save_state(state)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)
