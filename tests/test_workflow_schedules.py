import json
import re
from pathlib import Path


def get_active_crons(workflow_text: str) -> list[str]:
    """
    Return list of ACTIVE cron expressions in a workflow file text.
    A cron line is ACTIVE only if the FIRST non-whitespace character is NOT '#'.
    Also strips trailing inline comments (first '#' not inside quotes) before matching.
    Handles single-quoted, double-quoted, and unquoted cron values.
    """
    active = []
    # Match cron: followed by optional whitespace, then either:
    # - single-quoted value: '...'
    # - double-quoted value: "..."
    # - unquoted value: 5 space-separated fields (cron expression)
    cron_pattern = re.compile(r"cron:\s*(?:'([^']*)'|\"([^\"]*)\"|(\S+(?:\s+\S+){4}))")
    for line in workflow_text.splitlines():
        stripped = line.lstrip()
        if not stripped:
            continue
        if stripped.startswith('#'):
            continue
        # Cut at first '#' not inside quotes (simple: split on '#' and take first part)
        # Cron expressions don't contain '#' and inline comments start with '#'.
        code_part = stripped.split('#')[0]
        match = cron_pattern.search(code_part)
        if match:
            # One of the three capture groups will have the value
            value = match.group(1) or match.group(2) or match.group(3)
            if value:
                active.append(value.strip())
    return active


def has_active_workflow_dispatch(workflow_text: str) -> bool:
    """Check if workflow_dispatch is present and not commented out.
    Must be the actual key: stripped line starts with 'workflow_dispatch'
    and next char is ':' or end of line.
    """
    for line in workflow_text.splitlines():
        stripped = line.lstrip()
        if not stripped:
            continue
        if stripped.startswith('#'):
            continue
        if stripped.startswith('workflow_dispatch'):
            # Next char must be ':' or end of string
            rest = stripped[len('workflow_dispatch'):]
            if not rest or rest.startswith(':'):
                return True
    return False


def test_from_scratch_no_active_cron():
    workflows_dir = Path(__file__).resolve().parents[1] / ".github" / "workflows"
    text = (workflows_dir / "from-scratch.yml").read_text(encoding="utf-8")
    crons = get_active_crons(text)
    assert crons == [], f"from-scratch.yml should have ZERO active crons, got {crons}"


def test_from_scratch_has_workflow_dispatch():
    workflows_dir = Path(__file__).resolve().parents[1] / ".github" / "workflows"
    text = (workflows_dir / "from-scratch.yml").read_text(encoding="utf-8")
    assert has_active_workflow_dispatch(text), "from-scratch.yml must have active workflow_dispatch"


def test_next_stop_cron_yok():
    """DURAKLATILDI 2026-09-03: kanal korku kaydiragi formatina gecti.

    Bu test eskiden cron'un VAR olmasini sarti kosuyordu. Duraklatma kararindan
    sonra tersine cevrildi: zamanlanmis kosu OLMAMALI. Seriyi geri acmak isteyen
    next-stop.yml icindeki schedule yorumunu kaldirir ve bu testi de geri cevirir.
    """
    workflows_dir = Path(__file__).resolve().parents[1] / ".github" / "workflows"
    text = (workflows_dir / "next-stop.yml").read_text(encoding="utf-8")
    crons = get_active_crons(text)
    assert crons == [], f"next-stop.yml duraklatildi, aktif cron OLMAMALI, bulunan: {crons}"


def test_next_stop_has_workflow_dispatch():
    workflows_dir = Path(__file__).resolve().parents[1] / ".github" / "workflows"
    text = (workflows_dir / "next-stop.yml").read_text(encoding="utf-8")
    assert has_active_workflow_dispatch(text), "next-stop.yml must have active workflow_dispatch"


def test_helper_commented_cron_returns_empty():
    """Helper must return [] for a string with only a commented-out cron line."""
    text = """on:
  # schedule:
  #   - cron: '30 14 * * *'
  workflow_dispatch:"""
    crons = get_active_crons(text)
    assert crons == [], f"Helper failed: commented cron should return [], got {crons}"


def test_helper_uncommented_cron_returns_expression():
    """Helper must return the expression for an uncommented cron line."""
    text = """on:
  schedule:
    - cron: '20 13 * * *'
  workflow_dispatch:"""
    crons = get_active_crons(text)
    assert crons == ['20 13 * * *'], f"Helper failed: uncommented cron should return expression, got {crons}"


def test_helper_inline_comment_after_cron_ignored():
    """get_active_crons must ignore inline comment after cron expression."""
    text = """on:
  schedule:
    - cron: '30 14 * * *'   # this is a comment
  workflow_dispatch:"""
    crons = get_active_crons(text)
    assert crons == ['30 14 * * *'], f"Helper failed: inline comment should be stripped, got {crons}"


def test_helper_false_cron_in_comment_not_counted():
    """get_active_crons must not count cron in inline comment on non-cron line."""
    text = """on:
  workflow_dispatch:  # cron: '0 0 * * *'
  schedule:
    - cron: '20 13 * * *'
"""
    crons = get_active_crons(text)
    assert crons == ['20 13 * * *'], f"Helper failed: false cron in comment counted, got {crons}"


def test_helper_workflow_dispatch_key_only():
    """has_active_workflow_dispatch must only match the actual key, not in strings."""
    text = """on:
  if: github.event_name == 'workflow_dispatch'
  schedule:
    - cron: '20 13 * * *'
"""
    assert not has_active_workflow_dispatch(text), "Helper failed: false workflow_dispatch in string counted"

    text2 = """on:
  workflow_dispatch:
  schedule:
    - cron: '20 13 * * *'
"""
    assert has_active_workflow_dispatch(text2), "Helper failed: real workflow_dispatch not detected"


def test_helper_double_quoted_cron_detected():
    """get_active_crons must detect double-quoted cron expressions."""
    text = """on:
  schedule:
    - cron: "30 14 * * *"
  workflow_dispatch:"""
    crons = get_active_crons(text)
    assert crons == ['30 14 * * *'], f"Helper failed: double-quoted cron not detected, got {crons}"


def test_helper_unquoted_cron_detected():
    """get_active_crons must detect unquoted cron expressions."""
    text = """on:
  schedule:
    - cron: 30 14 * * *
  workflow_dispatch:"""
    crons = get_active_crons(text)
    assert crons == ['30 14 * * *'], f"Helper failed: unquoted cron not detected, got {crons}"

# --- Seri durumu muhafizlari -------------------------------------------------
# Cron'u yorumlamak yalniz ZAMANLANMIS yolu kapatir. Iki elle tetikleme yolu daha
# vardi: from-scratch.yml workflow_dispatch -> run_next(), ve series.yml
# workflow_dispatch -> run_all() -> list_active_series(). Ikisi de ayni alana
# bakiyor (series_runner.py:513 ve list_active_series), bu yuzden from-scratch
# serisinin durumu "paused" yapildi. Bu testler o karari koruyor.


def _seri(slug: str) -> dict:
    """aimagine/<slug>/series.json icerigini dondur."""
    kok = Path(__file__).resolve().parents[1]
    yol = kok / "aimagine" / slug / "series.json"
    return json.loads(yol.read_text(encoding="utf-8"))


def test_from_scratch_serisi_duraklatilmis():
    """Elle tetiklense bile uretim yapmamali."""
    durum = _seri("from-scratch")["status"]
    assert durum == "paused", (
        "from-scratch status 'paused' olmali, yoksa workflow_dispatch veya "
        f"series.yml uzerinden yine uretir. Bulunan: {durum!r}"
    )


def test_from_scratch_kaldigi_bolumden_devam_edebilir():
    """Duraklatma bolum sayacini ilerletmemeli; geri acilinca 11'den devam etmeli."""
    next_part = _seri("from-scratch")["next_part"]
    assert next_part == 11, (
        f"from-scratch next_part 11 olmali (kaldigi bolum), bulunan: {next_part!r}"
    )


def test_next_stop_duraklatildi():
    """DURAKLATILDI 2026-09-03 (Ihsan karari): kanal korku kaydiragi formatina gecti.

    status='paused' uc yolu birden kapatir: cron, next-stop.yml workflow_dispatch
    (series_runner.py run_next) ve series.yml workflow_dispatch (list_active_series).
    'paused' makine tarafindan ASLA diriltilmez.
    """
    durum = _seri("next-stop")["status"]
    assert durum == "paused", (
        f"next-stop 'paused' olmali, seri duraklatildi. Bulunan: {durum!r}"
    )


def test_next_stop_ilerlemesi_korundu():
    """Duraklatma bir SIFIRLAMA degil. Geri acilirsa kaldigi bolumden devam etmeli."""
    seri = _seri("next-stop")
    assert seri["next_part"] == 7, (
        f"next_part 7 olmali (part 6 yayinlandi, sirada 7 var). Bulunan: {seri['next_part']!r}"
    )
    assert seri["auto_replenish"]["enabled"] is False, (
        "auto_replenish kapali olmali; acik kalirsa Gemini kendiliginden yeni durak yazar"
    )


def test_iki_seri_hala_ayni_kanala_bakiyor():
    """Gunde-1 kilidi upload_profile esitligine dayanir; ayrilirsa karar yeniden gozden gecirilmeli."""
    fs = _seri("from-scratch")["upload_profile"]
    ns = _seri("next-stop")["upload_profile"]
    assert fs, "from-scratch upload_profile bos olmamali"
    assert fs == ns, (
        "Iki seri ayni kanala bakmali (gunde-1 kilidi buna dayaniyor). "
        f"from-scratch={fs!r} next-stop={ns!r}"
    )
