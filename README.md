# Daniel Salkin — Engineering Portfolio

A static, responsive portfolio using the Nord palette, JetBrains Mono, and the photos and reports in `documentation/`. No build step or package installation is required.

## Preview locally

From this directory:

```sh
python3 -m http.server 8000
```

Then open http://localhost:8000. You can also open `index.html` directly.

## Publish on GitHub Pages

1. Push these files to the `main` branch of your GitHub repository.
2. In **Settings → Pages → Build and deployment**, select **GitHub Actions**.
3. The included `pages.yml` workflow deploys the site on each push to `main`, or via **Actions → Deploy portfolio to GitHub Pages → Run workflow**.

All local links are relative, so both a `username.github.io` repository and a project repository work. If your default branch has another name, update the workflow trigger. No domain or account configuration has been changed by this implementation.

## Editing

- `index.html`: introduction and Honda jacket portrait.
- `projects.html`: project narratives, reports, and photo galleries.
- `experience.html`: work history, education, skills, and organization links.
- `contact.html`: email, phone, and résumé links.
- `styles.css`: layout, responsive breakpoints, Nord colors, and typography.
- `script.js`: accessible image dialog.
- `documentation/`: original project photos and downloadable PDFs.

Project descriptions, technical details, and galleries are always visible without expanding panels. Image links open the originals when JavaScript is unavailable. The font uses Google Fonts with local monospace fallbacks. Images retain their original colors to keep PCB and oscilloscope details legible. The Voron V0 shown here is the robotics-team printer, distinct from the Micron+ listed in the résumé.

The reference site at jonathan-tao.github.io and the Google Slides URL could not be retrieved in this environment. This is an original static implementation following the brief’s described sidebar architecture, scrolling flow, structure; it does not claim to reproduce that site’s source code.

## Licenses and asset review

The full Nord MIT copyright, permission notice, and disclaimer are preserved in `licenses/nord-MIT.txt`. The deployment includes this file, and every page links to `notices.html`, which reproduces the notice. Keep both when redistributing Nord-derived styling. This does not apply an MIT license to the entire portfolio.

JetBrains Mono is served through Google Fonts under SIL OFL 1.1; no font binaries are bundled. See the font attribution and upstream license link on the notices page. If font files are later self-hosted, bundle their full copyright and OFL license with them.

The experience page now uses the logo files supplied in `documentation/Portfolio Photos/Logos`, as requested. Supplied files do not by themselves establish third-party usage or modification rights. Organization names link to official sites. See `documentation/asset-rights-review.md` for the sources, conclusions, and unresolved ownership checks.

The experience page uses supplied organization logos; the original generic university icon remains for UIUC. Project images use compact two-column layouts. The purple dashboard layout replaces the 3D render and uses `object-fit: contain` without click-to-enlarge. Supporting galleries retain optional enlargement.

## Image color treatment

The site uses original source images with a presentation-only CSS `saturate(.65)` filter on the portrait, project images, and baking photos. Full-size image dialogs open unfiltered originals. There is no Honda portrait caption.

Experience marks use separate CSS treatment: SpaceX uses white, Deere uses Nord green (`#a3be8c`), MorTorq maps orange toward Nord orange while preserving neutral tones, and the supplied Illinois Block I uses a CSS-referenced SVG color matrix. That matrix maps Illinois orange to Nord orange `#d08770` and navy to Polar Night `#2e3440`, preserving transparency. The exported IEM vector uses the same two Nord colors directly.

`assets/nordified/` and `scripts/nordify-images.py` retain the earlier separate-image experiment, but no page references those variants. Original files remain unchanged. The GitHub Pages workflow excludes the unused experiment from deployment.

Analog Swerve now uses the supplied `betterTrackingADC.JPG` and `servoControlUnit.JPG` photos alongside the assembled-module photograph from the report. Baking photos and captions use the supplied caramel apple pie and matcha crinkle images.

The Dash project now presents its system diagram inline and includes power, CAN transceiver, switch, and microcontroller schematics, replacing the PCB layout image. Schematics retain their original colors for readability. Baking preview crops prioritize the 3 Musketeers and chocolate soufflé desserts. IEM, Illinois orange, and MorTorq orange target the same Nord orange (`#d08770`).

The introduction uses a side-by-side portrait layout, experience pairs dates with descriptions, and baking uses its compact thumbnail grid. Project narratives use one vertical column with paired image galleries. CAN equations are inline LaTeX between `\(` and `\)` delimiters, rendered by MathJax 3.2.2 from jsDelivr on the Projects page. Math rendering needs internet access; the raw LaTeX remains in the HTML if the CDN is unavailable. No MathJax library files are bundled. Footer back-to-top links are removed; the introduction has Explore my work and Get in touch buttons.

Voron and Analog Swerve use full-width photo frames (380 px main photos, 300 px gallery photos on desktop), with `object-fit: cover` and per-photo focal positions. This crops rather than stretches the source; the image viewer retains the entire original.

## Impulse-inspired design branch

This checkout is on `design/impulse-nord`. It replaces the sidebar presentation with a horizontal header, cinematic Formula-car hero, selected-work image panels, and larger section typography, while retaining the Nord palette, rounded rectangles, project content, and local image assets. The reference is https://www.impulsespace.com/; no reference-site artwork, text, or source code is copied.

Preview this checkout independently:

```sh
cd /home/Turquoisee/portfolio/release/impulse-nord
python3 -m http.server 8001 --bind 127.0.0.1
```

The original checkout can simultaneously run on port 8000:

```sh
cd /home/Turquoisee/portfolio
python3 -m http.server 8000 --bind 127.0.0.1
```

Open http://localhost:8001 for this variant and http://localhost:8000 for the original. Each server must serve its own checkout, not just use a different port in the same directory. This is an isolated Git checkout under the ignored `release/` directory. To import its branch into the original repository:

```sh
cd /home/Turquoisee/portfolio
git fetch /home/Turquoisee/portfolio/release/impulse-nord design/impulse-nord:design/impulse-nord
```

You can then create a durable worktree at a location of your choice. The branch has not been pushed or deployed; the production workflow triggers only on pushes to `main`.
