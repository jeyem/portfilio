# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Personal portfolio website for Ehsan Mahmoudi (e-mahmoudi.me). Single-page static site built with vanilla HTML5, CSS3, and JavaScript ES6+ — no framework, no build system, no dependencies.

## Structure

```
/
├── index.html                          # HTML structure + head metadata + GA4
├── css/style.css                       # All styles
├── js/main.js                          # All scripts (accordion, tabs, lightbox, etc.)
├── assets/
│   ├── avatar.png                      # Profile image, used as favicon + og:image
│   ├── Ehsan_Mahmoudi_CV.pdf           # Downloadable resume
│   └── stories/
│       ├── web/[1-8]/*.webp            # Gallery thumbnails (480px, ~708KB total)
│       └── full/[1-8]/*.webp           # Lightbox full-size (1200px, ~3.5MB total)
├── robots.txt                          # Crawl directives
├── sitemap.xml                         # Single-page sitemap
├── .gitignore
└── CLAUDE.md
```

There is no package.json, no build step, and no test suite.

## Development

Serve with any static file server (external CSS/JS won't load via `file://`):
```
python3 -m http.server 8000
```

## Architecture

- **`index.html`** — Head metadata (SEO, Open Graph, structured data with Person + Service schemas, Google Fonts, GA4 `G-XE11SNJJ42`) and semantic HTML body sections: nav, hero, stories (accordion with image galleries), consulting (pricing cards + skills grid), support (crypto donations — ETH, BTC, BSC, XRP, ADA), lightbox overlay, footer.
- **`css/style.css`** — CSS with custom properties defined at `:root` (dark theme: `--bg: #101010`, `--fg: #E2DDD6`, `--accent: #E8734A`). Responsive breakpoints at 900px and 480px. Includes: story gallery styles, lightbox overlay, skills grid (4-col → 2-col on mobile), plan card flexbox alignment.
- **`js/main.js`** — Vanilla JS for nav scroll effects, story accordion toggling, crypto chain tab switching (5 chains), clipboard copy, lightbox (click to open, click/Esc to close, loads full-size from `/full/`), Intersection Observer scroll-reveal animations, smooth scroll for nav links.

## Stories (8 accordion items, data-story 0-7)

0. **Origin Story** — IT bachelor's, C#, mentor → Linux/FSF, GPL3 contributions, PHP → Python/Django, AI master's (incomplete), first job at Cvas (Flask/MongoDB)
1. **Rock Climbing** — Basketball injuries → fitness (7 years) → mountaineering (Damavand summit) → rock climbing, 8a sport, top 10% worldwide
2. **Golang & Low-Level** — Diod Connection (one-way UDP, Reed-Solomon), fell for Golang concurrency, AEC Java→Golang rewrite (1GB/min Cassandra)
3. **Navaak Days** — Music streaming startup (5k+ users), CI/CD, cloud storage, publisher panel, recommendation engine, marriage, left when focus drifted → back to AEC (SNMP/ICMP monitoring, InfluxDB/Postgres/RabbitMQ/Gin)
4. **Rechat** — Dallas startup, first international role, MLS data sync (20+ providers, RabbitMQ/Postgres/Node.js), incidents reduced, left when asked to relocate to Turkey
5. **Blockchain Journey** — Learned Solidity, joined Socious (Japanese startup), rewrote PHP→Node.js, escrow on Milkomeda→Cardano (Aiken), digital identity, full refactor, left when realized fund-chasing model
6. **Fatherhood** — Son born Sep 21 2025, war/sanctions/chaos context, can't get passport due refused military service
7. **What's Next** — Building fitness app, helping others, LLM/AI agents, open for work

## Crypto Addresses (in js/main.js)

- ETH: `0x0eF141188cc4E8E0f8022ad7c50172f0feEE9Ca8`
- BTC: `bc1pc8vuu2va29wp3mlf5zye7pfl0g350agxeerqe67hm3jt6876cleqhxutmd`
- BSC: `0x0eF141188cc4E8E0f8022ad7c50172f0feEE9Ca8` (same as ETH)
- XRP: `rKSCtxX1EMpLd2TK1y9sreNb3QAKnT12DG`
- ADA: `addr1qxgp4e62vnqpp4u3nxmlsy6f484h4gfhup2sdznm3c2tena9dve7tnrgrjhkvepdapa7eus0a9y57aty6tla62yj0rnqpy7wcq`

## SEO Targets

Primary search terms the site is optimized for:
- blockchain consultant / blockchain consulting
- smart contract developer / Solidity developer
- software architect consulting
- startup technical consultant / startup CTO consultant
- hire blockchain developer (remote)
- Cardano developer / Ethereum developer
- Golang backend architect
- dApp development consulting

## Image Pipeline

Original photos are NOT kept in the repo. Optimized versions only:
- **Thumbnails** (`assets/stories/web/`): ffmpeg → 480px wide, WebP quality 75
- **Full-size** (`assets/stories/full/`): ffmpeg → 1200px wide, WebP quality 85
- To add new images: place originals in a temp folder, run ffmpeg conversion, delete originals

## Conventions

- CSS custom properties for all colors — change theme by modifying `:root` variables
- Fonts: Instrument Serif (headings), IBM Plex Mono (technical), Libre Franklin (body) via Google Fonts
- Animations use CSS transforms for GPU acceleration; hero elements use staggered `fadeUp` keyframes
- JavaScript binds via `data-*` attributes and semantic selectors — no IDs for JS hooks (except lightbox, donate elements)
- Mobile-first responsive: nav links hidden on mobile, single-column layouts below 900px
- Story galleries scroll horizontally on mobile, lightbox opens full-size on click
- Skills grid: 4 columns desktop → 2 columns mobile
