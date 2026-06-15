"""
Seri meta verisi — çok part'lı (uzun soluklu) dizinin durumu.

output/series/<slug>/series.json — sıradaki part, yayın durumu, başlık şablonu.
output/series/<slug>/plans/partNN.json — önceden yazılmış part planları (her biri bir bölüm).

Başlık kuralı: "{base_title} — Part N"  → izleyici nerede kaldığını görür.
Diyaloglar İngilizce yazılır (canlı yayın için).
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from core.config import logger
from .bible import data_dir, ensure_dirs

DEFAULT_PLATFORMS = ["youtube", "instagram", "tiktok"]


def series_meta_path(slug: str) -> Path:
    return data_dir(slug) / "series.json"


def plans_dir(slug: str) -> Path:
    return data_dir(slug) / "plans"


def part_plan_path(slug: str, n: int) -> Path:
    return plans_dir(slug) / f"part{int(n):02d}.json"


class SeriesMeta:
    """series.json'u saran ince yardımcı sınıf."""

    def __init__(self, data: dict):
        self.data = data

    # -- skaler alanlar --
    @property
    def slug(self) -> str: return self.data["slug"]
    @property
    def base_title(self) -> str: return self.data.get("base_title", self.slug)
    @property
    def logline(self) -> str: return self.data.get("logline", "")
    @property
    def language(self) -> str: return self.data.get("language", "en")
    @property
    def upload_profile(self) -> str: return self.data.get("upload_profile", "")
    @property
    def platforms(self) -> list[str]: return self.data.get("platforms", DEFAULT_PLATFORMS)
    @property
    def hashtags(self) -> str: return self.data.get("hashtags", "")
    @property
    def total_parts(self) -> int: return int(self.data.get("total_parts", 0))
    @property
    def next_part(self) -> int: return int(self.data.get("next_part", 1))
    @property
    def status(self) -> str: return self.data.get("status", "active")

    # -- başlık / açıklama (Part N) --
    def title_for(self, n: int, subtitle: str = "") -> str:
        t = f"{self.base_title} — Part {n}"
        if subtitle:
            t += f": {subtitle}"
        return t[:100]

    def description_for(self, n: int, subtitle: str = "") -> str:
        lines = [f"{self.base_title} — Part {n} of {self.total_parts}."]
        if subtitle:
            lines.append(subtitle)
        if self.logline:
            lines.append(self.logline)
        lines.append("\n▶ New part every day — follow the full series!")
        if self.hashtags:
            lines.append("\n" + self.hashtags)
        return "\n".join(lines)[:4900]

    # -- part durumu --
    def parts(self) -> dict:
        return self.data.setdefault("parts", {})

    def get_part(self, n: int) -> dict:
        return self.parts().setdefault(str(n), {"status": "planned"})

    def mark_produced(self, n: int, video: str | Path, subtitle: str = ""):
        p = self.get_part(n)
        p["status"] = "produced"
        p["video"] = str(video)
        if subtitle:
            p["subtitle"] = subtitle

    def mark_published(self, n: int, platforms_ok: list[str]):
        p = self.get_part(n)
        p["status"] = "published"
        p["platforms_ok"] = platforms_ok
        p["published_at"] = datetime.now(timezone.utc).isoformat()

    def advance(self):
        self.data["next_part"] = self.next_part + 1
        if self.next_part > self.total_parts:
            self.data["status"] = "completed"

    # -- IO --
    def save(self) -> Path:
        ensure_dirs(self.slug)
        plans_dir(self.slug).mkdir(parents=True, exist_ok=True)
        p = series_meta_path(self.slug)
        p.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")
        return p

    @classmethod
    def create(cls, slug: str, base_title: str, total_parts: int,
               logline: str = "", upload_profile: str = "",
               platforms: list[str] | None = None, hashtags: str = "") -> "SeriesMeta":
        data = {
            "slug": slug,
            "base_title": base_title,
            "logline": logline,
            "language": "en",
            "upload_profile": upload_profile,
            "platforms": platforms or DEFAULT_PLATFORMS,
            "hashtags": hashtags,
            "total_parts": total_parts,
            "next_part": 1,
            "status": "active",
            "parts": {},
        }
        ensure_dirs(slug)
        plans_dir(slug).mkdir(parents=True, exist_ok=True)
        return cls(data)

    @classmethod
    def load(cls, slug: str) -> "SeriesMeta | None":
        p = series_meta_path(slug)
        if not p.exists():
            logger.error(f"❌ series.json bulunamadı: {p}")
            return None
        return cls(json.loads(p.read_text(encoding="utf-8")))


def list_active_series() -> list[str]:
    """series_data/ altında status=active olan dizilerin slug listesi."""
    from .bible import SERIES_DATA_DIR
    active = []
    if not SERIES_DATA_DIR.exists():
        return active
    for d in sorted(SERIES_DATA_DIR.iterdir()):
        if d.is_dir() and series_meta_path(d.name).exists():
            m = SeriesMeta.load(d.name)
            if m and m.status == "active" and m.next_part <= m.total_parts:
                active.append(d.name)
    return active
