# API Coverage — Phase 193: The Deferred Claim, Made Measurable

> Full coverage by default. Opt-outs are explicit, reasoned decisions.

The deterministic detector returned `detected: false` (no signals) when run at plan time over the
ROADMAP's Phase 193 section. The matrix is recorded anyway, for the reason Phase 191 recorded one:
the seal-time re-detection runs over the plan bodies, which necessarily contain `endpoint`, `api`
and `consume`; and this phase genuinely **does** consume an external service, so a bare "no external
API integration" declaration would be false.

**One external surface is consumed and none is built against:** the **ClickHouse public playground**
at `https://sql-clickhouse.clickhouse.com/`, user `play`, no credentials, serving the public PyPI
download dataset. `tools/adoption/pypi_version_share.sh` issues exactly one `GET`-style query against
it per run and renders the result. It writes nothing, authenticates as nobody, and holds no state.

Two further surfaces were evaluated and **rejected as instruments** during discussion, so they carry
no rows of their own — they are recorded in the fallback table at the end: `pypistats.org` (no
per-version endpoint at all, so it cannot satisfy GATE-01) and GitHub release-asset download counts
(cumulative only, no time series, no client-version dimension — research question Q4 answered "no").

`INTEGRATE` is the default. Every `OPT-OUT` carries a one-line reason.

## ClickHouse HTTP interface — as consumed by `tools/adoption/pypi_version_share.sh`

| capability | decision | reason |
|---|---|---|
| Query via query-string parameters (`curl -G` + `--data-urlencode`) | INTEGRATE | The whole instrument. `user=play` must arrive as a query-string parameter; sent in a POST body, ClickHouse falls back to the `default` user and answers `Code: 194 … Authentication failed`. |
| `FORMAT TSVWithNames` output | INTEGRATE | A header row plus one data row, parseable with `read -r` in shell with no JSON dependency. |
| Server-error surfacing via HTTP status (`curl --fail-with-body`) | INTEGRATE | Returns exit 22 **and** prints the server's own `Code: NN … DB::Exception` message, so a failed query cannot render as a verdict. |
| Request timeout (`curl --max-time`) | INTEGRATE | Bounds the single outbound call so an unreachable endpoint fails instead of hanging. |
| Query via POST body | OPT-OUT | The credential parameter is read from the query string only; a POST body would silently authenticate as the wrong user. |
| `FORMAT JSON` / `JSONEachRow` / `Pretty*` | OPT-OUT | Would add a JSON parser to a `bash`-and-`curl`-only tool for no gain; the result is one row of scalars. |
| Authentication (`user`/`password` pair, `X-ClickHouse-Key` header) | OPT-OUT | The `play` user takes no credentials by design. Introducing a token would create a secret where none exists and a rotation obligation where none exists. |
| Per-query settings (`max_execution_time`, `max_result_rows`, …) | OPT-OUT | The query aggregates a single project over 90 days; the defaults are ample and a tuned setting would be an unexplained constant in the file. |
| Sessions (`session_id`, `session_timeout`) | OPT-OUT | One stateless request per run; there is no second query to share state with. |
| HTTP compression (`enable_http_compression`, `Accept-Encoding`) | OPT-OUT | The response is two lines. |
| Progress in HTTP headers (`send_progress_in_http_headers`) | OPT-OUT | The call completes in under a second; a progress channel would be dead code. |
| Query cancellation / `replace_running_query` | OPT-OUT | The script issues one query and exits; there is nothing to cancel or supersede. |
| `INSERT`, DDL, mutations | OPT-OUT | The instrument is a read-only consumer of a public dataset, and the `play` user is read-only by design. |
| `/ping`, `/replicas_status` health endpoints | OPT-OUT | A health or staleness gate was explicitly offered and declined (D-01). A minimal "did the query return rows" guard rides **inside** the query as a `count()` column instead. |
| Named/prepared query parameters (`param_<name>`) | OPT-OUT | The query is a fixed literal with nothing interpolated, which is also the mitigation for the injection threat in the plan's register. Adding a parameter surface would create the hole. |

## The PyPI dataset — table and dimension coverage

| capability | decision | reason |
|---|---|---|
| `pypi.pypi_downloads_per_day_by_version_by_installer_by_type` | INTEGRATE | The only table carrying both dimensions GATE-01 needs — per-version **and** per-installer — at daily resolution. |
| `version` dimension | INTEGRATE | The numerator is any stable version array `>= [2,0,9]`, computed; the denominator is `2.0.7` exactly. |
| `installer` dimension | INTEGRATE | Both legs filter `IN ('pip','uv')`. Unfiltered, the traffic is 3.2% `pip` against a mirror-dominated remainder, and the gate would fire when a mirror finished re-scanning. |
| `date` dimension | INTEGRATE | The rolling 90-day window, and the realised window reported in the output. |
| `type` dimension (sdist vs bdist_wheel) | OPT-OUT | Not needed. A download is a download for adoption purposes, and splitting it would halve every cell without changing the verdict. |
| Sibling table: downloads by country | OPT-OUT | Geography has no bearing on whether a stranded version is still being acquired. |
| Sibling table: downloads by Python version | OPT-OUT | The gate keys on the package version installed, not on the interpreter running it. |
| Sibling table: downloads by system | OPT-OUT | Operating system is orthogonal to the trigger. |
| `pypi.pypi_raw` (unaggregated source table) | OPT-OUT | Recorded as a fallback route rather than built (D-03). Same data, far more expensive to query, and a second code path never exercised until the day it is needed is a path that fails on that day. |
| Cross-project comparison | OPT-OUT | Explicitly out of scope — the trigger concerns one package. |

## Rejected and recorded fallbacks — not built

| capability | decision | reason |
|---|---|---|
| PyPI BigQuery (`bigquery-public-data.pypi.file_downloads`) | OPT-OUT | Per-version and per-installer, so it *could* serve — but it needs a GCP account. Recorded in the instrument's own header as the route for whoever meets a dead endpoint (D-03), deliberately not built. |
| `pypistats.org` API | OPT-OUT | Has no per-version endpoint at all, so it cannot satisfy GATE-01. Recorded as evaluated and rejected. |
| GitHub release-asset download counts | OPT-OUT | Cumulative only, no time series, no client-version dimension — verified against the firmware repository's releases, whose assets read 0 to 2 downloads each. Research question Q4 answered "no". |
| A scheduled run of the instrument | OPT-OUT | Would need a `.github/workflows/` the meta repository does not have, to put a recurring job behind a gate that will be evaluated a handful of times at most. Deferred at discussion time. |

## Package legitimacy

**Not applicable.** This phase installs no external package in any ecosystem. The instrument's only
dependencies are the pre-existing system `bash` (5.2.37) and `curl` (8.14.1); nothing is added to
`package.json`, `pyproject.toml` or `Cargo.toml`, and no plan in the phase runs a package-manager
install.
