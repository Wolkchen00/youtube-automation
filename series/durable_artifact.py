"""ROCK E - kosu sinirini gecen bolum eseri (durable episode artifact).

KUSUR. ``_persist_release(slug, n, video)`` YALNIZ ``if mode == "approval":``
blogunun icinden cagriliyordu (series_runner.py:806). unnatural-lab'in
``publish_mode`` degeri ``auto``, yani bu seride kalici Release HIC olusmuyor ve
uretilen hicbir sey kosu sinirini gecmiyordu. Sonraki kosu sifirdan uretirken
kalici defter (credits_ledger.json / episode_spend) ayni bolum tavanina karsi
saymaya devam ediyordu: bolum 25, 26, 28 ve 30 toplam 2.896 kredi yakti ve
sifir video uretti.

BU MODUL SAF MANTIKTIR. Yeni bir depolama katmani YOKTUR: eser hala
``series_runner._persist_release`` ile GitHub Release'e yuklenir. Burada yalniz
eserin KIMLIGI uretilir ve dogrulanir.

KIMLIK. ``series:episode`` anahtari ve bayt butunlugu YETMEZ; plan, referanslar
ya da QC politikasi degistikten sonra bayat bir cekimi geri getirirdi. Kontrol
noktalari dorde baglanir:
  1. normalize edilmis TAM PLAN ozeti (``plan_sha256``),
  2. REFERANS ICERIK ozeti (``reference_sha256``),
  3. QC POLITIKA parmak izi (``qc_policy_sha256``),
  4. KALICILASTIRILMIS QC-gecis kanit (``shots``: her kabul edilmis cekimin
     icerik ozeti + o cekimin ``qc_pass`` olayi).

BELIRSIZLIK. "Dogrulanamazsa yeniden uret" kurali gecici bir depolama arizasini
taze kredi harcamasina cevirir. Bu yuzden sonuc UC ayri koda ayrilir:
  ``absent``  - kayitli eser yok; normal uretim.
  ``invalid`` - eser indirildi ve KESIN olarak bugunku bolum tanimina ait degil
                (fingerprint uyusmuyor ya da baytlar bozuk); at ve yeniden uret.
  ``blocked`` - kurtarma BELIRSIZ (depo erisilemiyor ya da QC kaniti
                dogrulanamiyor); kosu durur, eyleme donuk alarm uretilir,
                TEK KREDI harcanmaz.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from core import ffmpeg_tools
from core.config import logger
from series import critic
from series.bible import REF_KINDS, data_dir, shots_dir

MANIFEST_VERSION = 1

# Release'e videonun yanina konan sidecar. Adi tag'den turetilmez ki indirme
# deseni tek ve sabit kalsin.
MANIFEST_ASSET_NAME = "episode_artifact.json"


@dataclass(frozen=True)
class Verdict:
    """Bir eserin kurtarilabilirligi. ``status`` yalniz dort koddan biridir."""

    status: str
    reason: str = ""
    path: Path | None = None
    manifest: dict | None = None

    @property
    def usable(self) -> bool:
        return self.status == "ok"


def enabled(bible) -> bool:
    """Seri kalici esere opt-in mi?

    Bayrak olmadan davranis BUGUNKUYLE birebir aynidir; boylece bu rock
    unnatural-lab disindaki uc kanalin davranisini degistirmez.
    """
    if bible is None:
        return False
    try:
        return bool(bible.data["series"].get("durable_artifacts"))
    except (AttributeError, KeyError, TypeError):
        return False


# --- kimlik ozetleri ---------------------------------------------------------

def _canonical(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _digest(value) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def plan_fingerprint(plan: dict) -> str:
    """Normalize edilmis TAM plan ozeti.

    ``doctrine_sha256`` planlar ARASINDA paylasilir ve ``ref_prompt_sha256``
    cekim prompt'larini disarida birakir; ikisi de tek basina kimlik degildir.
    Burada planin TAMAMI anahtar sirasindan bagimsiz kanonik JSON'a indirgenir.
    """
    return _digest(plan)


def _entity_reference(item: dict) -> dict:
    """Bir bible varliginin URETIME giren referans icerigi."""
    return {
        "id": item.get("id"),
        "ref_image_url": item.get("ref_image_url"),
        "voice_id": item.get("voice_id"),
        "character_id": item.get("character_id"),
        "descriptor": item.get("appearance") or item.get("desc") or item.get("bio"),
        "name": item.get("name"),
    }


def _shot_reference_urls(plan: dict) -> list[str]:
    """Cekimlerin kendi tasidigi referans URL'leri (sirali, tekrarsiz)."""
    seen: list[str] = []
    for shot in plan.get("shots") or []:
        if not isinstance(shot, dict):
            continue
        for key in ("image_urls", "ref_image_urls", "start_image_url", "ref_image_url"):
            value = shot.get(key)
            candidates = value if isinstance(value, list) else [value]
            for url in candidates:
                if isinstance(url, str) and url and url not in seen:
                    seen.append(url)
    return seen


def reference_fingerprint(bible, plan: dict) -> str:
    """REFERANS ICERIK ozeti.

    Motora giden referans, ImgBB URL'inin ARKASINDAKI baytlardir; yerel png
    yalniz bir onbellektir ve calisma dosyalariyla birlikte silinir. Bu yuzden
    ozet, uretimin gercekten tukettigi referans kimligine baglanir: URL kumesi,
    stil sozlesmesi ve referans prompt'unu belirleyen betimlemeler.
    """
    payload = {
        "art_style": bible.art_style,
        "style_ref_url": bible.style_ref_url,
        "aspect_ratio": bible.aspect_ratio,
        "resolution": bible.resolution,
        "engine": bible.engine,
        "omit_character_refs": bible.omit_character_refs,
        "plan_prop_ref_urls": plan.get("prop_ref_urls"),
        "plan_ref_prompt_sha256": plan.get("ref_prompt_sha256"),
        "plan_object_card": plan.get("object_card"),
        "shot_reference_urls": _shot_reference_urls(plan),
        "entities": {
            kind: sorted(
                (_entity_reference(item) for item in (bible.data.get(kind) or [])
                 if isinstance(item, dict)),
                key=lambda entry: str(entry.get("id")),
            )
            for kind in REF_KINDS
        },
    }
    return _digest(payload)


def qc_policy_fingerprint(bible) -> str:
    """QC POLITIKA parmak izi: bugun yururlukte olan kapilarin tam ayari."""
    return _digest(critic.qc_config(bible))


# --- QC gecis kaniti ---------------------------------------------------------

def _qc_events(slug: str) -> list[dict] | None:
    """Kalici qc_log.jsonl olaylarini oku. Okunamiyorsa ``None`` (belirsiz)."""
    path = data_dir(slug) / "qc_log.jsonl"
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None
    events: list[dict] = []
    for line in lines:
        try:
            event = json.loads(line)
        except (TypeError, ValueError):
            continue
        if isinstance(event, dict):
            events.append(event)
    return events


def _pass_event_for(events: list[dict], episode: int, shot: int,
                    content_hash: str) -> dict | None:
    for event in reversed(events):
        if (event.get("event") == "qc_pass"
                and event.get("content_sha256") == content_hash):
            try:
                same = (int(event.get("episode")) == int(episode)
                        and int(event.get("shot")) == int(shot))
            except (TypeError, ValueError):
                continue
            if same:
                return event
    return None


def collect_shot_evidence(slug: str, number: int, plan: dict, *,
                          qc_cfg: dict | None = None,
                          shots_root: Path | None = None) -> dict | None:
    """Kabul edilmis her cekim icin icerik ozeti + kalici ``qc_pass`` olayini topla.

    QC acikken kaniti olmayan TEK bir kabul edilmis cekim bile eseri
    kurtarilamaz yapar; bu durumda ``None`` doner (kanit toplanamadi).
    """
    root = Path(shots_root) if shots_root is not None else shots_dir(slug, number)
    events = _qc_events(slug) if qc_cfg else []
    if events is None:
        logger.error("qc_log.jsonl okunamadi; kalici eser kaniti toplanamadi")
        return None
    evidence: dict[str, dict] = {}
    for shot in plan.get("shots") or []:
        try:
            shot_number = int(shot.get("n"))
        except (TypeError, ValueError):
            return None
        clip = root / f"shot_{shot_number:02d}.mp4"
        if not (clip.exists() and clip.stat().st_size > 0):
            # Dusen cekim: bu bolum eksik cekimle teslim edildi, kanit beklenmez.
            continue
        content_hash = critic.content_sha256(clip)
        if not content_hash:
            return None
        entry: dict = {"content_sha256": content_hash, "clip": clip.name}
        if qc_cfg:
            pass_event = _pass_event_for(events, number, shot_number, content_hash)
            if pass_event is None:
                logger.error(
                    f"Cekim {shot_number} QC gecis kaniti yok; kalici eser "
                    "kimlige baglanamaz"
                )
                return None
            entry["qc_pass"] = pass_event
        evidence[str(shot_number)] = entry
    if not evidence:
        return None
    return evidence


def _evidence_holds(slug: str, number: int, manifest: dict,
                    qc_cfg: dict) -> tuple[bool, str]:
    """Kalicilastirlmis QC kanitini BUGUNKU politikaya gore yeniden yargila."""
    shots = manifest.get("shots")
    if not isinstance(shots, dict) or not shots:
        return False, "manifest QC kaniti tasimiyor"
    if not qc_cfg:
        return True, ""
    durable = _qc_events(slug)
    if durable is None:
        return False, "kalici qc_log.jsonl okunamadi"
    for key, entry in sorted(shots.items()):
        if not isinstance(entry, dict):
            return False, f"cekim {key} kanit kaydi bozuk"
        content_hash = entry.get("content_sha256")
        stored = entry.get("qc_pass")
        if not content_hash or not isinstance(stored, dict):
            return False, f"cekim {key} icin QC gecis kaniti yok"
        # 1) Esere yapisik kanit bugunku kapilari gecmeli.
        if not critic.qc_pass_exists(
            slug, number, int(key), content_hash, qc_cfg, events=[stored]
        ):
            return False, f"cekim {key} kaniti bugunku QC politikasini gecmiyor"
        # 2) Kalici defter (qc_log.jsonl) ayni gecisi dogrulamali.
        if _pass_event_for(durable, number, int(key), content_hash) is None:
            return False, f"cekim {key} icin kalici qc_log kaydi bulunamadi"
    return True, ""


# --- manifest ----------------------------------------------------------------

def build_manifest(slug: str, number: int, bible, plan: dict, video: Path, *,
                   shots_root: Path | None = None,
                   subtitle: str = "",
                   dropped_shots: list[int] | None = None,
                   coherence: dict | None = None) -> dict | None:
    """Videoyu bugunku plan/referans/QC kimligine baglayan manifesti uret."""
    video = Path(video)
    video_hash = critic.content_sha256(video)
    if not video_hash:
        logger.error(f"Kalici eser manifesti yazilamadi: {video} okunamadi")
        return None
    qc_cfg = critic.qc_config(bible)
    evidence = collect_shot_evidence(
        slug, number, plan, qc_cfg=qc_cfg, shots_root=shots_root
    )
    if evidence is None:
        return None
    return {
        "manifest_version": MANIFEST_VERSION,
        "slug": slug,
        "episode": int(number),
        "subtitle": str(subtitle or ""),
        "video_name": video.name,
        "video_sha256": video_hash,
        "video_bytes": video.stat().st_size,
        "plan_sha256": plan_fingerprint(plan),
        "reference_sha256": reference_fingerprint(bible, plan),
        "qc_policy_sha256": qc_policy_fingerprint(bible),
        "shots": evidence,
        # Teslim notlari kimlige GIRMEZ; ama geri yuklenen bolum de "eksik
        # cekimle yayinlandi" / "butunluk kusurlu" alarmlarini uretebilsin diye
        # eserle birlikte tasinir.
        "dropped_shots": [int(item) for item in (dropped_shots or [])],
        "coherence": coherence or None,
    }


def verify(slug: str, number: int, bible, plan: dict, manifest, video) -> Verdict:
    """Indirilen eseri bugunku bolum tanimina karsi yargila.

    KESIN uyusmazlik ``invalid`` (at ve yeniden uret); BELIRSIZ her sey
    ``blocked`` (dur ve alarm uret) doner.
    """
    if not isinstance(manifest, dict):
        return Verdict("blocked", "eser manifesti okunamadi")
    if manifest.get("manifest_version") != MANIFEST_VERSION:
        return Verdict(
            "blocked",
            f"manifest surumu taninmiyor: {manifest.get('manifest_version')!r}",
        )
    if str(manifest.get("slug")) != str(slug):
        return Verdict("invalid", "manifest baska seriye ait")
    try:
        if int(manifest.get("episode")) != int(number):
            return Verdict("invalid", "manifest baska bolume ait")
    except (TypeError, ValueError):
        return Verdict("blocked", "manifest bolum numarasi okunamadi")

    video = Path(video) if video is not None else None
    if video is None or not video.exists():
        return Verdict("blocked", "eser videosu indirilemedi")
    actual_hash = critic.content_sha256(video)
    if actual_hash is None:
        return Verdict("blocked", "eser videosu okunamadi")
    if actual_hash != manifest.get("video_sha256"):
        # Indirme BASARILI oldu ve baytlar kayitli ozetle uyusmuyor: bu kesin
        # bozulmadir, gecici bir depolama arizasi degildir.
        return Verdict("invalid", "eser videosu bozulmus (icerik ozeti uyusmuyor)")
    try:
        size = video.stat().st_size
    except OSError:
        return Verdict("blocked", "eser videosu boyutu okunamadi")
    if manifest.get("video_bytes") is not None and size != manifest["video_bytes"]:
        return Verdict("invalid", "eser videosu boyutu manifestle uyusmuyor")
    media_verdict = ffmpeg_tools.probe_media(video)
    if media_verdict is None:
        return Verdict("blocked", "eser videosu ffprobe ile dogrulanamadi")
    if media_verdict is False:
        return Verdict("invalid", "eser videosu okunabilir video akisi tasimiyor")

    if manifest.get("plan_sha256") != plan_fingerprint(plan):
        return Verdict("invalid", "plan degisti (normalize plan ozeti uyusmuyor)")
    if manifest.get("reference_sha256") != reference_fingerprint(bible, plan):
        return Verdict("invalid", "referans icerigi degisti")
    qc_cfg = critic.qc_config(bible)
    if manifest.get("qc_policy_sha256") != qc_policy_fingerprint(bible):
        return Verdict("invalid", "QC politikasi degisti")

    holds, reason = _evidence_holds(slug, number, manifest, qc_cfg)
    if not holds:
        # Kanit dogrulanamiyor: eser bozuk OLDUGU ispatlanmis degil, yalniz
        # yargilanamiyor. Yeniden uretmek taze kredi yakar, bu yuzden durulur.
        return Verdict("blocked", f"QC gecis kaniti dogrulanamadi: {reason}")

    return Verdict("ok", "", path=video, manifest=manifest)
