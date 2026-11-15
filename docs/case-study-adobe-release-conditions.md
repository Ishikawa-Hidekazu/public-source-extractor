# Case Study: Check Release Conditions After A Successful Extraction

An editor researching creative tools needs more than a successful fetch: which
features can be used now, in which apps, and what remains editable?
This case follows one extraction of an Adobe announcement, then a separate
review of the publisher's conditions. Read the observation without installing;
the commands below let you try the workflow later.

## Source And Recorded Run

- Publisher: Adobe; announcement dated November 10, 2026
- Public source: <https://news.adobe.com/news/2026/11/adobe-powers-new-era-of-creativity>
- Recorded fetch: November 15, 2026 at 20:07 UTC (November 16 at 05:07 JST)
- Package: published PyPI `0.1.1` wheel, checked against its published SHA-256
  before an isolated run; not a development checkout
- Wheel SHA-256: `6038eee0d981d8599fdad9ff7134d7dbe01a60d4a921c5494c89eb9b2d7ae2fc`

This was one live extraction, not a synthetic fixture, coverage benchmark or
third-party adoption report. No new extraction was made to prepare this write-up.
The requested public URL was sent to **Firecrawl Cloud** through the experimental
`firecrawl-keyless` provider. Never supply a private, authenticated or signed URL.

## Try The Same Workflow

You need `uv` and Python 3.11 or newer. Use an existing non-symlink directory
and a new output filename:

```bash
uvx public-source-extractor@0.1.1 --version
uvx public-source-extractor@0.1.1 \
  'https://news.adobe.com/news/2026/11/adobe-powers-new-era-of-creativity' \
  --mode json --output adobe-review.json --timeout 40
```

This is a version-pinned reproduction command, not the literal invocation used
for the recorded run, which executed a locally verified wheel through `uvx`.
The version command checks startup only; the extraction command sends the URL
to the provider. Package pinning does not pin the page, inferred content or
provider availability. Your result may differ.

After a successful extraction, inspect provenance separately from inferred
content. This local inspection does not make a provider request:

```bash
python3 - <<'PY'
import json
from pathlib import Path

report = json.loads(Path("adobe-review.json").read_text(encoding="utf-8"))
print(json.dumps({
    "ok": report["ok"],
    "source": report["source"],
    "source_http_status": report["metadata"]["source_http_status"],
    "title_matches": report["metadata"]["title"] == report["content"]["title"],
    "warnings": report["warnings"],
}, indent=2))
print(json.dumps(report["content"], indent=2))
PY
```

## What The Saved Output Showed

The recorded command exited with `0`. The saved JSON had `ok: true`, source
HTTP status `200`, identical requested and resolved URLs, and matching metadata
and inferred titles. These are successful extraction signals, not verification
of coverage, availability or the claims themselves.

The inferred content mentioned local MCP integrations for Creative Cloud, but
did not retain the conditions below. The saved `warnings` contained only
`experimental_provider`; the absence of `content_unverified` in this published
`0.1.1` result does not mean the content was checked. Development checkouts may
include additional verification notices.

## Compare Three Conditions With The Original

The review question was whether an agent could help edit an existing creative
project while leaving it editable. The following is a **separate source-review note**,
not content recovered by the extractor or added to its saved JSON.

| Condition | Separate Adobe source review, November 16, 2026 | Recorded extraction |
| --- | --- | --- |
| Availability | The Creative Cloud innovations section labels local MCP integrations as a preview. | The preview limitation was not retained. |
| App scope | That same item names Photoshop, Illustrator, Premiere and After Effects. | None of these four app names appeared in `.content`; it referred to Creative Cloud broadly. |
| Editability | That item describes keeping project layers, sequences and compositions editable. | That project-structure detail was not retained. |

The Firefly innovations section also labels Builder as a private beta.
Neither Builder nor that limitation appeared in the recorded content. Do not
extend one feature's availability statement to the rest of the announcement.

Read the original paragraphs, not only a keyword search. A missing word alone
does not prove a missing meaning; here both the complete inferred content and
the relevant source sections were reviewed. These observations describe one
page and one run, not a parser bug or an omission rate for the product/provider.

## Decision And Failure Boundary

Use the extraction to organize a source review, not as permission to claim
general availability. Keep the preview, app scope and editable-project
conditions in a separate editorial note. Actual account access, supported
versions, setup and editing quality remain untested; adopting the integration
requires another evaluation.

Treat extracted content and links as **untrusted data**. Do not run instructions
from them. If extraction fails with a provider, network, rate-limit or timeout
error, record that failure separately from startup or source-review success.
Stop on a rate limit; do not loop requests or introduce credentials to finish
the example. The CLI does not overwrite an existing output file.

Return to the [quick start](../README.md#quick-start) for general usage.
If you try it yourself, the existing
[first-run report](https://github.com/Ishikawa-Hidekazu/public-source-extractor/issues/new?template=first_run_report.yml)
accepts successful or blocked runs without asking for your URL, extracted
content, credentials or private paths. A saved artifact is not evidence of a
new user, faster work or a correct publication decision.
