"""
Series Bible — dizinin referans hafızası.

Tek dosyada tutulur: output/series/<slug>/bible/bible.json
İçerik: sanat tarzı + karakterler + ortamlar + aksesuarlar (görsel URL'leri ve
Omni characterId / kieAudioId değerleri cache'lenir, tekrar üretilmez).

Klasör yapısı:
  output/series/<slug>/
    bible/ bible.json  characters/  environments/  props/  style/
    episodes/ ep01/ shots/  ep01.mp4
"""

import json
from pathlib import Path

from core.config import SERIES_DIR, PROJECT_ROOT, OMNI_DEFAULT_ASPECT, OMNI_DEFAULT_RESOLUTION, logger

REF_KINDS = ("characters", "environments", "props")

# KAYNAK (git'te tutulur): bible.json, series.json, plans/, raporlar
SERIES_DATA_DIR = PROJECT_ROOT / "series_data"
# ARTEFAKT (gitignore: output/): üretilen videolar, çekimler, referans görselleri


# ─── Yol yardımcıları ──────────────────────────────────────────────────────────

def data_dir(slug: str) -> Path:
    """Git'te tutulan kaynak klasörü (bible.json, series.json, plans/, rapor)."""
    return SERIES_DATA_DIR / slug


def series_dir(slug: str) -> Path:
    """Artefakt kökü (output/series/<slug>) — gitignore'da."""
    return SERIES_DIR / slug


def bible_path(slug: str) -> Path:
    return data_dir(slug) / "bible.json"


def refs_dir(slug: str, kind: str) -> Path:
    """Üretilen referans görsellerinin yerel kopyası (artefakt)."""
    return series_dir(slug) / "refs" / kind


def episodes_dir(slug: str) -> Path:
    return series_dir(slug) / "episodes"


def episode_dir(slug: str, number: int) -> Path:
    return episodes_dir(slug) / f"ep{int(number):02d}"


def shots_dir(slug: str, number: int) -> Path:
    return episode_dir(slug, number) / "shots"


def ensure_dirs(slug: str) -> None:
    """Dizi için gereken tüm klasörleri oluştur (kaynak + artefakt)."""
    (data_dir(slug) / "plans").mkdir(parents=True, exist_ok=True)
    for kind in REF_KINDS:
        refs_dir(slug, kind).mkdir(parents=True, exist_ok=True)
    episodes_dir(slug).mkdir(parents=True, exist_ok=True)


# ─── Bible nesnesi ─────────────────────────────────────────────────────────────

class Bible:
    """bible.json'u saran ince yardımcı sınıf."""

    def __init__(self, data: dict):
        self.data = data

    # -- meta --
    @property
    def slug(self) -> str:
        return self.data["series"]["slug"]

    @property
    def title(self) -> str:
        return self.data["series"].get("title", self.slug)

    @property
    def art_style(self) -> str:
        return self.data.get("art_style", "")

    @property
    def style_ref_url(self) -> str | None:
        return self.data.get("style_ref_url")

    @property
    def aspect_ratio(self) -> str:
        return self.data["series"].get("aspect_ratio", OMNI_DEFAULT_ASPECT)

    @property
    def resolution(self) -> str:
        return self.data["series"].get("resolution", OMNI_DEFAULT_RESOLUTION)

    # -- referanslar --
    @property
    def characters(self) -> list[dict]:
        return self.data.setdefault("characters", [])

    @property
    def environments(self) -> list[dict]:
        return self.data.setdefault("environments", [])

    @property
    def props(self) -> list[dict]:
        return self.data.setdefault("props", [])

    def items(self, kind: str) -> list[dict]:
        return self.data.setdefault(kind, [])

    def get(self, kind: str, item_id: str) -> dict | None:
        for it in self.data.get(kind, []):
            if it.get("id") == item_id:
                return it
        return None

    def get_character(self, char_id: str) -> dict | None:
        return self.get("characters", char_id)

    # -- kayıt --
    def save(self) -> Path:
        ensure_dirs(self.slug)
        p = bible_path(self.slug)
        p.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")
        logger.info(f"💾 Bible kaydedildi: {p}")
        return p

    # -- oluştur / yükle --
    @classmethod
    def create(cls, slug: str, title: str = "", art_style: str = "",
               aspect_ratio: str | None = None, resolution: str | None = None) -> "Bible":
        data = {
            "series": {
                "slug": slug,
                "title": title or slug,
                "aspect_ratio": aspect_ratio or OMNI_DEFAULT_ASPECT,
                "resolution": resolution or OMNI_DEFAULT_RESOLUTION,
            },
            "art_style": art_style,
            "style_ref_url": None,
            "characters": [],
            "environments": [],
            "props": [],
        }
        ensure_dirs(slug)
        return cls(data)

    @classmethod
    def load(cls, slug: str) -> "Bible | None":
        p = bible_path(slug)
        if not p.exists():
            logger.error(f"❌ Bible bulunamadı: {p}")
            return None
        return cls(json.loads(p.read_text(encoding="utf-8")))


def resolve_voice_id(character: dict) -> str | None:
    """Karakterin Omni'de kullanılacak ses kimliğini döndür.
    Özel ses üretildiyse kieAudioId, aksi halde preset audio_id.
    """
    voice = character.get("voice") or {}
    return voice.get("kie_audio_id") or voice.get("audio_id")
