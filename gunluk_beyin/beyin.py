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
import hashlib
import json
import os
import statistics as st
import sys
import tempfile
from datetime import datetime, timezone

import tamlik

ROOT = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.join(ROOT, "arac")

# Channel ids. Keep in sync with kanallarimiz.md.
CHANNELS = {
    "unnatural-lab": "UC-Aht8VqAUMTUKYRQA3agYQ",
    "event-horizon": "UCVCRWrQYrIHW6csOsw9bDNw",
    "flashpoints": "UCUdp0KLBh4EeeSgVbwS_DhA",
    "aimagine-fear": "UCCgbHTzYKYawUT6zEo0nlDg",
}

# Kanal -> seri klasoru. Rejim damgasi ve yayinlanmayan bolumler buradan okunur.
# aimagine-fear listede YOK: o kanal ayri bir boru hattiyla (build.py) uretiliyor,
# bible.json/series.json tasimiyor. Eksik olmasi hata degildir.
SERIES_DIRS = {
    "unnatural-lab": os.path.join("sentinal_ihsan", "unnatural-lab"),
    "event-horizon": os.path.join("galactic_experience", "event-horizon"),
    "flashpoints": os.path.join("shadowedhistory", "flashpoints"),
}

# TESLIM REJIMI: videoyu fiilen degistiren ayarlar. Iki farkli rejimde uretilmis
# videolar ayni defterde YAN YANA KARSILASTIRILAMAZ. -22 LUFS ve ekran yazisiz
# bolumlerle -14 LUFS ve kunyeli bolumler ayni urunun iki ornegi degil, iki ayri
# urundur; havuzlanirsa beyin izlenme farkini yanlis sebebe baglar.
REGIME_BIBLE_FIELDS = (
    "master_lufs", "master_true_peak_margin_db", "title_card", "fact_captions",
    "required_layers", "duration_band", "block_degraded_publish", "hook_teaser",
    "upscale", "micro_trim", "audio_smooth", "resolution", "aspect_ratio",
)
REGIME_REPLENISH_FIELDS = ("shots", "shot_seconds", "title_style", "narration",
                           "title_card", "fact_captions")

# series.json'da YAYINLANMIS sayilmayan durumlar zaten "published" disidir;
# bu ikisi ise kuyrukta sirasini bekleyen normal hallerdir, kusur degildir.
QUEUED_STATES = ("", "planned", "queued", "pending")

# Yayinlanmayan her bolum "uretildi" DEMEK DEGILDIR. Butce kapisi ucretli ise
# BASLAMADAN once durur, atlanan/reddedilen bolum hic cekilmez. Bunlari
# "uretildi ama yayinlanmadi" diye sunmak BEYIN.md'yi yalanci yapar.
UNPRODUCED_STATES = ("budget_exhausted", "skipped", "rejected")

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


def safe_slug(channel):
    """Reject slugs that could escape `kanallar/`, return it unchanged if safe.

    Found by an independent adversarial suite on 2026-09-10:
    `beyin.py beyin "unnatural-lab/../pwned"` exited 0 and wrote
    `kanallar/unnatural-lab/../pwned/BEYIN.md`, i.e. OUTSIDE the intended tree.
    Membership in CHANNELS is deliberately NOT required here: `beyin` only reads
    a ledger and writing reports for ad-hoc slugs is a feature. Safety is not.
    """
    text = "" if channel is None else str(channel)
    if not text.strip():
        sys.exit("Bilinmeyen kanal , gecersiz slug: bos slug.")
    if text != text.strip():
        sys.exit("Bilinmeyen kanal , gecersiz slug: bastaki/sondaki bosluk. -> %r" % text)
    if os.path.isabs(text) or (len(text) > 1 and text[1] == ":"):
        sys.exit("Bilinmeyen kanal , gecersiz slug: mutlak yol kabul edilmez. -> %r" % text)
    if "/" in text or "\\" in text or os.sep in text:
        sys.exit("Bilinmeyen kanal , gecersiz slug: yol ayraci kabul edilmez. -> %r" % text)
    if text in (".", "..") or text.startswith("."):
        sys.exit("Bilinmeyen kanal , gecersiz slug: nokta ile baslayan slug kabul edilmez. -> %r" % text)
    if any(ord(ch) < 32 for ch in text):
        sys.exit("Bilinmeyen kanal , gecersiz slug: kontrol karakteri iceriyor.")
    return text


def channel_dir(channel, root=None):
    return os.path.join(root or os.getcwd(), "kanallar", safe_slug(channel))


def ledger_path(channel, root=None):
    return os.path.join(channel_dir(channel, root), "defter.jsonl")


def repo_root(root=None):
    """gunluk_beyin/ bir alt klasordur; seri dosyalari bir ust dizindedir."""
    return os.path.dirname(root or ROOT)


def series_dir(channel, root=None):
    """Kanalin seri klasoru. Bilinmeyen kanal ya da yoksa None (hata degil)."""
    rel = SERIES_DIRS.get(channel)
    if not rel:
        return None
    path = os.path.join(repo_root(root), rel)
    return path if os.path.isdir(path) else None


def _read_json(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return None


def delivery_regime(channel, root=None):
    """Bugun bu kanaldan cikan videoyu belirleyen ayarlarin parmak izi.

    Donus: {"id": "<8 hex>", "alanlar": {...}} ya da kaynak yoksa None.
    Kaynagin bulunamamasi bir HATA DEGILDIR: aimagine-fear'in bible.json'u yok
    ve testler beyin.py'yi bos bir gecici kokte calistirir.
    """
    folder = series_dir(channel, root)
    if not folder:
        return None
    bible = _read_json(os.path.join(folder, "bible.json"))
    if not isinstance(bible, dict):
        return None
    fields = {}
    series = bible.get("series")
    if isinstance(series, dict):
        for key in REGIME_BIBLE_FIELDS:
            if key in series:
                fields["bible." + key] = series[key]
    if "music" in bible:
        fields["bible.music"] = bible["music"]
    meta = _read_json(os.path.join(folder, "series.json"))
    cfg = (meta or {}).get("auto_replenish")
    if isinstance(cfg, dict):
        for key in REGIME_REPLENISH_FIELDS:
            if key in cfg:
                fields["cfg." + key] = cfg[key]
    if not fields:
        return None
    blob = json.dumps(fields, sort_keys=True, ensure_ascii=False)
    digest = hashlib.sha256(blob.encode("utf-8")).hexdigest()[:8]
    return {"id": digest, "alanlar": fields}


def _parts_of(channel, root=None):
    folder = series_dir(channel, root)
    if not folder:
        return None
    meta = _read_json(os.path.join(folder, "series.json"))
    parts = (meta or {}).get("parts")
    return parts if isinstance(parts, dict) else None


def part_regime(channel, part, root=None):
    """Bir bolumun URETIM ANINDAKI teslim parmak izi.

    Motor her bolumun uretim stack'ini (kaynak dosyalar + bible + auto_replenish)
    hashleyip part kaydina `stack_sha256` yaziyor. Bu, olcum aninda yapilandirmayi
    yeniden okumaktan KESIN olarak daha dogrudur: 24 saat kapisi yuzunden bir video
    hep ayarlar DEGISMIS olabilecek bir gun sonra olculur. Olculdu: part 32 eski
    ayarla yayinlandi, ertesi gun yeni ayarlar yururlukteyken olculecek.
    """
    parts = _parts_of(channel, root)
    row = (parts or {}).get(str(part))
    digest = (row or {}).get("stack_sha256")
    if isinstance(digest, str) and len(digest) >= 8:
        return digest[:8]
    return None


def published_regime(channel, video_id, root=None):
    """video_id -> published.json -> part -> uretim anindaki parmak izi."""
    folder = series_dir(channel, root)
    if not folder:
        return None
    published = _read_json(os.path.join(folder, "published.json"))
    if not isinstance(published, list):
        return None
    for entry in reversed(published):
        if not isinstance(entry, dict):
            continue
        if (entry.get("results") or {}).get("youtube") == video_id:
            return part_regime(channel, entry.get("part"), root)
    return None


def latest_regime(channel, root=None):
    """EN SON yayinlanan bolumun parmak izi = bugunun rejimi."""
    parts = _parts_of(channel, root)
    if not parts:
        return None
    numaralar = sorted((int(k) for k in parts if str(k).isdigit()), reverse=True)
    for numara in numaralar:
        row = parts.get(str(numara)) or {}
        if row.get("status") != "published":
            continue
        digest = row.get("stack_sha256")
        if isinstance(digest, str) and len(digest) >= 8:
            return digest[:8]
    return None


def regimes_path(channel, root=None):
    return os.path.join(channel_dir(channel, root), "rejimler.json")


def read_regimes(channel, root=None):
    data = _read_json(regimes_path(channel, root))
    return data if isinstance(data, dict) else {}


def remember_regime(channel, regime, root=None):
    """Rejimi bir kez kaydet; boylece beyin NEYIN degistigini soyleyebilir."""
    if not regime:
        return
    known = read_regimes(channel, root)
    if regime["id"] in known:
        return
    known[regime["id"]] = {"ilk_gorulme": now_iso(), "alanlar": regime["alanlar"]}
    os.makedirs(channel_dir(channel, root), exist_ok=True)
    with open(regimes_path(channel, root), "w", encoding="utf-8") as fh:
        json.dump(known, fh, ensure_ascii=False, indent=2, sort_keys=True)


def regime_diff(older, newer):
    """Iki rejimin alan sozlukleri arasindaki farki insan diliyle listele."""
    lines = []
    for key in sorted(set(older) | set(newer)):
        before, after = older.get(key, "<yok>"), newer.get(key, "<yok>")
        if before == after:
            continue
        lines.append("%s: %s -> %s"
                     % (key, json.dumps(before, ensure_ascii=False)[:60],
                        json.dumps(after, ensure_ascii=False)[:60]))
    return lines


def held_episodes(channel, root=None):
    """URETILDI ama YAYINLANMADI olan bolumler.

    Beynin kor noktasi tam olarak burasi: defter yalnizca YouTube'a cikani
    olcer, yani en cok ogrenilecek basarisizliklar kayda hic girmez.
    Donus: liste, ya da kaynak okunamadiysa None.
    """
    folder = series_dir(channel, root)
    if not folder:
        return None
    meta = _read_json(os.path.join(folder, "series.json"))
    parts = (meta or {}).get("parts")
    if not isinstance(parts, dict):
        return None
    held = []
    for key, part in parts.items():
        if not isinstance(part, dict):
            continue
        status = str(part.get("status") or "").strip()
        if status == "published" or status in QUEUED_STATES:
            continue
        coherence = part.get("coherence")
        coherence = coherence if isinstance(coherence, dict) else {}
        held.append({
            "part": str(key),
            "durum": status,
            "kod": part.get("last_reason_code") or "",
            "neden": str(part.get("hold_reason") or "")[:120],
            "deneme": part.get("retry_count"),
            "dusen_roller": coherence.get("arc_roles_missing") or [],
            "anlatim": coherence.get("narration_delivered"),
            "sure": coherence.get("duration_s"),
            "baslik": str(part.get("subtitle") or "")[:48],
            "uretildi": status not in UNPRODUCED_STATES,
        })
    held.sort(key=lambda h: int(h["part"]) if h["part"].isdigit() else 0)
    return held


def read_hold_log(channel, root=None):
    """Motorun OLAY ANINDA yazdigi tutulma defteri.

    series.json anlik durumu tutar, bu dosya ise gecmisi: bir bolum takilip
    sonraki kosuda toparlanirsa series.json'da iz kalmaz ama burada kalir.
    Donus: liste (dosya yoksa bos liste).
    """
    folder = series_dir(channel, root)
    if not folder:
        return []
    path = os.path.join(folder, "hold_log.jsonl")
    rows = []
    if not os.path.exists(path):
        return rows
    with open(path, encoding="utf-8", errors="replace") as fh:
        for raw in fh:
            raw = raw.strip()
            if not raw:
                continue
            try:
                row = json.loads(raw)
            except Exception:
                continue
            if isinstance(row, dict) and row.get("part") is not None:
                rows.append(row)
    return rows


def faults_path(channel, root=None):
    return os.path.join(channel_dir(channel, root), "kusur.jsonl")


def read_faults(channel, root=None):
    """Kusur defteri: gecmiste GORULMUS yayinlanmama olaylari."""
    path = faults_path(channel, root)
    rows = []
    if not os.path.exists(path):
        return rows
    with open(path, encoding="utf-8", errors="replace") as fh:
        for raw in fh:
            raw = raw.strip()
            if not raw:
                continue
            try:
                row = json.loads(raw)
            except Exception:
                continue
            if isinstance(row, dict) and row.get("anahtar"):
                rows.append(row)
    return rows


def _fault_key(item):
    return "%s|%s|%s|%s" % (item["part"], item["durum"], item["kod"],
                            item["neden"][:40])


def record_faults(channel, root=None):
    """Anlik kusurlari KALICI deftere isle.

    series.json yalnizca SU ANKI durumu tutar: iki gunluk kosu arasinda kendini
    toparlayan bir hata (ornek: unnatural-lab part 33, AUDIO_MASTER, yeniden
    denemede yayinlandi) hicbir yerde iz birakmazdi. Burasi o izi birakir.
    Donus: (toplam_kayit, yeni_eklenen).
    """
    held = held_episodes(channel, root)
    if held is None:
        return None
    known = read_faults(channel, root)
    seen = {row["anahtar"]: row for row in known}
    added = 0
    stamp = now_iso()
    for item in held:
        key = _fault_key(item)
        if key in seen:
            seen[key]["son_gorulme"] = stamp
            continue
        row = dict(item)
        row["anahtar"] = key
        row["ilk_gorulme"] = stamp
        row["son_gorulme"] = stamp
        known.append(row)
        seen[key] = row
        added += 1
    if known:
        os.makedirs(channel_dir(channel, root), exist_ok=True)
        with open(faults_path(channel, root), "w", encoding="utf-8") as fh:
            for row in known:
                fh.write(json.dumps(row, ensure_ascii=False) + chr(10))
    return (len(known), added)


def read_ledger(channel, root=None):
    """Skip malformed lines instead of crashing. Returns (rows, skipped).

    Duplicate `video_id` rows are collapsed to the LAST occurrence and counted
    as skipped. Without this a duplicated row inflates the sample count and can
    push a channel past the 15-video gate on fake evidence, which is exactly the
    kind of false confidence the whole design tries to avoid.
    """
    path = ledger_path(channel, root)
    rows, skipped = [], 0
    if not os.path.exists(path):
        return rows, skipped
    by_id = {}
    order = []
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
            if not (isinstance(row, dict) and row.get("video_id")):
                skipped += 1
                continue
            vid = row["video_id"]
            if vid in by_id:
                skipped += 1          # duplicate, later row wins
            else:
                order.append(vid)
            by_id[vid] = row
    rows = [by_id[v] for v in order]
    return rows, skipped


def write_ledger(channel, rows, root=None):
    """Atomic write. Either the whole ledger lands, or the old one survives.

    The previous version opened the target with "w", which truncates before the
    first byte is written: a crash mid-write destroyed the entire ledger, and
    `olc` calls this inside its per-video loop, so the window was wide open.
    Now we write a sibling temp file, fsync it, and atomically replace.
    `os.replace` is atomic on both POSIX and Windows.
    """
    path = ledger_path(channel, root)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as fh:
            for row in rows:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    except Exception:
        # Leave the original untouched and drop the half-written temp file.
        try:
            if os.path.exists(tmp):
                os.remove(tmp)
        except OSError:
            pass
        raise


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
        from uploads import list_uploads
        from olc import tek as measure_one
    except Exception as exc:
        sys.exit("arac/ modulleri yuklenemedi: %s" % exc)

    rows, _ = read_ledger(channel)
    known = {row["video_id"] for row in rows}
    # Teslim rejimi: bu video HANGI ayarlarla uretildi. Kaynak yoksa damgasiz
    # gecer; beyin damgasiz kayitlari "bilinmiyor" diye ayri sayar.
    regime = delivery_regime(channel)
    remember_regime(channel, regime)
    if regime:
        print("teslim rejimi: %s" % regime["id"])
    else:
        print("teslim rejimi: kaynak yok (bu kanal icin seri dosyasi bulunamadi)")
    # Yukleme listesi okunamadiysa DUR. Eskiden bos liste donuyordu ve arac
    # bunu "yeni video yok" sanip exit 0 veriyordu: kaynak tamamen kopukken
    # gunluk kosu YESIL gorunuyordu. Artik fail-closed.
    #
    # Kaynak artik RSS DEGIL. Olculdu 2026-09-10: youtube.com/feeds/videos.xml
    # hem ev IP'sinden hem GitHub runner'indan 404/500 veriyor; MrBeast ve
    # Google kanallarinda da ayni. Birincil kaynak Data API v3, RSS yedek.
    feed, feed_error, feed_source = list_uploads(CHANNELS[channel], limit)
    if feed_error:
        sys.exit("DUR: %s kanalinin yukleme listesi okunamadi.\n  %s\n"
                 "  Defter DEGISTIRILMEDI. Bu bir ag/erisim/kota sorunudur, "
                 "'yeni video yok' DEGILDIR." % (channel, feed_error))
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

    print("kanal: %s  |  kaynak: %s  |  liste: %d  |  defterde yok: %d"
          "  |  olculecek: %d"
          % (channel, feed_source, len(feed), len(candidates), len(due)))
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
        yayin_rejimi = published_regime(channel, vid)
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
            # Once URETIM anindaki parmak izi (dogru olan), o yoksa olcum
            # anindaki yapilandirma karmasi (yaklasik; kaynagi da yaziliyor).
            "rejim": yayin_rejimi or (regime["id"] if regime else None),
            "rejim_kaynak": ("yayin" if yayin_rejimi
                             else ("olcum" if regime else None)),
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

    # Fail-closed: tek bir kayit bile guncellenemediyse bu neredeyse kesinlikle
    # ag/erisim sorunudur, "izlenme degismemis" DEGILDIR. Eskiden sessizce
    # exit 0 veriyordu ve gunluk kosu yesil goruunuyordu.
    if rows and updated == 0:
        sys.exit("DUR: %d kaydin HICBIRI icin canli sayi alinamadi.\n"
                 "  Bu bir ag/erisim sorunudur. Defter yazildi ama hicbir yeni\n"
                 "  olcum eklenmedi." % len(rows))
    # Kismi basarisizlik kirmizi degil ama sessiz de degil: gorunur olsun.
    if rows and updated < len(rows):
        print("UYARI: %d kayit icin canli sayi alinamadi (ag veya video kaldirilmis)."
              % (len(rows) - updated))


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
    # Yazim hatasi sessizce yeni bir kanal acmamali. `flashpoint` (s eksik)
    # bugune kadar `kanallar/flashpoint/BEYIN.md` diye BOS bir rapor uretiyordu
    # ve okuyan onu `flashpoints` sanabilirdi.
    # Kapi "CHANNELS uyesi VEYA defteri zaten var" seklinde: deneysel/ad-hoc
    # defterler calismaya devam eder, yazim hatasi durur.
    safe_slug(channel)
    if channel not in CHANNELS and not os.path.exists(ledger_path(channel)):
        sys.exit("Bilinmeyen kanal: %s\n  Gecerli: %s\n"
                 "  (ya da once %s dosyasini olustur)"
                 % (channel, ", ".join(sorted(CHANNELS)), ledger_path(channel)))
    rows, skipped = read_ledger(channel)
    total = len(rows)

    # --- uretim tamligi --------------------------------------------------
    # Rejim damgasi "hangi AYARLARLA uretildi" sorusunu cozer. Bu ise ayri bir
    # soru: "uretim BASARILI mi oldu". Defter yayinlanmis DOSYAYI olcer, yani
    # 9,44 saniyelik bir videonun aslinda cekimi dusmus 20 saniyelik bir plan
    # oldugunu bilemez. Olculen sonuc: flashpoints ust yarisindaki 7 videonun
    # 4'u yarim bolumdu ve bolum 4 "9.44sn ve 26 kelime hedefle" diyordu , yani
    # ayni gun min_shots=2 ile durdurulan kusuru ogretiyordu.
    # "Bilinmiyor" EKSIK demek DEGILDIR: yargilanamayan satir iceride kalir.
    durations = {}
    for row in rows:
        vid = row.get("video_id")
        value = field(row, "sure")
        if vid and value is not None:
            durations[vid] = value
    try:
        completeness = tamlik.episode_completeness(channel, durations=durations)
    except Exception:
        completeness = {}
    dropped_ids = set()
    for row in rows:
        vid = row.get("video_id")
        if (completeness.get(vid) or {}).get("complete") is False:
            dropped_ids.add(vid)
    clean = [r for r in rows if r.get("video_id") not in dropped_ids]

    # --- teslim rejimi ---------------------------------------------------
    # Iki farkli rejimde uretilmis videolari YAN YANA sayarsak beyin izlenme
    # farkini yanlis sebebe baglar. Kural:
    #   damga hic yoksa      -> havuzla, ama takibin YENI basladigini soyle
    #   guncel rejim yeterli -> YALNIZ onu kullan
    #   guncel rejim az      -> havuzla, ama kac kaydin guncel oldugunu SOYLE
    # Guncel rejim = EN SON YAYINLANAN bolumun uretim parmak izi. Yapilandirmayi
    # SIMDI okumak yaniltir: bugun degistirilen bir ayar dun yayinlanmis videoyu
    # etkilemez, ama 24 saat kapisi yuzunden olcum hep bir gun sonra yapilir.
    regime = delivery_regime(channel)
    regime_id = latest_regime(channel) or (regime["id"] if regime else None)
    stamped = [r for r in clean if r.get("rejim")]
    current_rows = ([r for r in clean if r.get("rejim") == regime_id]
                    if regime_id else [])
    regime_note = None
    if not stamped:
        compare_rows = clean
        if regime_id:
            regime_note = ("Rejim takibi bugun basladi; defterdeki %d kaydin "
                           "hicbirinde damga yok, hepsi birlikte sayiliyor."
                           % total)
    elif len(current_rows) >= MIN_SAMPLES:
        compare_rows = current_rows
        regime_note = ("Karsilastirma YALNIZ guncel rejimin %d kaydiyla yapildi "
                       "(defterde toplam %d kayit var)." % (len(current_rows), total))
    else:
        compare_rows = clean
        regime_note = ("**DIKKAT: karma orneklem.** Guncel rejimde yalnizca %d "
                       "kayit var, en az %d gerekiyor; bu yuzden asagidaki "
                       "karsilastirma FARKLI ayarlarla uretilmis %d kaydi bir "
                       "arada kullaniyor. Yonu kanun sanma."
                       % (len(current_rows), MIN_SAMPLES, total))
    enough = len(compare_rows) >= MIN_SAMPLES

    # Age-fair ranking. Comparing a 30-day-old video to a 2-day-old one on
    # current views is unfair; if most rows carry an hour-24 figure, use it.
    # Otherwise fall back to current views AND SAY SO in the report.
    # MIN_SAMPLES sarti BURADA da gecerli olmali. Aksi halde veri birikirken
    # sistem GERILER: 11/15 kayitta 24s olcumu varken guncel izlenmeyle kural
    # uretiliyor, 12/15'e cikinca 24s olcusune geciliyor ama o olcuye sahip
    # kayit sayisi (12) MIN_SAMPLES'in (15) altinda kaldigi icin 2. bolum
    # "YETERSIZ VERI" diyor. Yani olcum iyilesirken rapor korlesiyor.
    # Olculdu 2026-09-10: 0/15 kural VAR, 11/15 kural VAR, 12/15 YETERSIZ, 15/15 kural VAR.
    with_24h = [r for r in rows if views_at_24h(r) is not None]
    if rows and len(with_24h) >= max(MIN_SAMPLES, int(total * 0.8)):
        metric = views_at_24h
        metric_label = "**24. saat izlenmesi** (yas-adil)"
    else:
        metric = views
        metric_label = ("guncel izlenme , _24. saat olcumu henuz %d/%d kayitta "
                        "var, yaslar farkli oldugu icin siralamayi dikkatli oku_"
                        % (len(with_24h), total))

    # Eksik uretilen kayitlar elendiyse SAYISINI soyle: yoksa "n=15, en az 15
    # gerekiyor" gibi kendiyle celisen bir cumle cikiyor ve hata gibi okunuyor.
    _elenen = total - len(clean)
    not_enough = (
        "**YETERSIZ VERI** (n=%d, en az %d gerekiyor%s). Bu kanala ozel kural "
        "cikarilamaz, asagidaki genel esikler kullanilmali."
        % (len(compare_rows), MIN_SAMPLES,
           "; defterdeki %d kaydin %d tanesi eksik uretildigi icin sayilmadi"
           % (total, _elenen) if _elenen else "")
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

    # --- teslim rejimi: neyle uretildi -----------------------------------
    if regime_note:
        out.append("")
        out.append("### Teslim rejimi")
        out.append("")
        if regime_id:
            out.append("- Guncel rejim: `%s`" % regime_id)
        out.append("- %s" % regime_note)
        by_regime = {}
        for row in rows:
            key = row.get("rejim") or "damgasiz"
            by_regime[key] = by_regime.get(key, 0) + 1
        if len(by_regime) > 1:
            out.append("- Defterdeki dagilim: %s"
                       % ", ".join("`%s` x%d" % (k, v)
                                   for k, v in sorted(by_regime.items(),
                                                      key=lambda kv: -kv[1])))
            known = read_regimes(channel)
            others = [k for k in by_regime if k not in ("damgasiz",)
                      and k != regime_id]
            if regime and others:
                previous = known.get(others[0], {}).get("alanlar")
                if isinstance(previous, dict):
                    changes = regime_diff(previous, regime["alanlar"])
                    if changes:
                        out.append("- Onceki rejime gore degisenler:")
                        for line in changes[:8]:
                            out.append("  - %s" % line)

    # --- yayinlanmayanlar: beynin goremedigi hatalar ---------------------
    fault_stats = record_faults(channel)
    held = held_episodes(channel)
    if held is None:
        # Sessizlik "temiz" diye okunur. Goremedigimizi ACIKCA soyle.
        out.append("")
        out.append("### Yayinlanmayanlar")
        out.append("")
        out.append("- Bu kanal icin seri kaydi okunamadi (ayri boru hatti ya da "
                   "dosya yok). Yayinlanmayan bolumler GORUNTULENEMIYOR; "
                   "bu 'hata yok' demek DEGILDIR.")
    else:
        out.append("")
        out.append("### Yayinlanmayanlar")
        out.append("")
        history = fault_stats[0] if fault_stats else 0
        engine_log = read_hold_log(channel)
        if engine_log:
            son = engine_log[-1]
            out.append("- Motor tutulma defterinde **%d** olay var "
                       "(`hold_log.jsonl`); sonuncusu part %s / %s. Bu defter olay "
                       "ANINDA yazilir, yani kendini toparlayan hatalar da iz birakir."
                       % (len(engine_log), son.get("part"), son.get("kod") or "?"))
        if not held:
            out.append("- Su anda tutulan bolum yok.")
            if history:
                out.append("- Kusur defterinde gecmisten **%d** olay kayitli "
                           "(`kusur.jsonl`). series.json yalnizca ANLIK durumu "
                           "tutar; kendini toparlayan hatalar orada iz birakmaz."
                           % history)
        else:
            uretilen = [h for h in held if h.get("uretildi")]
            uretilmeyen = [h for h in held if not h.get("uretildi")]
            out.append("- **%d bolum YAYINLANMADI.** Bunlar YouTube'a cikmadigi "
                       "icin yukaridaki olcumlere HIC girmiyor." % len(held))
            if uretilen:
                out.append("  - %d tanesi URETILDI ama yayina giremedi; en cok "
                           "ogrenilecek hatalar bunlardir." % len(uretilen))
            if uretilmeyen:
                out.append("  - %d tanesi HIC URETILMEDI (butce kapisi, atlandi "
                           "ya da reddedildi); kredi harcanmadi." % len(uretilmeyen))
            out.append("")
            out.append("| part | uretim | durum | kod | eksik | deneme |")
            out.append("|---|---|---|---|---|---|")
            for item in held[-8:]:
                eksik = []
                if item["dusen_roller"]:
                    eksik.append("dusen: " + ", ".join(map(str, item["dusen_roller"])))
                if item["anlatim"] is False:
                    eksik.append("anlatim cikmadi")
                if item["sure"]:
                    eksik.append("%.1f sn" % item["sure"])
                if not eksik and item["neden"]:
                    eksik.append(item["neden"][:44])
                out.append("| %s | %s | %s | %s | %s | %s |"
                           % (item["part"],
                              "uretildi" if item.get("uretildi") else "uretilmedi",
                              item["durum"] or "?",
                              item["kod"] or "-", "; ".join(eksik) or "-",
                              item["deneme"] if item["deneme"] is not None else "-"))
    # Hicbir satir SESSIZCE dusmesin: raporu okuyan ajan NEYIN neden
    # elendigini gormeli. Yeni bir numarali bolum degil ALT baslik, cunku
    # tests/test_beyin_bagimsiz.py bes ust basligi birebir sabitliyor.
    if dropped_ids:
        out.append("")
        out.append("### Kural cikarimina GIRMEYEN bolumler")
        out.append("")
        out.append("Bu bolumler EKSIK uretilmis (bir cekim dusmus). Yayinlanan")
        out.append("dosya kisa ve anlatimi otomatik kisaltilmis oldugu icin")
        out.append("olcumleri bir basari ornegi DEGILDIR; 2., 4. ve 5. bolumlerin")
        out.append("hicbirine girmiyorlar.")
        out.append("")
        out.append("| video | bolum | sebep |")
        out.append("|---|---|---|")
        for row in rows:
            vid = row.get("video_id")
            if vid not in dropped_ids:
                continue
            info = completeness.get(vid) or {}
            out.append("| `%s` | %s | %s |"
                       % (vid,
                          info.get("part") if info.get("part") is not None else "?",
                          info.get("reason") or "?"))
        out.append("")
        out.append("Kalan tam kayit: **%d** (esik %d)." % (len(clean), MIN_SAMPLES))
    out.append("")

    # --- 2. what works here
    out.append("## 2. BU KANALDA NE ISE YARIYOR")
    out.append("")
    comparisons = []
    if not enough:
        out.append(not_enough)
    else:
        rankable = [r for r in compare_rows if metric(r) is not None]
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
        # Bolum 2 ile AYNI kume: hedefler o karsilastirmadan cikiyor, farkli
        # kume kullanmak iki bolumu celiskiye dusurur.
        ranked = sorted([r for r in compare_rows if metric(r) is not None],
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
    # En iyi video TAM bolumlerden secilmeli. Bir esigi KUSURLU bir bolume
    # dayanarak gecersiz ilan etmek, LUFS hedefinin 2026-09-10'da tam olarak
    # boyle cizilip atilmasina yol acti (o -21.2 LUFS "en iyi" yarim bolumdu).
    ranked_any = [r for r in clean if metric(r) is not None]
    if ranked_any:
        best = max(ranked_any, key=metric)

    def _best_also_breaks(name, predicate):
        if not best:
            return False
        value = as_number((best.get("olcum") or {}).get(name))
        return value is not None and predicate(value)

    def _all_break(name, predicate):
        """TUM olculen videolar esigi ihliyorsa True.

        En iyi video, baskalarinin tutturdugu bir esigi ihlal ediyorsa o esik
        gercekten burada kazananlari ayirmiyor demektir. Ama HERKES ihlal
        ediyorsa bu esik hakkinda hicbir sey soylemez: boru hattinin o esigi
        HIC UYGULAMADIGINI soyler. Cizip atmak gercek kusuru gizler.
        Olculen ornek: flashpoints'te 15 kaydin 15'i de -19,6..-25,1 LUFS'ta,
        cunku mastering hic cagrilmamisti (bible.series.master_lufs yoktu).
        """
        seen = [as_number((r.get("olcum") or {}).get(name)) for r in rows]
        seen = [v for v in seen if v is not None]
        return bool(seen) and all(predicate(v) for v in seen)

    contradicted = []
    never_applied = []
    for _ad, _tur, _etiket, _kosul in (
        ("en_uzun_plan", "Uzun statik plan", "en uzun plan 4 sn tavani",
         lambda v: v > 4.0),
        ("lufs", "Ses seviyesi hedef disi", "LUFS -16..-13 hedefi",
         lambda v: not (-16.0 <= v <= -13.0)),
    ):
        if not _best_also_breaks(_ad, _kosul):
            continue
        _deger = as_number((best.get("olcum") or {}).get(_ad))
        if _all_break(_ad, _kosul):
            # Boru hatti o esigi HIC uygulamamis. Bu bir cikarim degil,
            # dogrudan olculmus bir olgu; az veriyle de dogrudur, kapisiz gecer.
            never_applied.append((_tur, _etiket, _deger))
        elif enough:
            # Esik IPTALI kanala ozel bir CIKARIMDIR. n<15 iken tek bir videoya
            # dayanip genel bir esigi "gecersiz" ilan etmek, 2. ve 4. bolumlerde
            # yasakladigimiz seyin aynisidir. Ayni `enough` kapisinin arkasinda.
            contradicted.append((_tur, _etiket, _deger))
    contradicted_kinds = {kind for kind, _, _ in contradicted}
    never_kinds = {kind for kind, _, _ in never_applied}

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

    problems = [(k, text) for k, text in problems
                if k not in contradicted_kinds and k not in never_kinds]

    if never_applied:
        out.append("### Bu kanalda HIC UYGULANMAMIS esikler")
        out.append("")
        out.append("Asagidaki esigi olculen videolarin **TAMAMI** ihlal ediyor.")
        out.append("Bu, esigin burada calismadigini GOSTERMEZ , boru hattinin o")
        out.append("esigi hic uygulamadigini gosterir. Esik gecerlidir; eksik olan")
        out.append("uygulamadir. Duzeltilene kadar bu boyutta karsilastirma yapma.")
        out.append("")
        for _, _etiket, _deger in never_applied:
            out.append("- **%s** , en iyi tam videoda deger: **%.1f** "
                       "(tum kayitlar ihlalde)" % (_etiket, _deger))
        out.append("")

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

    # --- 6. title subject
    # Etiketler kanallar/<kanal>/ozne.json icinde ELLE konuluyor ve asagidaki
    # medyan ayni etiketlerden hesaplaniyor. Bu bir KESIF DEGILDIR; bolum
    # bunu acikca soyler ve kaynagini her zaman gosterir.
    # Yeni numarali baslik guvenli: sabitlenen baslik testleri yalniz 1-5'i kapsar.
    out.append("## 6. BASLIK OZNESI")
    out.append("")
    labels = tamlik.read_subject_labels(channel)
    _kaynak = ("`shadowedhistory/REELYZE-RAPOR.md` , 29 bolumun tamami olculdu, "
               "10 Eylul 2026")
    _gruplar = {}
    for row in clean:
        _etiket = labels.get(row.get("video_id"))
        _deger = metric(row)
        if _etiket and _deger is not None:
            _gruplar.setdefault(_etiket, []).append(_deger)
    _dolu = {k: v for k, v in _gruplar.items() if len(v) >= 3}

    out.append("**HIPOTEZ** , baslikin KALIBI degil, OZNESI ayirt ediyor gorunuyor:")
    out.append("gozde canlanan bir SEY (yapi, eser, hayvan, marka) > OLAY > adiyla")
    out.append("anilan KISI. Kaynak: %s." % _kaynak)
    out.append("")
    if len(_dolu) >= 2:
        out.append("Bu defterdeki etiketli ve TAM bolumlerde:")
        out.append("")
        out.append("| ozne | n | medyan izlenme |")
        out.append("|---|---|---|")
        for _etiket in ("SEY", "OLAY", "KISI"):
            _degerler = _dolu.get(_etiket)
            if _degerler:
                out.append("| %s | %d | %s |"
                           % (_etiket, len(_degerler),
                              "{:,.0f}".format(st.median(_degerler))))
        out.append("")
        out.append("> Etiketler ELLE konuldu ve medyan ayni etiketlerden hesaplandi.")
        out.append("> Bu bir KESIF DEGIL, kayitli bir HIPOTEZIN bu defterdeki")
        out.append("> gorunumudur. Korelasyon, nedensellik degil.")
    else:
        out.append("Bu defterde HENUZ yeterli etiket yok (en az iki grupta 3'er")
        out.append("tam bolum gerekiyor), bu yuzden **sayi uretilmedi**.")
        out.append("Etiket eklemek icin: `kanallar/%s/ozne.json`" % channel)
        out.append('(`{"<video_id>": "SEY" | "OLAY" | "KISI"}`).')
    out.append("")
    out.append("Uygulama notu: kisi konusu ELENMEZ, basligin OZNESI degistirilir.")
    out.append('Ornek: "John Snow: The Father Of Epidemiology" yerine')
    out.append("\"The Water Pump That Ended London's Cholera Outbreak\".")
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
