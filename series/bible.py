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

    # -- üretim motoru (çok-motorlu) --
    @property
    def engine(self) -> str:
        """Varsayılan üretim motoru: 'omni' (karakter+ses) | 'seedance' | 'veo3_fast' |
        'veo3_lite' | 'kling' (ucuz görsel). Çekim bazında shot['engine'] ile override edilir."""
        return self.data["series"].get("engine", "omni")

    @property
    def chain_frames(self) -> bool:
        """True ise 'bitmeyen yolculuk': her çekimin son karesi sonraki çekimin (ve sonraki
        bölümün ilk çekiminin) başlangıç karesi olur → kesintisiz akış."""
        return bool(self.data["series"].get("chain_frames", False))

    @property
    def chain_scope(self) -> str:
        """Zincirin kapsamı: "series" (varsayılan) = bölümün son karesi SONRAKİ BÖLÜME de
        taşınır (series.json.last_frame_url); "episode" = zincir yalnız bölüm İÇİNDE çalışır,
        her bölüm temiz/yeni bir sahneyle açılır (sidecar yazılmaz, last_frame_url okunmaz).
        Bölümleri farklı mekân/tema olan kanallar için "episode" şarttır — yoksa yeni bölümün
        ilk çekimi önceki bölümün mekânından başlar."""
        v = str(self.data["series"].get("chain_scope", "series")).strip().lower()
        return v if v in ("series", "episode") else "series"

    @property
    def narration(self) -> dict:
        """Anlatım katmanı ayarı: {'channel': 'galactic_experiment'|'shadowedhistory'|...}.
        Boşsa anlatım eklenmez (motorun native sesi kullanılır)."""
        return self.data.get("narration") or {}

    @property
    def music(self) -> bool:
        """True ise arka plan müziği eklenir (galactic/shadowedhistory/aimagine atmosferi)."""
        return bool(self.data.get("music", False))

    @property
    def native_audio(self) -> bool:
        """Ucuz motorun (Seedance) kendi sesini üretsin mi? Anlatım-odaklı kanallarda
        False önerilir (anlatım+müzik temiz kalsın); 'trip' kanalında serbest."""
        return bool(self.data["series"].get("native_audio", True))

    @property
    def micro_trim(self) -> float:
        """Kurgu öncesi her çekimin BAŞINDAN ve SONUNDAN kırpılacak saniye.
        AI klipleri kendi içinde 'poz → aksiyon → poz' yaşar; uçlar kırpılınca her
        kesme hareketin ORTASINA düşer → bölüm tek akış gibi okunur (en ucuz
        akıcılık kazancı). 0/yok = kapalı; true = 0.30s. Örn: "micro_trim": 0.25"""
        v = self.data["series"].get("micro_trim", 0)
        if v is True:
            return 0.3
        try:
            return max(0.0, float(v))
        except (TypeError, ValueError):
            return 0.0

    @property
    def cctv(self) -> dict:
        """Güvenlik kamerası sunum katmanı (opt-in). Etkinse her çekim kurgudan önce
        CCTV gibi giydirilir: işleyen saat + tarih + kamera etiketi + REC + grain +
        düşük fps (AI kusurlarını da maskeler). Bible'daki değerler varsayılandır;
        plan['cctv'] (kamera/tarih bölüme özgü) ve shot['cam_time']/shot['caption']
        çekim bazında zenginleştirir.
        Örn: "cctv": {"enabled": true, "fps": 18, "grain": 7}"""
        v = self.data["series"].get("cctv") or {}
        return v if isinstance(v, dict) and v.get("enabled") else {}

    @property
    def hook_teaser(self) -> dict:
        """Açılış kancası (opt-in): bölümün DORUK çekiminden kısa bir kesit videonun
        en başına eklenir ('bekle, ne oluyor?' etkisi — ilk 2 saniye kuralı).
        plan['hook_shot'] doruk çekimin n'sini söyler (yoksa sondan bir önceki).
        Örn: "hook_teaser": {"enabled": true, "duration": 1.4, "offset_in_shot": 1.6}"""
        v = self.data["series"].get("hook_teaser") or {}
        return v if isinstance(v, dict) and v.get("enabled") else {}

    @property
    def audio_smooth(self) -> bool:
        """True ise çekim sınırlarında ses YUMUŞATILIR: her çekimin sesi loudness
        eşitlenir + kısa afade ile in/out yapılır → geçişlerde 'pop'/seviye sıçraması
        ve ses boşluğu olmaz. Atmosfer/müzik kanalları için idealdir.
        Diyalog kanallarında (ör. viral-detective) KAPALI olmalı — afade söz
        baş/sonunu kırpabilir; orada akıcılığı sürekli diyalog zaten sağlar.
        Varsayılan: müzik açıksa açık."""
        return bool(self.data["series"].get("audio_smooth", self.music))

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
