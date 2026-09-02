"""Filodaki gerçek Gemini QC çağrılarını salt-okunur olarak sayar."""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTCOMES = ("ok", "429", "diger_hata", "sonucsuz")
SENTINAL_LINE = "sentinal_ihsan/unnatural-lab"


class CensusError(Exception):
    """Sayımın devam etmesini güvensiz kılan gerçek bir okuma hatası."""


def read_journal(path: Path) -> tuple[list[dict[str, Any]], int]:
    """Geçerli JSON nesnelerini ve okunamayan satır sayısını döndür."""
    events: list[dict[str, Any]] = []
    malformed = 0
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        # Glob ile okuma arasında silinen veya hiç olmayan journal veri yok demektir.
        return events, malformed
    except (OSError, UnicodeError) as exc:
        raise CensusError(f"journal okunamadı: {path}: {exc}") from exc

    for line in lines:
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            malformed += 1
            continue
        if isinstance(event, dict):
            events.append(event)
        else:
            malformed += 1
    return events, malformed


def parse_ts(value: Any) -> datetime | None:
    """Journal zamanını UTC'ye çevir; geçersiz değerde None döndür."""
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def find_journals(project_root: Path) -> list[Path]:
    """Kanal/seri klasörlerindeki journal'ları seri adlarını sabitlemeden bul."""
    try:
        return sorted(
            path for path in project_root.glob("*/*/qc_log.jsonl") if path.is_file()
        )
    except OSError as exc:
        raise CensusError(f"journal yolları taranamadı: {project_root}: {exc}") from exc


def _line_name(project_root: Path, journal: Path) -> str:
    try:
        relative = journal.relative_to(project_root)
    except ValueError:
        relative = journal
    return f"{relative.parent.parent.name}/{relative.parent.name}"


def _outcome_for(results: list[dict[str, Any]]) -> str:
    if not results:
        return "sonucsuz"
    # Bir attempt tek çağrıdır. Yinelenen result kayıtları çağrının sayısını artırmaz;
    # journal'daki son terminal kayıt o çağrının sonucu kabul edilir.
    outcome = results[-1].get("outcome")
    if outcome in ("ok", "429"):
        return str(outcome)
    return "diger_hata"


def build_report(
    project_root: Path,
    days: int = 7,
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Journal'ları değiştirmeden Q1/Q2/Q3 sayımlarını üret."""
    if days < 0:
        raise CensusError("--days negatif olamaz")
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    current = current.astimezone(timezone.utc)
    cutoff = current - timedelta(days=days)

    journals = find_journals(project_root)
    malformed = 0
    invalid_timestamps = 0
    attempts: dict[str, dict[str, Any]] = {}
    results: dict[str, list[dict[str, Any]]] = {}
    duplicate_attempts = 0

    for journal in journals:
        events, bad_lines = read_journal(journal)
        malformed += bad_lines
        line_name = _line_name(project_root, journal)
        for event in events:
            event_name = event.get("event")
            if event_name not in ("qc_api_attempt", "qc_api_result"):
                continue
            event_ts = parse_ts(event.get("ts"))
            if event_ts is None:
                invalid_timestamps += 1
                continue
            # Sınır anındaki olay pencereye dahildir.
            if event_ts < cutoff or event_ts > current:
                continue
            attempt_id = event.get("attempt_id")
            if not isinstance(attempt_id, str) or not attempt_id:
                continue
            enriched = dict(event)
            enriched["_ts"] = event_ts
            if event_name == "qc_api_attempt":
                enriched["_line"] = line_name
                if attempt_id in attempts:
                    duplicate_attempts += 1
                else:
                    attempts[attempt_id] = enriched
            else:
                results.setdefault(attempt_id, []).append(enriched)

    # Result sırası dosya sıralarına değil zamana bağlı olsun.
    for matching_results in results.values():
        matching_results.sort(key=lambda item: item["_ts"])

    q1_counter: Counter[tuple[str, str, str]] = Counter()
    q2_counter: Counter[str] = Counter()
    episode_counter: Counter[tuple[str, Any]] = Counter()
    episode_shots: dict[tuple[str, Any], set[Any]] = {}

    for attempt_id, attempt in attempts.items():
        line_name = attempt["_line"]
        model = attempt.get("model")
        if not isinstance(model, str) or not model:
            model = "(model yok)"
        day = attempt["_ts"].date().isoformat()
        q1_counter[(day, line_name, model)] += 1
        q2_counter[_outcome_for(results.get(attempt_id, []))] += 1

        episode = attempt.get("episode")
        episode_key = (line_name, episode)
        episode_counter[episode_key] += 1
        shot = attempt.get("shot")
        if isinstance(shot, int) and not isinstance(shot, bool):
            episode_shots.setdefault(episode_key, set()).add(shot)

    q1_rows = [
        {"tarih": day, "hat": line, "model": model, "cagri": count}
        for (day, line, model), count in sorted(q1_counter.items())
    ]
    total = len(attempts)
    outcome_counts = {name: q2_counter[name] for name in OUTCOMES}
    outcome_fractions = {
        name: (outcome_counts[name] / total if total else None) for name in OUTCOMES
    }
    failed = outcome_counts["429"] + outcome_counts["diger_hata"]

    sentinal_episodes = []
    for (line_name, episode), count in sorted(
        episode_counter.items(), key=lambda item: (item[0][0], str(item[0][1]))
    ):
        if line_name != SENTINAL_LINE:
            continue
        sentinal_episodes.append(
            {
                "episode": episode,
                "cagri": count,
                "ulasinilan_shotlar": sorted(episode_shots.get((line_name, episode), set())),
                # Attempt/result şeması beklenen son shot numarasını taşımıyor.
                "tamamlandi": None,
            }
        )

    episode_counts = [row["cagri"] for row in sentinal_episodes]
    median_calls = statistics.median(episode_counts) if episode_counts else None
    max_calls = max(episode_counts) if episode_counts else None
    no_data = total == 0

    return {
        "mesaj": "veri yok" if no_data else None,
        "meta": {
            "gun": days,
            "simdi_utc": current.isoformat().replace("+00:00", "Z"),
            "baslangic_utc": cutoff.isoformat().replace("+00:00", "Z"),
            "bulunan_journal": len(journals),
            "bozuk_json_satiri": malformed,
            "gecersiz_zamanli_api_olayi": invalid_timestamps,
            "yinelenen_attempt_kaydi": duplicate_attempts,
        },
        "q1": {"toplam_cagri": total, "gun_hat_model": q1_rows},
        "q2": {
            "toplam_cagri": total,
            "adet": outcome_counts,
            "pay": outcome_fractions,
            "basarisiz_adet": failed,
            "basarisiz_pay": failed / total if total else None,
        },
        "q3": {
            "hat": SENTINAL_LINE,
            "bolumler": sentinal_episodes,
            "gozlenen_bolum_medyani": median_calls,
            "gozlenen_bolum_maksimumu": max_calls,
            "tam_bolum_cagri_ihtiyaci": None,
            "tamamlanma_notu": (
                "Journal attempt/result kayıtları beklenen son shot numarasını veya bir "
                "episode_complete işaretini taşımıyor. Bu nedenle hangi bölümlerin son "
                "shot'a ulaştığı ve bir tam bölümün kaç çağrı gerektirdiği journal'dan "
                "kesin olarak belirlenemiyor; medyan ve maksimum gözlenen bölüm "
                "kayıtlarınındır."
            ),
        },
    }


def _fmt_number(value: int | float | None) -> str:
    if value is None:
        return "belirlenemedi"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def render_table(report: dict[str, Any]) -> str:
    """Raporu Türkçe, sade insan tablosu olarak yaz."""
    meta = report["meta"]
    lines = [
        "Gemini QC filo çağrısı sayımı (salt-okunur)",
        f"Pencere (UTC): {meta['baslangic_utc']} <= ts <= {meta['simdi_utc']}",
        (
            f"Journal: {meta['bulunan_journal']} | Bozuk JSON satırı: "
            f"{meta['bozuk_json_satiri']} | Geçersiz zamanlı API olayı: "
            f"{meta['gecersiz_zamanli_api_olayi']} | Yinelenen attempt kaydı: "
            f"{meta['yinelenen_attempt_kaydi']}"
        ),
    ]
    if report["mesaj"]:
        lines.append("veri yok: seçilen pencerede qc_api_attempt kaydı bulunamadı")
        return "\n".join(lines)

    lines.extend(
        [
            "",
            "Q1 - Gün / hat / model bazında benzersiz QC çağrıları",
            "Tarih     | Hat                              | Model                 | Çağrı",
            "-----------+----------------------------------+-----------------------+------",
        ]
    )
    for row in report["q1"]["gun_hat_model"]:
        lines.append(
            f"{row['tarih']:<10} | {row['hat']:<32} | {row['model']:<21} | {row['cagri']:>5}"
        )
    lines.append(f"TOPLAM     |                                  |                       | {report['q1']['toplam_cagri']:>5}")

    lines.extend(
        [
            "",
            "Q2 - Sonuç dağılımı (payda: tüm benzersiz çağrılar)",
            "Sonuç       | Adet | Pay",
            "------------+------+--------",
        ]
    )
    labels = {
        "ok": "ok",
        "429": "429",
        "diger_hata": "diğer hata",
        "sonucsuz": "sonuçsuz",
    }
    for outcome in OUTCOMES:
        fraction = report["q2"]["pay"][outcome]
        lines.append(
            f"{labels[outcome]:<11} | {report['q2']['adet'][outcome]:>4} | {fraction:>6.1%}"
        )
    lines.append(
        "Başarısız (429 + diğer hata): "
        f"{report['q2']['basarisiz_adet']}/{report['q2']['toplam_cagri']} "
        f"({report['q2']['basarisiz_pay']:.1%}); sonuçsuz ayrı gösterilir."
    )

    q3 = report["q3"]
    lines.extend(
        [
            "",
            f"Q3 - Bir tam Sentinal bölümü ({q3['hat']})",
            "Bölüm | Benzersiz çağrı | Ulaşılan shotlar | Tamamlanma",
            "------+------------------+------------------+-------------",
        ]
    )
    if q3["bolumler"]:
        for row in q3["bolumler"]:
            shots = ",".join(str(shot) for shot in row["ulasinilan_shotlar"]) or "-"
            lines.append(
                f"{str(row['episode']):>5} | {row['cagri']:>16} | {shots:<16} | belirlenemedi"
            )
    else:
        lines.append("veri yok")
    lines.extend(
        [
            f"Gözlenen bölüm medyanı: {_fmt_number(q3['gozlenen_bolum_medyani'])}",
            f"Gözlenen bölüm maksimumu: {_fmt_number(q3['gozlenen_bolum_maksimumu'])}",
            "Bir TAM bölümün çağrı ihtiyacı: belirlenemedi.",
            f"Not: {q3['tamamlanma_notu']}",
        ]
    )
    return "\n".join(lines)


def main(
    argv: list[str] | None = None,
    *,
    project_root: Path | None = None,
    now: datetime | None = None,
) -> int:
    parser = argparse.ArgumentParser(
        description="Tüm kanal journal'larından gerçek Gemini QC çağrılarını sayar."
    )
    parser.add_argument("--days", type=int, default=7, help="UTC zaman penceresi (varsayılan: 7)")
    parser.add_argument("--json", action="store_true", help="Makine-okunur JSON yaz")
    args = parser.parse_args(argv)

    try:
        report = build_report(project_root or PROJECT_ROOT, args.days, now=now)
    except CensusError as exc:
        print(f"HATA: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_table(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
