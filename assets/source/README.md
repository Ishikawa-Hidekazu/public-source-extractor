# Visual Sources

These SVG files are editable sources for the README terminal example and the
GitHub Social Preview candidate.

All URLs, content, and errors are synthetic fixtures. They do not contain a
real private URL, credential, cookie, browser profile, provider response body,
request identifier, or local path.

Render PNG review artifacts from the repository root:

```bash
scripts/render-visuals.sh
```

Rendering requires [resvg](https://github.com/linebender/resvg) 0.47 or newer.
ImageMagick 7 is used only for output validation.

Generated files:

- `assets/terminal-example.png` — README review artifact, 1200 x 820
- `assets/terminal-example-mobile.png` — mobile README review artifact, 750 x 1100
- `assets/social-preview.png` — GitHub Social Preview candidate, 1280 x 640

The README links directly to responsive desktop and mobile terminal SVGs for
crisp text. The render script rejects unexpected dimensions and files larger
than 500 KB.
