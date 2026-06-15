"""
Audio ID Kataloğu — Gemini Omni ses kimlikleri.

İki tür ses vardır:
  1. PRESET sesler  → küçük harf isimle doğrudan kullanılır (örn. "callirrhoe").
  2. ÖZEL sesler    → omni/audio/create ile üretilen kieAudioId (hex hash).

Bu dosya bağımlılıksızdır (rich vb. import etmez) — her yerden güvenle import edilir.
Karaktere uygun ses seçerken bu tabloya bakılır.
"""

# ─── 30 Preset Ses (Gemini Omni) ──────────────────────────────────────────────
# Her kayıt: id (API'de kullanılan), name (görünen ad), gender, description
PRESET_VOICES = [
    {"id": "achernar",      "name": "Achernar",      "gender": "female",     "description": "soft, high pitch"},
    {"id": "achird",        "name": "Achird",        "gender": "male",       "description": "friendly, mid pitch"},
    {"id": "algenib",       "name": "Algenib",       "gender": "male",       "description": "gravelly, low pitch"},
    {"id": "algieba",       "name": "Algieba",       "gender": "male",       "description": "easy-going, mid-low pitch"},
    {"id": "alnilam",       "name": "Alnilam",       "gender": "male",       "description": "firm, mid-low pitch"},
    {"id": "aoede",         "name": "Aoede",         "gender": "female",     "description": "breezy, mid pitch"},
    {"id": "autonoe",       "name": "Autonoe",       "gender": "female",     "description": "bright, mid pitch"},
    {"id": "callirrhoe",    "name": "Callirrhoe",    "gender": "female",     "description": "easy-going, mid pitch"},
    {"id": "charon",        "name": "Charon",        "gender": "male",       "description": "informative, lower pitch"},
    {"id": "despina",       "name": "Despina",       "gender": "female",     "description": "smooth, mid pitch"},
    {"id": "enceladus",     "name": "Enceladus",     "gender": "male",       "description": "breathy, lower pitch"},
    {"id": "erinome",       "name": "Erinome",       "gender": "female",     "description": "clear, mid pitch"},
    {"id": "fenrir",        "name": "Fenrir",        "gender": "male",       "description": "excitable, younger pitch"},
    {"id": "gacrux",        "name": "Gacrux",        "gender": "female",     "description": "mature, mid pitch"},
    {"id": "iapetus",       "name": "Iapetus",       "gender": "male",       "description": "clear, mid-low pitch"},
    {"id": "kore",          "name": "Kore",          "gender": "female",     "description": "firm, mid pitch"},
    {"id": "laomedeia",     "name": "Laomedeia",     "gender": "female",     "description": "upbeat, mid-high pitch"},
    {"id": "leda",          "name": "Leda",          "gender": "female",     "description": "youthful, mid-high pitch"},
    {"id": "orus",          "name": "Orus",          "gender": "male",       "description": "firm, mid-low pitch"},
    {"id": "puck",          "name": "Puck",          "gender": "male",       "description": "upbeat, mid pitch"},
    {"id": "pulcherrima",   "name": "Pulcherrima",   "gender": "ungendered", "description": "forward, mid-high pitch"},
    {"id": "rasalgethi",    "name": "Rasalgethi",    "gender": "male",       "description": "informative, mid pitch"},
    {"id": "sadachbia",     "name": "Sadachbia",     "gender": "male",       "description": "lively, low pitch"},
    {"id": "sadaltager",    "name": "Sadaltager",    "gender": "male",       "description": "knowledgeable, mid pitch"},
    {"id": "schedar",       "name": "Schedar",       "gender": "male",       "description": "even, mid-low pitch"},
    {"id": "sulafat",       "name": "Sulafat",       "gender": "female",     "description": "warm, mid pitch"},
    {"id": "umbriel",       "name": "Umbriel",       "gender": "male",       "description": "smooth, lower pitch"},
    {"id": "vindemiatrix",  "name": "Vindemiatrix",  "gender": "female",     "description": "gentle, mid pitch"},
    {"id": "zephyr",        "name": "Zephyr",        "gender": "female",     "description": "bright, mid-high pitch"},
    {"id": "zubenelgenubi", "name": "Zubenelgenubi", "gender": "male",       "description": "casual, mid-low pitch"},
]

# ─── İhsan'ın hazır özel sesleri (omni/audio/create ile üretilmiş kieAudioId'ler) ──
# Yeni özel ses üretilirse buraya eklenebilir.
CUSTOM_VOICES = [
    {"id": "9ff707aa7d2a487d87b7a2da59a33eeb", "name": "Bahçe Ses",
     "gender": "female", "description": "Bahçe bakımı anlatan, informatif kadın sesi · 'Merhaba, benim adım Nil'"},
]

PRESET_IDS = {v["id"] for v in PRESET_VOICES}


def get_voice(voice_id: str) -> dict | None:
    """id ile bir sesi bul (preset veya özel)."""
    if not voice_id:
        return None
    vid = voice_id.strip().lower()
    for v in PRESET_VOICES:
        if v["id"] == vid:
            return v
    for v in CUSTOM_VOICES:
        if v["id"] == voice_id.strip():
            return v
    return None


def is_preset(voice_id: str) -> bool:
    """Verilen id bir preset ses mi? (Aksi halde özel kieAudioId kabul edilir.)"""
    return bool(voice_id) and voice_id.strip().lower() in PRESET_IDS


def list_voices(gender: str | None = None) -> list[dict]:
    """Preset sesleri (opsiyonel cinsiyet filtresiyle) listele."""
    if gender:
        g = gender.strip().lower()
        return [v for v in PRESET_VOICES if v["gender"] == g]
    return list(PRESET_VOICES)


def format_table() -> str:
    """Sesleri düz metin tablo olarak döndür (rich bağımlılığı olmadan)."""
    lines = [f"{'ID':<15} {'Cinsiyet':<11} Açıklama", "-" * 60]
    for v in PRESET_VOICES:
        lines.append(f"{v['id']:<15} {v['gender']:<11} {v['description']}")
    if CUSTOM_VOICES:
        lines.append("")
        lines.append("Özel sesler (kieAudioId):")
        for v in CUSTOM_VOICES:
            lines.append(f"{v['id']:<34} {v['name']} — {v['description']}")
    return "\n".join(lines)


if __name__ == "__main__":
    print(format_table())
