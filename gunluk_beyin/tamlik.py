"""Tamlik modulu: yayinlanmis bolumlerin uretim tamligini kontrol eder."""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Union

# Olculen 15 gercek bolumde, tam bolumler planlanan surelerin %93-95'inde,
# shot dusurulmus bolumler ise %46-48'inde kalmistir. 0.70 bu boslukta oturur.
COMPLETE_DURATION_RATIO = 0.70

PRODUCTION_DIRS = {
    "unnatural-lab": "sentinal_ihsan/unnatural-lab",
    "event-horizon": "galactic_experience/event-horizon",
    "flashpoints": "shadowedhistory/flashpoints",
    "aimagine-fear": None,
}


def production_root() -> Path:
    """Repo kokunu dondurur. BEYIN_URETIM_KOK env varsa onu, yoksa cwd'nin parent'ini kullanir.
    Cagri aninda hesaplanir, import aninda degil."""
    env_root = os.environ.get("BEYIN_URETIM_KOK")
    if env_root:
        return Path(env_root).resolve()
    # beyin cwd=<repo>/gunluk_beyin oldugu icin parent = <repo>
    return Path.cwd().parent.resolve()


def production_dir(channel: str, root: Optional[Union[str, Path]] = None) -> Optional[Path]:
    """Kanalin uretim klasorunun mutlak yolunu dondurur. Kanal bilinmiyorsa veya
    PRODUCTION_DIRS degeri None ise None dondurur."""
    if root is None:
        root = production_root()
    else:
        root = Path(root).resolve()

    rel_path = PRODUCTION_DIRS.get(channel)
    if rel_path is None:
        return None
    return (root / rel_path).resolve()


def _safe_read_json(path: Path) -> Optional[Any]:
    """JSON dosyasini guvenli okur. Herhangi bir hata olursa None dondurur."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def _parse_duration(val: Any) -> float:
    """Sure degerini float'a cevirir. Basarisiz olursa 0.0 dondurur."""
    try:
        return float(val)
    except (TypeError, ValueError):
        return 0.0


def _read_planned_seconds(prod_dir: Path, part: int) -> Optional[float]:
    """Plans/partNN.json dosyasindan planlanan toplam sureyi (saniye) okur.
    Dosya yoksa veya okunamazsa None dondurur."""
    plan_file = prod_dir / "plans" / f"part{part:02d}.json"
    data = _safe_read_json(plan_file)
    if not isinstance(data, dict):
        return None
    shots = data.get("shots")
    if not isinstance(shots, list):
        return None
    total = 0.0
    for shot in shots:
        if isinstance(shot, dict):
            total += _parse_duration(shot.get("duration"))
    return total


def episode_completeness(
    channel: str,
    root: Optional[Union[str, Path]] = None,
    durations: Optional[Dict[str, float]] = None
) -> Dict[str, Dict[str, Any]]:
    """Kanalin yayinlanmis bolumlerinin tamlik durumunu dondurur.

    Returns:
        {video_id: {"complete": True|False|None,
                    "reason": str,
                    "ratio": float|None,
                    "part": int|None}}
    """
    result: Dict[str, Dict[str, Any]] = {}

    prod_dir = production_dir(channel, root)
    if prod_dir is None or not prod_dir.exists():
        return result

    # a. published.json oku
    published_data = _safe_read_json(prod_dir / "published.json")
    if not isinstance(published_data, list):
        return result

    # video_id -> part eslesmesi
    video_to_part: Dict[str, int] = {}
    for entry in published_data:
        if not isinstance(entry, dict):
            continue
        results = entry.get("results")
        if not isinstance(results, dict):
            continue
        video_id = results.get("youtube")
        part = entry.get("part")
        if video_id and isinstance(part, int):
            video_to_part[video_id] = part

    if not video_to_part:
        return result

    # b. series.json oku
    series_data = _safe_read_json(prod_dir / "series.json")
    parts_info: Dict[str, Dict[str, Any]] = {}
    if isinstance(series_data, dict):
        parts = series_data.get("parts")
        if isinstance(parts, dict):
            parts_info = parts

    # c. Her video icin karar ver
    for video_id, part in video_to_part.items():
        part_str = str(part)
        part_info = parts_info.get(part_str, {}) if isinstance(parts_info, dict) else {}

        # dropped_shots kontrolu
        dropped_shots = part_info.get("dropped_shots")
        if isinstance(dropped_shots, list) and dropped_shots:
            result[video_id] = {
                "complete": False,
                "reason": f"dropped_shots={dropped_shots}",
                "ratio": None,
                "part": part,
            }
            continue

        # Planlanan sure
        planned_seconds = _read_planned_seconds(prod_dir, part)

        # Olculen sure
        measured_seconds = None
        if durations and video_id in durations:
            measured_seconds = durations[video_id]

        if planned_seconds is not None and planned_seconds > 0 and measured_seconds is not None:
            ratio = measured_seconds / planned_seconds
            if ratio < COMPLETE_DURATION_RATIO:
                result[video_id] = {
                    "complete": False,
                    "reason": f"sure orani {ratio:.2f} < {COMPLETE_DURATION_RATIO}",
                    "ratio": ratio,
                    "part": part,
                }
            else:
                result[video_id] = {
                    "complete": True,
                    "reason": f"sure orani {ratio:.2f}",
                    "ratio": ratio,
                    "part": part,
                }
        else:
            result[video_id] = {
                "complete": None,
                "reason": "uretim kaydi eksik",
                "ratio": None,
                "part": part,
            }

    return result


def read_subject_labels(
    channel: str,
    brain_root: Optional[Union[str, Path]] = None
) -> Dict[str, str]:
    """<brain_root>/kanallar/<channel>/ozne.json dosyasini okur ve
    sadece SEY, OLAY, KISI etiketlerini tutar."""
    allowed = {"SEY", "OLAY", "KISI"}
    result: Dict[str, str] = {}

    if brain_root is None:
        brain_root = Path.cwd()
    else:
        brain_root = Path(brain_root)

    label_file = brain_root / "kanallar" / channel / "ozne.json"
    data = _safe_read_json(label_file)
    if not isinstance(data, dict):
        return result

    for video_id, label in data.items():
        if isinstance(label, str) and label in allowed:
            result[video_id] = label

    return result