# e-mahmoudi.me

Personal portfolio website for **Ehsan Mahmoudi** — blockchain consultant, software architect, and rock climber from Tehran, Iran.

**Live:** [e-mahmoudi.me](https://e-mahmoudi.me)

## About

A single-page static site with no frameworks, no build tools, and no dependencies. Just HTML, CSS, and vanilla JavaScript.

The site tells my story through interactive accordion sections — from learning C# in university to deploying smart contracts on Cardano, from summiting Damavand to climbing 8a sport routes, from building Iran's music streaming platform to becoming a dad during wartime.

## Tech Stack

- **HTML5** — Semantic markup, structured data (Schema.org), Open Graph, SEO
- **CSS3** — Custom properties, flexbox/grid, responsive (900px/480px breakpoints), GPU-accelerated animations
- **JavaScript ES6+** — Accordion, lightbox, crypto donation tabs, scroll reveal (Intersection Observer)
- **Google Analytics** — GA4 tracking
- **WebP images** — Optimized with ffmpeg (thumbnails 480px, full-size 1200px)

## Features

- 8 personal stories with image galleries and lightbox viewer
- Consulting section with booking links
- Crypto donation support (ETH, BTC, BSC, XRP, ADA) with clipboard copy
- Skills grid organized by category
- Dark theme with custom typography (Instrument Serif, IBM Plex Mono, Libre Franklin)
- Fully responsive — mobile to desktop
- SEO optimized for blockchain/software consulting searches

## Run Locally

```bash
python3 -m http.server 8000
```

Then open [http://localhost:8000](http://localhost:8000)

## Structure

```
index.html              # Single page — all sections
css/style.css           # Styles
js/main.js              # Scripts
assets/
  avatar.png            # Profile image & favicon
  Ehsan_Mahmoudi_CV.pdf # Downloadable resume
  stories/
    web/                # Gallery thumbnails (480px WebP)
    full/               # Lightbox images (1200px WebP)
robots.txt
sitemap.xml
```

## Adding Story Images

1. Place original photos in a temp folder
2. Generate optimized versions:
   ```bash
   # Thumbnails
   ffmpeg -i input.jpg -vf "scale='min(480,iw)':-2" -quality 75 web/N/1.webp

   # Full-size for lightbox
   ffmpeg -i input.jpg -vf "scale='min(1200,iw)':-2" -quality 85 full/N/1.webp
   ```
3. Reference in HTML: `<img src="assets/stories/web/N/1.webp">`
4. Lightbox automatically loads from `full/` path

## License

- **Code** (HTML, CSS, JS): [GPL-3.0](LICENSE)
- **Images** (`assets/stories/`, `assets/avatar.png`): All Rights Reserved. Personal photographs may not be used without written permission.

## Contact

- **Email:** me@e-mahmoudi.me
- **GitHub:** [@jeyem](https://github.com/jeyem)
- **Twitter:** [@jeyem90](https://twitter.com/jeyem90)
- **LinkedIn:** [ehsan-mahmoudi](https://www.linkedin.com/in/ehsan-mahmoudi-611123b8/)
