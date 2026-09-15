# API Coverage — Phase 190: Endpoints That Do Not Depend on a Redirect

The deterministic detector returned `detected: false` (no signals) at plan time. This matrix is
recorded anyway, for two reasons: the seal-time re-detection (`api-coverage.verify-pre`) runs over
the plan bodies, which necessarily contain `api`, `endpoint` and `consume`; and unlike Phase 189,
this phase **genuinely does consume an external API** — the GitHub Releases REST API, at three
endpoints, through `firestarter_app/firestarter/firmware.py`. Declaring "no external API
integration" here would be false.

**What this phase does to that consumption:** it repoints the three endpoint constants from
`henols/firestarter` to `henols/firestarter_fw`, and it makes a failed fetch distinguishable from an
empty result. It adds **no new capability** against the API. The matrix below is therefore mostly a
record of what was already integrated and what was already, deliberately, left out — the subtraction
record, per the checkpoint's own framing.

`INTEGRATE` is the default. Every `OPT-OUT` carries a one-line reason.

| Capability | INTEGRATE / OPT-OUT | Reason |
|---|---|---|
| `GET /repos/{owner}/{repo}/releases/latest` | INTEGRATE | `FIRESTARTER_RELEASE_URL`; the stable channel. Repointed by URL-01. |
| `GET /repos/{owner}/{repo}/releases` (list, paginated) | INTEGRATE | `FIRESTARTER_RELEASES_URL`; the `--pre` channel and `fw --list`. Repointed by URL-01. |
| `GET /repos/{owner}/{repo}/releases/tags/{tag}` | INTEGRATE | `FIRESTARTER_RELEASE_BY_TAG_URL`; the `--firmware-version` pinned channel. Repointed by URL-01. |
| Link-header pagination (`rel="next"`) | INTEGRATE | Already implemented in `_fetch_all_releases`, capped at 5 pages. Unchanged here. |
| Release asset download (`browser_download_url`) | INTEGRATE | `_download_firmware_file`; exercised live by the D-14 check-3 evidence leg. |
| Redirect transparency (`response.history`) | INTEGRATE | The single observable that distinguishes "addresses `firestarter_fw`" from "followed a 301". The whole point of URL-01; asserted by the D-16 evidence script. |
| `GET /repos/{owner}/{repo}/releases/{release_id}` | OPT-OUT | The app never holds a numeric release id; every lookup is by channel or by tag. |
| `GET /repos/{owner}/{repo}/releases/{id}/assets` (list assets) | OPT-OUT | Assets are already embedded in the release payload; a second round trip would add nothing. |
| Create / update / delete a release | OPT-OUT | The host CLI is a read-only consumer; releases are published by the firmware repository's own CI. |
| Upload / update / delete a release asset | OPT-OUT | Same reason — write operations against the firmware repository are out of the CLI's remit. |
| Generate release notes | OPT-OUT | The CLI renders version, channel, publish date and asset URL; release prose is not consumed anywhere. |
| Release reactions | OPT-OUT | No use case; the CLI has no social surface. |
| Authenticated requests (token, higher rate limit) | OPT-OUT | The repository is public and the API is used unauthenticated by design — `Auth: None — public API, no token required`. Introducing a token would create a secret where none exists. |
| Conditional requests / ETag caching | OPT-OUT | `fw` is an interactive, occasional command; the unauthenticated rate limit has never been a constraint. Adding a cache would create staleness in exactly the check whose job is to be fresh. |
| Rate-limit headers (`X-RateLimit-*`) | OPT-OUT | Not read today. A 403 from rate limiting already surfaces through the `RequestException` arm, which this phase makes visible rather than silent. |
| Asset provenance verification (signature / checksum) | OPT-OUT | Pre-existing gap, recorded in the threat model of `190-04` as accepted, not mitigated. The Releases API exposes no signature for these assets, and adding one is a firmware-release-process change, not a host change. |
| GraphQL release queries | OPT-OUT | `requests` against the REST API is the incumbent; a second client for the same data is not justified. |
