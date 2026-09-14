#!/usr/bin/env bash
#
# firestarter PyPI per-version download share.
#
# Reports, for the `firestarter` PyPI package, the split between downloads of
# a fixed stable version (>= 2.0.9) and downloads of the at-risk stable
# version (2.0.7 exactly), restricted to the pip and uv installers over a
# rolling 90-day window. Prints a threshold verdict, then unconditionally
# prints what the reading does not and cannot measure.
#
# Authoritative source: the ClickHouse public PyPI download dataset, table
# pypi.pypi_downloads_per_day_by_version_by_installer_by_type, queried
# read-only and without credentials at https://sql-clickhouse.clickhouse.com/
# (user "play"). Fixed leg: any stable version array >= [2, 0, 9]. At-risk
# leg: the exact stable version 2.0.7.
#
# Recorded fallbacks, not built here, if this endpoint stops answering:
#   - PyPI's BigQuery public dataset (bigquery-public-data.pypi) — same
#     per-version, per-installer granularity, but requires a GCP account.
#   - The raw pypi.pypi_raw table on this same ClickHouse playground — the
#     same underlying events, unaggregated, far more expensive to query.
#
# Takes no arguments, reads no other file, and writes nothing to disk.
#
# Requirements: bash, curl

set -euo pipefail

ENDPOINT="https://sql-clickhouse.clickhouse.com/"

QUERY="$(cat <<'SQL'
SELECT
  today() AS ch_today,
  today() - 90 AS window_start,
  max(date) AS window_end,
  count() AS rows_matched,
  sumIf(count, arrayMap(x -> toUInt32OrZero(x), splitByChar('.', version)) >= [2, 0, 9]) AS fixed,
  sumIf(count, version = '2.0.7') AS at_risk,
  round(100 * fixed / nullIf(fixed + at_risk, 0), 1) AS fixed_share_pct,
  (fixed + at_risk) > 0
    AND fixed * 10 >= 9 * (fixed + at_risk)
    AND at_risk <= 10 AS trigger_met
FROM pypi.pypi_downloads_per_day_by_version_by_installer_by_type
WHERE project = 'firestarter'
  AND date >= today() - 90
  AND installer IN ('pip', 'uv')
  AND NOT match(version, '(a|b|rc)[0-9]|dev')
FORMAT TSVWithNames
SQL
)"

print_fallbacks() {
    echo "  Fallback 1: PyPI's BigQuery public dataset (bigquery-public-data.pypi) — same granularity, needs a GCP account." >&2
    echo "  Fallback 2: the raw pypi.pypi_raw table on this same playground — same events, unaggregated, far more expensive to query." >&2
}

if ! body="$(curl -s \
    --max-time 90 \
    --fail-with-body \
    -G "$ENDPOINT" \
    --data-urlencode "user=play" \
    --data-urlencode "query=$QUERY")"; then
    echo "ERROR: the ClickHouse query failed:" >&2
    echo "$body" >&2
    print_fallbacks
    exit 1
fi

data_line="$(printf '%s\n' "$body" | tail -n +2)"

IFS=$'\t' read -r ch_today window_start window_end rows_matched fixed at_risk fixed_share_pct trigger_met <<< "$data_line"

if [ "$rows_matched" = "0" ]; then
    echo "ERROR: the query succeeded and matched no rows in the window — no verdict printed" >&2
    exit 2
fi

if [ "$trigger_met" = "1" ]; then
    trigger_line="TRIGGER: MET"
else
    trigger_line="TRIGGER: NOT MET"
fi

if [ "$fixed_share_pct" = '\N' ] || [ -z "$fixed_share_pct" ]; then
    display_share="unmeasured"
else
    display_share="$fixed_share_pct"
fi

echo "window: ${window_start} .. ${window_end} (rolling 90 days ending at the table's latest date, UTC, stable channel, installer pip and uv)"
echo "fixed_downloads_ge_2_0_9: ${fixed}"
echo "at_risk_downloads_2_0_7: ${at_risk}"
echo "fixed_share_pct: ${display_share}"
echo "threshold: fixed share >= 90% AND at-risk (2.0.7) downloads <= 10, both over the window above"
echo "$trigger_line"

echo "WHAT THIS DOES NOT MEASURE"
echo "  - Installed base is not observable. Download share is a proxy for it, not a census of it."
echo "  - A download of a stranded version today is a NEW ACQUISITION of an old version — a pin,"
echo "    a cache, or a stale tutorial someone is following right now."
echo "  - A user who installed 2.0.7 and never reinstalls generates zero downloads and is invisible"
echo "    to every instrument considered, including this one."
echo "  - This threshold therefore certifies that new acquisition of stranded versions has"
echo "    effectively stopped — a necessary condition, never a sufficient one."
echo "  - The pre-2.0.7 population is outside the instrument's reach entirely: down there, a"
echo "    stranded human and an automated scanner cannot be told apart."
