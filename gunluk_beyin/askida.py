"""Suspend a channel's brain while its concept is being rewritten.

Why a suspension is not just "skip the run": the channel agent reads
`kanallar/<channel>/BEYIN.md` every day and does not know the brain stopped.
Leaving yesterday's file in place keeps selling advice derived from a concept
that no longer exists, which is exactly what a suspension is meant to prevent.
So suspending REPLACES the report with a notice, and the previous report is
kept beside it as `BEYIN-askidan-onceki.md` rather than thrown away.

The suspension carries an end date and expires on its own. An indefinite
suspension is allowed (`--kadar acik`) for when the restart date is unknown;
it has to be lifted by hand with `devam`.
"""
import json
import os
from datetime import datetime, timedelta, timezone

STATE_FILE = "askida.json"
REPORT_FILE = "BEYIN.md"
ARCHIVED_REPORT = "BEYIN-askidan-onceki.md"

OPEN_ENDED = "acik"


def _now():
    return datetime.now(timezone.utc)


def state_path(channel_dir):
    return os.path.join(channel_dir, STATE_FILE)


def parse_until(text):
    """'2026-09-20' or 'acik' -> ISO string or None. Raises ValueError."""
    text = (text or "").strip()
    if text.lower() == OPEN_ENDED:
        return None
    try:
        parsed = datetime.strptime(text, "%Y-%m-%d")
    except ValueError:
        raise ValueError(
            "tarih YYYY-AA-GG olmali ya da 'acik' yazilmali. -> %r" % text)
    # End of that day UTC: a suspension "until the 20th" should include the 20th.
    return parsed.replace(hour=23, minute=59, second=59,
                          tzinfo=timezone.utc).isoformat()


def until_from_days(days):
    if days < 1:
        raise ValueError("gun sayisi en az 1 olmali. -> %r" % days)
    return (_now() + timedelta(days=days)).isoformat()


def write_state(channel_dir, until_iso, reason):
    """Atomic. A half-written suspension file would read as 'not suspended'."""
    os.makedirs(channel_dir, exist_ok=True)
    record = {
        "askiya_alindi": _now().isoformat(),
        "kadar": until_iso,          # None = acik uclu
        "sebep": reason or "",
    }
    path = state_path(channel_dir)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(record, fh, ensure_ascii=False, indent=1)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)
    return record


def read_state(channel_dir):
    """Return (record, active). `active` is False for an expired suspension.

    A broken or unreadable file is treated as NOT suspended, deliberately: the
    failure mode of a silently suspended channel is worse than an extra run.
    """
    try:
        with open(state_path(channel_dir), encoding="utf-8") as fh:
            record = json.load(fh)
    except Exception:
        return None, False
    if not isinstance(record, dict):
        return None, False
    until = record.get("kadar")
    if until is None:
        return record, True
    try:
        deadline = datetime.fromisoformat(str(until))
    except ValueError:
        return record, True          # okunamayan tarih = hala askida, sessizce acilmasin
    if deadline.tzinfo is None:
        deadline = deadline.replace(tzinfo=timezone.utc)
    return record, _now() < deadline


def clear_state(channel_dir):
    try:
        os.remove(state_path(channel_dir))
        return True
    except OSError:
        return False


def describe(record):
    """Human line for the log, always in the user's language."""
    until = record.get("kadar")
    when = "acik uclu (elle kaldirilmali)" if until is None else str(until)[:16].replace("T", " ") + " UTC"
    sebep = record.get("sebep") or "belirtilmemis"
    return "%s , sebep: %s" % (when, sebep)


def notice_text(channel, record):
    """The BEYIN.md that stands in for the real report while suspended."""
    until = record.get("kadar")
    when = ("acik uclu , elle kaldirilana kadar"
            if until is None else str(until)[:10] + " (UTC gun sonu)")
    lines = [
        "# %s , ASKIDA" % channel,
        "",
        "**Bu kanalin beyni %s tarihine kadar askiya alindi.**" % when,
        "",
        "Sebep: %s" % (record.get("sebep") or "belirtilmemis"),
        "",
        "## Bu dosyada bugun icin YON YOKTUR",
        "",
        "Onceki olcumler bu kanalin ESKI konseptine aittir. Yeni format icin",
        "yol gosterici degildir; kor uygularsan yeni konsepti eskisine benzetirsin.",
        "",
        "- Eski rapor silinmedi: `%s` dosyasinda duruyor." % ARCHIVED_REPORT,
        "  Merak edersen oku, ama **oradan hedef alma**.",
        "- Aski kalkinca beyin sifirdan yazacak.",
        "- Yeni formatin ilk videosu, yayindan **24 saat sonraki** kosuda olculur.",
        "  Yani yayin gunu degil, ertesi gunku raporda gorunur.",
        "",
        "Askiyi kaldirmak icin:",
        "",
        "```",
        "python beyin.py devam %s" % channel,
        "```",
        "",
        "_Askiya alindi: %s_" % str(record.get("askiya_alindi", ""))[:16].replace("T", " "),
        "",
    ]
    return "\n".join(lines)


def install_notice(channel, channel_dir, record):
    """Put the notice in place of BEYIN.md, keeping the old report beside it.

    Returns True if a previous report was archived.
    """
    os.makedirs(channel_dir, exist_ok=True)
    report = os.path.join(channel_dir, REPORT_FILE)
    archived = False
    if os.path.exists(report):
        with open(report, encoding="utf-8", errors="replace") as fh:
            previous = fh.read()
        # Do not archive a notice over a notice: re-suspending twice would
        # otherwise destroy the only real report we kept.
        if not previous.lstrip().startswith("# %s , ASKIDA" % channel):
            with open(os.path.join(channel_dir, ARCHIVED_REPORT), "w",
                      encoding="utf-8") as fh:
                fh.write(previous)
            archived = True
    tmp = report + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(notice_text(channel, record))
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, report)
    return archived
