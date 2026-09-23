"""Deterministic engagement text selection for automatic series publishes."""

from __future__ import annotations


def valid_engagement_question(text: object) -> bool:
    """Return whether *text* is safe and useful as a short viewer question."""
    if not isinstance(text, str):
        return False
    value = text.strip()
    lowered = value.lower()
    return (
        8 <= len(value) <= 200
        and "?" in value
        and "#" not in value
        and "http" not in lowered
        and "www." not in lowered
    )


def engagement_block(series_cfg) -> dict:
    """series.json 'engagement' blogu; yoksa ya da sozluk degilse bos sozluk.

    Bozuk bir blok (true, metin, liste) ASLA kosuyu durdurmaz: etkilesim
    kapali sayilir ve seri bugunku gibi yayinlanir.
    """
    block = series_cfg.get("engagement") if isinstance(series_cfg, dict) else None
    return block if isinstance(block, dict) else {}


def _rotated_pool_value(series_cfg: dict, pool_name: str, part_n: int) -> str:
    pool = engagement_block(series_cfg).get(pool_name) or []
    if not isinstance(pool, list) or not pool:
        return ""
    try:
        index = (int(part_n) - 1) % len(pool)
    except (TypeError, ValueError):
        return ""
    value = pool[index]
    return value.strip() if valid_engagement_question(value) else ""


def pick_first_comment(plan: dict, series_cfg: dict, part_n: int) -> str:
    """Prefer a valid episode-specific comment, then rotate the series pool.

    OPT-IN: engagement blogu olmayan seri planinda first_comment olsa bile
    (Gemini istenmeden eklemis olabilir) yorum GONDERMEZ.
    """
    if not engagement_block(series_cfg):
        return ""
    planned = plan.get("first_comment") if isinstance(plan, dict) else None
    if valid_engagement_question(planned):
        return planned.strip()
    return _rotated_pool_value(series_cfg, "first_comment_pool", part_n)


def pick_caption_question(series_cfg: dict, part_n: int) -> str:
    """Rotate the configured caption-question pool for this part."""
    return _rotated_pool_value(series_cfg, "caption_question_pool", part_n)


def insert_caption_question(caption: str, question: str) -> str:
    """Insert *question* before the trailing hashtag block unless the body asks one."""
    if not question or not valid_engagement_question(question):
        return caption

    nl = "\n"
    lines = caption.splitlines()
    # Sondaki etiket BLOGUNUN ilk satirini bul: bos satirlar ve '#' ile baslayan
    # satirlar geriye dogru atlanir. Etiketler birden fazla satira yayilsa bile
    # soru bloklarin ARASINA degil, blogun ONUNE girer.
    hashtag_index = None
    for index in range(len(lines) - 1, -1, -1):
        stripped = lines[index].strip()
        if stripped.startswith("#"):
            hashtag_index = index
        elif stripped:
            break
    body = nl.join(lines[:hashtag_index] if hashtag_index is not None else lines)
    if "?" in body:
        return caption

    if hashtag_index is None:
        return caption.rstrip() + nl * 2 + question if caption.strip() else question

    before = nl.join(lines[:hashtag_index]).rstrip()
    hashtags = nl.join(lines[hashtag_index:]).strip(nl)
    parts = [p for p in (before, question, hashtags) if p]
    return (nl * 2).join(parts)
