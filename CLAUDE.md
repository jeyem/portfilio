# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Personal portfolio website for Ehsan Mahmoudi (e-mahmoudi.me). Built with **Hugo** static site generator, vanilla CSS, and vanilla JavaScript. No JS framework, no CSS preprocessor.

## Development Commands

```bash
# Dev server (drafts included, live reload)
npm run dev          # hugo server --buildDrafts --disableFastRender

# Production build → dist/
npm run build        # hugo --minify --destination dist
```

Hugo must be installed (`hugo version` to check). No other dependencies.

## Structure

```
hugo.toml                   # Site config (baseURL, GA4 ID, calendar URL, permalinks)
content/
  _index.md                 # Homepage front matter (title, description)
  blog/
    _index.md               # Blog list description
    *.md                    # Blog posts
layouts/
  _default/baseof.html      # Base template (nav, lightbox overlay, main.js)
  index.html                # Homepage: assembles hero/stories/consulting/support partials
  partials/
    head.html               # <head> — SEO, OG, structured data, GA4, Google Fonts
    nav.html
    hero.html
    stories.html            # Renders $.Site.Data.stories
    consulting.html         # Renders $.Site.Data.consulting
    support.html            # Renders $.Site.Data.crypto
    footer.html
  blog/
    list.html               # Blog index
    single.html             # Blog post
data/
  stories.yaml              # 8 accordion stories (index, icon, tag, paragraphs, gallery)
  consulting.yaml           # Pricing plans + skill groups
  crypto.yaml               # Donation chain addresses
static/
  assets/
    avatar.png              # Profile image, favicon, og:image
    Ehsan_Mahmoudi_CV.pdf
    stories/
      web/[1-8]/*.webp      # Gallery thumbnails (480px)
      full/[1-8]/*.webp     # Lightbox full-size (1200px)
  robots.txt
  _headers                  # HTTP headers for CDN
static/css/style.css        # All styles — Hugo serves this at /css/style.css
static/js/main.js           # All scripts — Hugo serves this at /js/main.js
css/style.css               # Mirror of static/css/style.css (kept in sync manually)
js/main.js                  # Mirror of static/js/main.js (kept in sync manually)
```

## Architecture

Content and data are separated: dynamic section content lives in `data/*.yaml` files, not in templates or JS. Partials iterate over site data via `$.Site.Data.*`.

**Editing CSS/JS**: Always edit `static/css/style.css` and `static/js/main.js` — those are what Hugo serves. The root-level `css/` and `js/` are mirrors kept in sync manually.

- **`layouts/partials/stories.html`** — `{{ range $.Site.Data.stories }}` renders each story accordion item with icon, paragraphs, and gallery images from `static/assets/stories/web/{folder}/`.
- **`layouts/partials/consulting.html`** — `{{ range .Site.Data.consulting.plans }}` and `{{ range .Site.Data.consulting.skillGroups }}`.
- **`layouts/partials/support.html`** — `{{ range .Site.Data.crypto.chains }}` for donation tabs.
- **`js/main.js`** — Handles all interactivity post-render: accordion toggle, crypto chain tabs + clipboard copy, lightbox (loads full-size from `/assets/stories/full/`), Intersection Observer scroll-reveal, nav scroll effect, smooth scroll.

## Blog Posts

Add a file to `content/blog/`. Front matter fields used by the template:

```yaml
---
title: "Post Title"
date: 2025-01-15
description: "Summary shown in list and single views"
tags: ["blockchain", "golang"]
draft: false
---
```

Tags render as `<span class="skill-tag">` chips (same class as the skills grid).

`markup.goldmark.renderer.unsafe = false` in `hugo.toml` — raw HTML in blog post markdown will not render. Use Hugo shortcodes for any HTML embedding needs.

## CSS Conventions

Custom properties in `:root`: `--bg: #101010`, `--fg: #E2DDD6`, `--accent: #E8734A`. All colors use these vars. Responsive breakpoints: 900px and 480px. Fonts via Google Fonts: Instrument Serif (headings), IBM Plex Mono (technical), Libre Franklin (body).

## Adding Story Images

```bash
# Thumbnails (480px)
ffmpeg -i input.jpg -vf "scale='min(480,iw)':-2" -quality 75 static/assets/stories/web/N/1.webp

# Full-size for lightbox (1200px)
ffmpeg -i input.jpg -vf "scale='min(1200,iw)':-2" -quality 85 static/assets/stories/full/N/1.webp
```

Reference in `data/stories.yaml` under `gallery.folder` and `gallery.images`. Original photos are not kept in the repo.

## SEO

GA4 ID `G-XE11SNJJ42` and calendar URL are set in `hugo.toml [params]`. Structured data (Person + Service schemas) and Open Graph are in `layouts/partials/head.html`. Primary SEO targets: blockchain consultant, smart contract developer, Cardano/Ethereum developer, Golang backend architect, startup CTO consulting.
