"""FROM SCRATCH ilk deneme prompt yuzeylerini denetler."""

import argparse
import json
import pathlib
import re
import sys
import unicodedata


PROHIBITED_NOUNS = (
    "signage",
    "sign",
    "billboard",
    "poster",
    "banner",
    "scoreboard",
    "lettering",
    "screen",
    "monitor",
    "display",
    "logo",
    "brand mark",
    "license plate",
    "number plate",
    "branded machinery",
    "camera",
    "tripod",
    "clapperboard",
    "film crew",
)

_NEGATION_WORDS = (
    "never",
    "no",
    "not",
    "nor",
    "none",
    "avoid",
    "without",
    "exclude",
    "lacking",
    "devoid",
    "only",
    "sole",
)
_CONTINUITY_WORDS = (
    "drift",
    "composition",
    "consistency",
    "wardrobe",
    "appearance",
    "style",
    "geography",
    "lock",
    "continuity",
)
_PENDING_PARTS = range(6, 11)


def normalize(text):
    """Metni NFKC ve ASCII tabanli sozcuk taramasina hazirlar."""
    value = unicodedata.normalize("NFKC", str(text or "")).lower()
    value = value.replace("’", "'").replace("‘", "'")
    return re.sub(r"[^a-z0-9'-]+", " ", value).strip()


def _words(text):
    """Normalize edilmis metindeki sayilabilir sozcukleri dondurur."""
    return re.findall(r"[a-z0-9]+(?:['-][a-z0-9]+)*", normalize(text))


def word_count(text):
    """Plan kurallarindaki sozcuk sayisini hesaplar."""
    return len(_words(text))


def find_negations(text):
    """Yasak veya olumsuzlama dilini yanlis pozitif uretmeden bulur."""
    value = normalize(text)
    found = []
    for word in _NEGATION_WORDS:
        if re.search(rf"\b{re.escape(word)}\b", value):
            found.append(word)
    if re.search(r"\bfree\s+of\b", value):
        found.append("free of")
    if re.search(r"\b[a-z0-9']+-free\b", value):
        found.append("-free")
    if re.search(r"\bdon't\b", value):
        found.append("don't")
    return found


def find_prohibited_nouns(text):
    """Kanonik sahne nesnelerini tekil ve cogul bicimleriyle bulur."""
    value = normalize(text)
    found = []
    for noun in PROHIBITED_NOUNS:
        root = re.escape(noun).replace(r"\ ", r"\s+")
        if re.search(rf"\b{root}s?\b", value, re.IGNORECASE):
            found.append(noun)
    return found


def repetition_ratio(prefix, body, size=8):
    """Onek ile govdenin n-gram kume cakisma oranini hesaplar."""
    prefix_words = _words(prefix)
    body_words = _words(body)
    prefix_grams = {
        tuple(prefix_words[index:index + size])
        for index in range(max(0, len(prefix_words) - size + 1))
    }
    body_grams = {
        tuple(body_words[index:index + size])
        for index in range(max(0, len(body_words) - size + 1))
    }
    if not body_grams:
        return 0.0
    return len(prefix_grams & body_grams) / len(body_grams)


def split_prompt(prompt, configured_prefix=""):
    """Motorun ekledigi onegi govdeden ayirir, eski onegi de taniyabilir."""
    content = str(prompt or "").strip()
    prefix = str(configured_prefix or "").strip()
    if prefix and content.startswith(prefix):
        remainder = content[len(prefix):]
        if not remainder or remainder[0].isspace():
            return prefix, remainder.strip()
    if "\n\n" in content:
        stored_prefix, body = content.split("\n\n", 1)
        return stored_prefix.strip(), body.strip()
    return prefix, content


def _violation(surface, rule, detail, path="", shot=None):
    """Makine ve insan tarafindan okunabilir tek ihlal kaydi kurar."""
    return {
        "surface": surface,
        "rule": rule,
        "detail": detail,
        "path": str(path),
        "shot": shot,
    }


def lint_art_style(text):
    """Art style alanindaki olumsuzlama ve sahne nesnelerini denetler."""
    violations = []
    hits = find_negations(text)
    if hits:
        violations.append(_violation("art_style", "negation", ", ".join(hits)))
    nouns = find_prohibited_nouns(text)
    if nouns:
        violations.append(_violation(
            "art_style", "prohibited_noun", ", ".join(nouns)
        ))
    return violations


def lint_qc_notes(text):
    """QC notunda sureklilik ile artifact skorunun karismasini denetler."""
    violations = []
    sentences = re.split(r"(?<=[.!?])\s+|\n+", str(text or ""))
    for number, sentence in enumerate(sentences, start=1):
        value = normalize(sentence)
        if not re.search(r"\bartifact\b", value):
            continue
        hits = [
            word for word in _CONTINUITY_WORDS
            if re.search(rf"\b{re.escape(word)}\b", value)
        ]
        if hits:
            violations.append(_violation(
                "qc.notes",
                "score_contamination",
                f"cumle {number}: {', '.join(hits)}",
            ))
    return violations


def lint_shot_plan(shot_plan):
    """Sabit oneklerin dil, nesne ve 45 sozcuk sinirini denetler."""
    violations = []
    for number, prefix in enumerate(shot_plan or [], start=1):
        hits = find_negations(prefix)
        if hits:
            violations.append(_violation(
                "shot_plan", "negation", ", ".join(hits), shot=number
            ))
        nouns = find_prohibited_nouns(prefix)
        if nouns:
            violations.append(_violation(
                "shot_plan", "prohibited_noun", ", ".join(nouns), shot=number
            ))
        count = word_count(prefix)
        if count > 45:
            violations.append(_violation(
                "shot_plan", "length", f"{count} sozcuk, sinir 45", shot=number
            ))
    return violations


def lint_plan_data(plan, art_style, shot_plan, path=""):
    """Tek bekleyen plani cozulmus yuk ve yalniz govde kurallariyla denetler."""
    violations = []
    shots = plan.get("shots") if isinstance(plan, dict) else None
    if not isinstance(shots, list):
        return [_violation("pending_plan", "format", "shots listesi yok", path)]
    for index, shot in enumerate(shots, start=1):
        if not isinstance(shot, dict):
            violations.append(_violation(
                "pending_plan", "format", "cekim nesne degil", path, index
            ))
            continue
        number = shot.get("n", index)
        configured_prefix = shot_plan[index - 1] if index <= len(shot_plan) else ""
        prompt = str(shot.get("prompt") or "")
        prefix, body = split_prompt(prompt, configured_prefix)
        resolved = f"{art_style}\n\n{prompt}" if art_style else prompt

        negations = find_negations(resolved)
        if negations:
            violations.append(_violation(
                "pending_plan", "negation", ", ".join(negations), path, number
            ))
        nouns = find_prohibited_nouns(body)
        if nouns:
            violations.append(_violation(
                "pending_plan", "prohibited_noun", ", ".join(nouns), path, number
            ))
        count = word_count(body)
        if count > 60:
            violations.append(_violation(
                "pending_plan", "length", f"{count} sozcuk, sinir 60", path, number
            ))
        ratio = repetition_ratio(prefix, body)
        if ratio > 0.30:
            violations.append(_violation(
                "pending_plan", "repetition", f"oran {ratio:.3f}, sinir 0.300", path, number
            ))
    return violations


def lint_series(series_dir):
    """Alanlari ve yalniz part06 ile part10 arasindaki bekleyen planlari denetler."""
    root = pathlib.Path(series_dir)
    try:
        bible = json.loads((root / "bible.json").read_text(encoding="utf-8"))
        series = json.loads((root / "series.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return [_violation("config", "read", f"veri okunamadi: {error}", root)]

    art_style = str(bible.get("art_style") or "")
    qc_notes = str(((bible.get("series") or {}).get("qc") or {}).get("notes") or "")
    shot_plan = list(((series.get("auto_replenish") or {}).get("shot_plan") or []))
    violations = []
    violations.extend(lint_art_style(art_style))
    violations.extend(lint_qc_notes(qc_notes))
    violations.extend(lint_shot_plan(shot_plan))

    for number in _PENDING_PARTS:
        path = root / "plans" / f"part{number:02d}.json"
        try:
            plan = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            violations.append(_violation(
                "pending_plan", "read", f"plan okunamadi: {error}", path
            ))
            continue
        violations.extend(lint_plan_data(plan, art_style, shot_plan, path))
    return violations


def _print_report(series_dir, violations):
    """Denetim sonucunu yuzey ve bekleyen plan olarak ayri yazar."""
    print(f"RF prompt denetimi: {pathlib.Path(series_dir)}")
    for surface in ("art_style", "qc.notes", "shot_plan"):
        count = sum(item["surface"] == surface for item in violations)
        print(f"{surface}: {count} ihlal")
    pending = [item for item in violations if item["surface"] == "pending_plan"]
    for item in pending:
        location = pathlib.Path(item["path"]).name
        if item["shot"] is not None:
            location += f" cekim {item['shot']}"
        print(f"HATA {location} [{item['rule']}]: {item['detail']}")
    other = [
        item for item in violations
        if item["surface"] not in {"art_style", "qc.notes", "shot_plan", "pending_plan"}
    ]
    for item in other:
        print(f"HATA {item['surface']} [{item['rule']}]: {item['detail']}")
    print(f"Bekleyen planlar: {len(pending)} ihlal")
    print(f"Toplam: {len(violations)} ihlal")


def main(argv=None):
    """Komut satiri girisini calistirir ve ihlalde sifir disi doner."""
    parser = argparse.ArgumentParser(
        description="FROM SCRATCH ilk deneme prompt yuzeylerini denetler."
    )
    parser.add_argument("series_dir", type=pathlib.Path)
    args = parser.parse_args(argv)
    violations = lint_series(args.series_dir)
    _print_report(args.series_dir, violations)
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
