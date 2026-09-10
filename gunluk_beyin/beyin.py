"""Daily learning brain.

Accumulates MEASUREMENTS and OUTCOMES of published videos per channel into a
ledger, then reads that ledger and writes a channel-specific BEYIN.md. The
channel agent reads that file every day to shape the next idea.

No static idea pool. The brain is rewritten every day from measured outcomes.

    python beyin.py olc   <channel>   measure new uploads, append to ledger
    python beyin.py topla <channel>   refresh view counts (time series)
    python beyin.py beyin <channel>   read ledger, write BEYIN.md

Channel slugs: unnatural-lab, event-horizon, flashpoints, aimagine-fear

Note on language: identifiers and comments are English; user-facing strings
(the report body and log lines) stay Turkish because Ihsan and the channel
agents read them.
"""
import argparse
import json
import os
import statistics as st
import sys
import tempfile
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.join(ROOT, "arac")

# Channel ids. Keep in sync with kanallarimiz.md.
CHANNELS = {
    "unnatural-lab": "UC-Aht8VqAUMTUKYRQA3agYQ",
    "event-horizon": "UCVCRWrQYrIHW6csOsw9bDNw",
    "flashpoints": "UCUdp0KLBh4EeeSgVbwS_DhA",
    "aimagine-fear": "UCCgbHTzYKYawUT6zEo0nlDg",
}

# Minimum ledger size before we derive any channel-specific rule.
# Below this we claim NOTHING and fall back to the general thresholds.
MIN_SAMPLES = 15

# A video is not measured until it is at least this old. Ihsan, 2026-09-10:
# "stay one day behind, then we see where the views actually land."
# A fresh video has near-zero views; ranking on it corrupts the comparison.
MIN_AGE_HOURS = 24.0

# Age-fair comparison window: prefer the view count around hour 24. Current
# view counts unfairly compare a 30-day-old video against a 2-day-old one.
AGE_WINDOW_LOW = 20.0
AGE_WINDOW_HIGH = 48.0

# Below this relative gap between the two halves it is NOISE, not a direction.
# Measured example: event-horizon duration 16.54 vs 16.52 s was reported as
# "upper half HIGHER" and section 4 said "target 16.54s". Useless advice.
MIN_RELATIVE_GAP = 0.10

# Fields compared between halves: (ledger key, display name, unit)
FIELDS = [
    ("sure", "sure", "sn"),
    ("kesme_per_10sn", "kesme / 10 sn", ""),
    ("en_uzun_plan", "en uzun plan", "sn"),
    ("lufs", "ses seviyesi (LUFS)", ""),
]
EXTRA_FIELDS = [("wpm", "konusma hizi (WPM)", ""), ("kelime", "kelime sayisi", "")]

GENERAL_THRESHOLDS = """- Integrated loudness hedefi: **-16 ila -13 LUFS**
- True peak tavani: **-1,0 dBTP** (ustu platform yeniden kodlamasinda bozulur)
- En uzun tek plan: **4 saniyeyi asmasin**
- Kesme araligi: **1,5-3 saniye**, pattern interrupt her 5-7 saniyede
- Ilk 1,5 saniyede ekran yazisi: **3-7 kelime**, ust-orta ucte bir, dip %15 yasak
- Sure: nis ici olcumde **kisa kazaniyor** (0-7 sn en iyi 1,69x; 90+ sn en kotu 0,65x)
- Sinyal sirasi: skip rate (ilk 3 sn) > shares > likes > saves > reposts > comments
- **Yorum orani begeni oranindan daha ayirt edici** (begeni skor dilimleri arasi sabit)"""


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def channel_dir(channel, root=None):
    return os.path.join(root or os.getcwd(), "kanallar", channel)


def ledger_path(channel, root=None):
    return os.path.join(channel_dir(channel, root), "defter.jsonl")


def read_ledger(channel, root=None):
    """Skip malformed lines instead of crashing. Returns (rows, skipped)."""
    path = ledger_path(channel, root)
    rows, skipped = [], 0
    if not os.path.exists(path):
        return rows, skipped
    with open(path, encoding="utf-8", errors="replace") as fh:
        for raw in fh:
            raw = raw.strip()
            if not raw:
                continue
            try:
                row = json.loads(raw)
            except Exception:
                skipped += 1
                continue
            if isinstance(row, dict) and row.get("video_id"):
                rows.append(row)
            else:
                skipped += 1
    return rows, skipped


def write_ledger(channel, rows, root=None):
    path = ledger_path(channel, root)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def as_number(value):
    """Real numbers only. None, bool and strings are rejected."""
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def field(row, name):
    """Look inside 'olcum' first, then at the row root."""
    measured = row.get("olcum")
    if isinstance(measured, dict) and name in measured:
        return as_number(measured.get(name))
    return as_number(row.get(name))


def views(row):
    outcome = row.get("sonuc")
    if isinstance(outcome, dict):
        value = as_number(outcome.get("izlenme"))
        if value is not None:
            return value
    return as_number(row.get("rss_izlenme"))


def views_at_24h(row):
    """View count around hour 24, or None."""
    outcome = row.get("sonuc")
    if isinstance(outcome, dict):
        return as_number(outcome.get("izlenme_24s"))
    return None


def age_hours(row_or_ts):
    """Hours since publication, or None if unparseable.

    Prefers the full timestamp (yayin_ts). Falls back to the date-only field,
    which OVERSTATES age because it counts from midnight; accepted knowingly
    since older ledger rows predate yayin_ts.
    """
    if isinstance(row_or_ts, dict):
        raw = row_or_ts.get("yayin_ts") or row_or_ts.get("tarih")
    else:
        raw = row_or_ts
    if not raw:
        return None
    text = str(raw).strip()
    if len(text) == 10:
        text += "T00:00:00+00:00"
    text = text.replace("Z", "+00:00")
    try:
        published = datetime.fromisoformat(text)
    except Exception:
        return None
    if published.tzinfo is None:
        published = published.replace(tzinfo=timezone.utc)
    return round((datetime.now(timezone.utc) - published).total_seconds() / 3600, 1)


def derive_24h_views(row):
    """Pick the snapshot closest to hour 24 from the time series."""
    outcome = row.get("sonuc")
    if not isinstance(outcome, dict):
        return None
    best = None
    for snapshot in outcome.get("gecmis") or []:
        age = as_number(snapshot.get("yas_saat"))
        count = as_number(snapshot.get("izlenme"))
        if age is None or count is None:
            continue
        if not (AGE_WINDOW_LOW <= age <= AGE_WINDOW_HIGH):
            continue
        if best is None or abs(age - 24.0) < abs(best[0] - 24.0):
            best = (age, count)
    return best[1] if best else None


# ------------------------------------------------------------------ measure

def cmd_measure(channel, limit=15):
    if channel not in CHANNELS:
        sys.exit("Bilinmeyen kanal: %s\n  Gecerli: %s"
                 % (channel, ", ".join(sorted(CHANNELS))))
    sys.path.insert(0, TOOLS)
    try:
        from kanal import youtube_rss
        from olc import tek as measure_one
    except Exception as exc:
        sys.exit("arac/ modulleri yuklenemedi: %s" % exc)

    rows, _ = read_ledger(channel)
    known = {row["video_id"] for row in rows}
    feed = youtube_rss(CHANNELS[channel], limit)
    candidates = [v for v in feed if v["video_id"] not in known]

    # 24-hour gate: fresh videos are NOT measured, they arrive tomorrow.
    # Their view count is near zero, which would corrupt any ranking.
    due, held = [], []
    for video in candidates:
        age = age_hours(video)
        if age is not None and age < MIN_AGE_HOURS:
            held.append((video, age))
        else:
            due.append(video)

    print("kanal: %s  |  RSS: %d  |  defterde yok: %d  |  olculecek: %d"
          % (channel, len(feed), len(candidates), len(due)))
    for video, age in held:
        print("  BEKLETILDI (%.1f saat < %.0f): %s  %s"
              % (age, MIN_AGE_HOURS, video["video_id"],
                 (video.get("baslik") or "")[:38]))
    if not due:
        print("olculecek video yok.")
        return

    workdir = os.path.join(tempfile.gettempdir(), "gunluk-beyin")
    os.makedirs(workdir, exist_ok=True)

    for video in due:
        vid = video["video_id"]
        print("  olculuyor: %s  %s" % (vid, (video.get("baslik") or "")[:44]))
        try:
            result = measure_one(
                "https://www.youtube.com/shorts/" + vid, workdir, False)
        except Exception as exc:
            print("    HATA: %s" % exc)
            continue
        if result.get("hata"):
            print("    ATLANDI: %s" % result["hata"])
            continue
        rows.append({
            "video_id": vid,
            "kanal": channel,
            "tarih": video.get("tarih"),
            "yayin_ts": video.get("yayin_ts"),
            "baslik": video.get("baslik"),
            "olcum": result.get("olcum") or {},
            "kelime": result.get("kelime"),
            "wpm": result.get("wpm"),
            "sonuc": {"izlenme": video.get("rss_izlenme"), "begeni": None,
                      "gecmis": []},
            "olculdu_ts": now_iso(),
        })
        write_ledger(channel, rows)
    print("defter: %d kayit -> %s" % (len(rows), ledger_path(channel)))


# ------------------------------------------------------------------ collect

def cmd_collect(channel):
    if channel not in CHANNELS:
        sys.exit("Bilinmeyen kanal: %s" % channel)
    sys.path.insert(0, TOOLS)
    try:
        from kanal import youtube_canli as live_stats
    except Exception as exc:
        sys.exit("arac/kanal.py yuklenemedi: %s" % exc)

    rows, skipped = read_ledger(channel)
    if not rows:
        print("defter bos, once 'olc' calistir.")
        return
    if skipped:
        print("UYARI: %d bozuk satir atlandi." % skipped)

    updated = 0
    for row in rows:
        live = live_stats(row["video_id"]) or {}
        if not live.get("izlenme"):
            continue
        outcome = row.get("sonuc")
        if not isinstance(outcome, dict):
            outcome = {"gecmis": []}
            row["sonuc"] = outcome
        outcome.setdefault("gecmis", [])
        # Append, never overwrite: the time series is the point.
        outcome["gecmis"].append({
            "ts": now_iso(),
            "izlenme": live["izlenme"],
            "yas_saat": age_hours(row),
        })
        outcome["izlenme"] = live["izlenme"]
        if live.get("begeni") is not None:
            outcome["begeni"] = live["begeni"]
        # Once the hour-24 figure is frozen it never changes again.
        if outcome.get("izlenme_24s") is None:
            snapshot = derive_24h_views(row)
            if snapshot is not None:
                outcome["izlenme_24s"] = snapshot
        updated += 1

    write_ledger(channel, rows)
    print("%d/%d kayit guncellendi -> %s"
          % (updated, len(rows), ledger_path(channel)))


# -------------------------------------------------------------------- brain

def _half_gap(upper, lower, name):
    """Return (median_upper, median_lower, n_upper, n_lower, significant)."""
    a = [x for x in (field(r, name) for r in upper) if x is not None]
    b = [x for x in (field(r, name) for r in lower) if x is not None]
    if len(a) < 3 or len(b) < 3:
        return None
    ma, mb = st.median(a), st.median(b)
    scale = max(abs(ma), abs(mb), 1e-9)
    return ma, mb, len(a), len(b), abs(ma - mb) / scale >= MIN_RELATIVE_GAP


def _comparison_row(upper, lower, name, label, unit):
    result = _half_gap(upper, lower, name)
    if result is None:
        return None
    ma, mb, na, nb, significant = result
    if not significant:
        direction = "**anlamli fark yok**"
    elif ma > mb:
        direction = "ust yari DAHA YUKSEK"
    else:
        direction = "ust yari DAHA DUSUK"
    return ("| %s | %.2f%s | %.2f%s | %s | n=%d/%d |"
            % (label, ma, unit, mb, unit, direction, na, nb))


def cmd_brain(channel):
    rows, skipped = read_ledger(channel)
    total = len(rows)
    enough = total >= MIN_SAMPLES

    # Age-fair ranking. Comparing a 30-day-old video to a 2-day-old one on
    # current views is unfair; if most rows carry an hour-24 figure, use it.
    # Otherwise fall back to current views AND SAY SO in the report.
    with_24h = [r for r in rows if views_at_24h(r) is not None]
    if rows and len(with_24h) >= max(3, int(total * 0.8)):
        metric = views_at_24h
        metric_label = "**24. saat izlenmesi** (yas-adil)"
    else:
        metric = views
        metric_label = ("guncel izlenme , _24. saat olcumu henuz %d/%d kayitta "
                        "var, yaslar farkli oldugu icin siralamayi dikkatli oku_"
                        % (len(with_24h), total))

    not_enough = (
        "**YETERSIZ VERI** (n=%d, en az %d gerekiyor). Bu kanala ozel kural "
        "cikarilamaz, asagidaki genel esikler kullanilmali." % (total, MIN_SAMPLES)
    )

    out = []
    out.append("# BEYIN , %s" % channel)
    out.append("")
    out.append("Uretim: %s" % now_iso())
    out.append("Kaynak: `%s` (%d kayit)" % (ledger_path(channel), total))
    if skipped:
        out.append("")
        out.append("> UYARI: defterde %d bozuk satir atlandi." % skipped)
    out.append("")
    out.append("Bu dosya HER GUN yeniden yazilir. Sabit fikir havuzu yoktur.")
    out.append("Sadece **%.0f saatten eski** videolar olculur, boylece izlenmenin"
               % MIN_AGE_HOURS)
    out.append("nerede oturdugu gorulur.")
    out.append("")
    out.append("---")
    out.append("")

    # --- 1. status
    out.append("## 1. DURUM")
    out.append("")
    if total == 0:
        out.append("Defter bos. Once `python beyin.py olc %s` calistir." % channel)
    else:
        counts = [c for c in (metric(r) for r in rows) if c is not None]
        out.append("- Olculen video: **%d**" % total)
        out.append("- Siralama olcusu: %s" % metric_label)
        fresh = [r for r in rows if (age_hours(r) or 999) < MIN_AGE_HOURS]
        if fresh:
            out.append("- _%d video %.0f saatten taze, siralamaya girmiyor._"
                       % (len(fresh), MIN_AGE_HOURS))
        if counts:
            out.append("- Medyan izlenme: **%s**" % "{:,.0f}".format(st.median(counts)))
            out.append("- Aralik: %s ile %s arasi"
                       % ("{:,.0f}".format(min(counts)), "{:,.0f}".format(max(counts))))
            ranked = sorted([r for r in rows if metric(r) is not None],
                            key=lambda r: -metric(r))
            out.append("")
            out.append("| | izlenme | tarih | baslik |")
            out.append("|---|---|---|---|")
            for label, row in (("EN IYI", ranked[0]), ("EN KOTU", ranked[-1])):
                out.append("| %s | %s | %s | %s |"
                           % (label, "{:,.0f}".format(metric(row)),
                              row.get("tarih") or "?",
                              (row.get("baslik") or "?")[:48]))
            out.append("")
            out.append("Son yayinlar (tekrar etme):")
            for row in sorted(rows, key=lambda r: str(r.get("tarih") or ""),
                              reverse=True)[:5]:
                out.append("- %s , %s" % (row.get("tarih") or "?",
                                          (row.get("baslik") or "?")[:60]))
        else:
            out.append("- Izlenme verisi yok. `python beyin.py topla %s` calistir."
                       % channel)
    out.append("")

    # --- 2. what works here
    out.append("## 2. BU KANALDA NE ISE YARIYOR")
    out.append("")
    comparisons = []
    if not enough:
        out.append(not_enough)
    else:
        rankable = [r for r in rows if metric(r) is not None]
        if len(rankable) < MIN_SAMPLES:
            out.append("**YETERSIZ VERI** (izlenmesi bilinen kayit n=%d, en az %d "
                       "gerekiyor). `topla` komutunu calistir."
                       % (len(rankable), MIN_SAMPLES))
        else:
            ranked = sorted(rankable, key=lambda r: -metric(r))
            half = len(ranked) // 2
            upper, lower = ranked[:half], ranked[-half:]
            for name, label, unit in FIELDS + EXTRA_FIELDS:
                line = _comparison_row(upper, lower, name, label, unit)
                if line:
                    comparisons.append(line)
            if comparisons:
                out.append("Videolar izlenmeye gore siralandi, ust yari ile alt yarinin")
                out.append("medyanlari karsilastirildi.")
                out.append("")
                out.append("| olcum | ust yari | alt yari | yon | n |")
                out.append("|---|---|---|---|---|")
                out.extend(comparisons)
                out.append("")
                out.append("> **Korelasyon, nedensellik degil.** Bunlar yon gosterir,")
                out.append("> kanun degildir. Tek dogru sanma, hipotez olarak kullan.")
            else:
                out.append("Karsilastirilabilir olcum alani bulunamadi "
                           "(her alanda en az 3+3 gecerli deger gerekiyor).")
    out.append("")

    # --- 3. general thresholds
    out.append("## 3. GENEL ESIKLER")
    out.append("")
    out.append("Kanala ozel veri yetersizse veya celiskiliyse bunlar gecerli.")
    out.append("")
    out.append(GENERAL_THRESHOLDS)
    out.append("")

    # --- 4. direction for today
    out.append("## 4. BUGUN ICIN YON")
    out.append("")
    if not enough or not comparisons:
        out.append(not_enough)
    else:
        out.append("2. bolumdeki farklardan cikan somut hedefler:")
        out.append("")
        advice = []
        ranked = sorted([r for r in rows if metric(r) is not None],
                        key=lambda r: -metric(r))
        half = len(ranked) // 2
        upper, lower = ranked[:half], ranked[-half:]
        for name, label, unit in FIELDS + EXTRA_FIELDS:
            result = _half_gap(upper, lower, name)
            if result is None:
                continue
            ma, mb, _, _, significant = result
            # Never turn noise into a target: it misleads the agent and burns
            # the credibility of the whole system.
            if not significant:
                continue
            # Never advise toward zero cuts. That direction falls out of blind
            # correlation and is actively harmful.
            if name == "kesme_per_10sn" and ma < 0.5:
                advice.append("- **%s**: ust yari %.2f, alt yari %.2f. Fark var ama "
                              "hedef olarak VERILMIYOR (sifira yakin kesme onerisi "
                              "zararli olur). Bu, format farkinin yan urunu olabilir."
                              % (label, ma, mb))
                continue
            advice.append("- **%s**: ust yarinin medyani %.2f%s (alt yari %.2f%s). "
                          "Bugunku videoyu %.2f%s civarina hedefle."
                          % (label, ma, unit, mb, unit, ma, unit))
        if advice:
            out.extend(advice)
        else:
            out.append("- Olculen alanlarin hicbirinde **anlamli fark yok** "
                       "(bagil fark esigi %%%d). Genel esiklere gore uret."
                       % int(MIN_RELATIVE_GAP * 100))
    out.append("")

    # --- 5. avoid
    out.append("## 5. KACIN")
    out.append("")

    # If the channel's BEST video breaks a threshold, that threshold does not
    # hold here. Applying it blindly would break what is working. Measured
    # example: the fleet's best channel has a 17.85 s longest shot.
    best = None
    ranked_any = [r for r in rows if metric(r) is not None]
    if ranked_any:
        best = max(ranked_any, key=metric)

    def _best_also_breaks(name, predicate):
        if not best:
            return False
        value = as_number((best.get("olcum") or {}).get(name))
        return value is not None and predicate(value)

    contradicted = []
    if _best_also_breaks("en_uzun_plan", lambda v: v > 4.0):
        contradicted.append(("Uzun statik plan", "en uzun plan 4 sn tavani",
                             as_number((best.get("olcum") or {}).get("en_uzun_plan"))))
    if _best_also_breaks("lufs", lambda v: not (-16.0 <= v <= -13.0)):
        contradicted.append(("Ses seviyesi hedef disi", "LUFS -16..-13 hedefi",
                             as_number((best.get("olcum") or {}).get("lufs"))))
    contradicted_kinds = {kind for kind, _, _ in contradicted}

    problems = []
    for row in rows:
        measured = row.get("olcum") or {}
        peak = as_number(measured.get("true_peak"))
        loud = as_number(measured.get("lufs"))
        longest = as_number(measured.get("en_uzun_plan"))
        if peak is not None and peak > -1.0:
            problems.append(("Ses kirpiyor",
                             "- **Ses kirpiyor**: `%s` true peak %.1f dBFS (tavan -1,0)"
                             % (row.get("video_id"), peak)))
        if loud is not None and not (-16.0 <= loud <= -13.0):
            problems.append(("Ses seviyesi hedef disi",
                             "- **Ses seviyesi hedef disi**: `%s` %.1f LUFS "
                             "(hedef -16..-13)" % (row.get("video_id"), loud)))
        if longest is not None and longest > 4.0:
            problems.append(("Uzun statik plan",
                             "- **Uzun statik plan**: `%s` en uzun plan %.1f sn "
                             "(tavan 4,0)" % (row.get("video_id"), longest)))

    problems = [(k, text) for k, text in problems if k not in contradicted_kinds]

    if contradicted:
        out.append("### Bu kanalda GECERSIZ esikler")
        out.append("")
        out.append("Asagidaki genel esikleri kanalin **en iyi videosu** de ihlal ediyor")
        out.append("(`%s`, %s izlenme). Yani bu kanalda o esik calismiyor."
                   % (best.get("video_id"), "{:,.0f}".format(metric(best) or 0)))
        out.append("**Kor uygulama, calisan seyi bozarsin.**")
        out.append("")
        for _, label, value in contradicted:
            out.append("- ~~%s~~ , en iyi videoda deger: **%.1f**" % (label, value))
        out.append("")

    if problems:
        # At most 3 examples per kind so the report stays readable.
        seen = {}
        trimmed = []
        for kind, text in problems:
            seen[kind] = seen.get(kind, 0) + 1
            if seen[kind] <= 3:
                trimmed.append(text)
        out.extend(trimmed)
        for kind, count in sorted(seen.items()):
            if count > 3:
                out.append("- _%s: toplam %d kayitta var, ilk 3 gosterildi._"
                           % (kind, count))
    elif contradicted:
        out.append("Kalan teknik esik ihlali yok.")
    elif total == 0:
        out.append("Veri yetersiz.")
    else:
        out.append("Olculen kayitlarda teknik esik ihlali yok.")
    out.append("")

    target = os.path.join(channel_dir(channel), "BEYIN.md")
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out))
    print("yazildi: %s  (n=%d, %s)"
          % (target, total,
             "kanala ozel kural VAR" if enough else "YETERSIZ VERI"))


def main():
    parser = argparse.ArgumentParser(description="Gunluk ogrenen beyin")
    parser.add_argument("komut", choices=["olc", "topla", "beyin"])
    parser.add_argument("kanal")
    parser.add_argument("--limit", type=int, default=15,
                        help="olc: RSS'ten kac video taransin")
    args = parser.parse_args()

    if args.komut == "olc":
        cmd_measure(args.kanal, args.limit)
    elif args.komut == "topla":
        cmd_collect(args.kanal)
    else:
        cmd_brain(args.kanal)


if __name__ == "__main__":
    main()
