"""ISO 8601 timestamps in CET (UTC+01:00), or CEST (UTC+02:00) during EU
summer time. Summer time starts on the last Sunday of March and ends on the
last Sunday of October, at 01:00 UTC both times. stdlib only.

The rule is computed here because the devcontainer has no tz database, so
`zoneinfo` cannot load a zone. The app has the same rule in
`firestarter/timestamps.py`. A skill owns its scripts, so this file is a copy,
not an import.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta, timezone

_CET = timezone(timedelta(hours=1), "CET")
_CEST = timezone(timedelta(hours=2), "CEST")


def _last_sunday_0100_utc(year: int, month: int) -> datetime:
    """01:00 UTC on the last Sunday of `month` (March or October, both 31 days)."""
    last_day = datetime(year, month, 31, 1, tzinfo=UTC)
    return last_day - timedelta(days=(last_day.weekday() + 1) % 7)


def to_cet(moment: datetime) -> datetime:
    """`moment` converted to CET or CEST. Raises ValueError when it is naive."""
    if moment.tzinfo is None:
        raise ValueError("to_cet() needs a timezone-aware datetime")
    year = moment.astimezone(UTC).year
    summer = _last_sunday_0100_utc(year, 3) <= moment < _last_sunday_0100_utc(year, 10)
    return moment.astimezone(_CEST if summer else _CET)


def parse_cet(text: str | None) -> datetime | None:
    """Parse an ISO 8601 timestamp that has an offset (`...Z` or `...+02:00`)
    and return it in CET. Returns None when `text` is empty, does not parse,
    or has no offset: a time without a zone cannot be ordered.
    """
    try:
        moment = datetime.fromisoformat(text or "")
    except ValueError:
        return None
    return to_cet(moment) if moment.tzinfo is not None else None


def cet_text(text: str | None) -> str:
    """`text` re-expressed as ISO 8601 in CET, e.g. `2026-08-07T14:07:39+02:00`.
    Returns `text` unchanged (or "" for None) when it does not parse.
    """
    moment = parse_cet(text)
    return moment.isoformat(timespec="seconds") if moment else (text or "")
