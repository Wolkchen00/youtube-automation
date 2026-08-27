#!/usr/bin/env python
"""P7 ROCK B kalibrasyon manifestini fail-closed raporla."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = REPO_ROOT / "tests" / "fixtures" / "qc_calibration" / "manifest.json"
ROCK_B_FIELDS = ("anomaly_match", "violation_reads", "state_carry_ok")
MIN_SAMPLES = 24
MIN_NEGATIVES = 8
MIN_HELD_OUT_FRACTION = 0.5


def _load_manifest(path: Path) -> tuple[list[dict], list[str]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return [], [f"manifest bulunamadı: {path}"]
    except (OSError, json.JSONDecodeError) as error:
        return [], [f"manifest okunamadı: {path} ({error})"]
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        return [], ["manifest schema_version tam 1 olmalı"]
    samples = data.get("samples")
    if not isinstance(samples, list):
        return [], ["manifest samples alanı liste olmalı"]
    return samples, []


def _prediction(sample: dict) -> tuple[object, list[str]]:
    errors: list[str] = []
    result = sample.get("model_result")
    if not isinstance(result, dict) or set(result) != {"value", "visible", "confidence"}:
        return None, ["model_result exact value/visible/confidence nesnesi olmalı"]
    value = result.get("value")
    visible = result.get("visible")
    confidence = result.get("confidence")
    if value is not None and type(value) is not bool:
        errors.append("model_result.value bool|null olmalı")
    if type(visible) is not bool:
        errors.append("model_result.visible bool olmalı")
    if (isinstance(confidence, bool) or not isinstance(confidence, (int, float))
            or not 0.0 <= float(confidence) <= 1.0):
        errors.append("model_result.confidence 0-1 sayı olmalı")
    if errors:
        return None, errors
    effective = None if float(confidence) < 0.5 else value
    if effective is None and sample.get("human_visible") is True:
        reason = sample.get("null_reason")
        if not isinstance(reason, str) or not reason.strip():
            errors.append("gözlemlenebilir null sonucu için null_reason zorunlu")
    return effective, errors


def _validate_field(field: str, samples: list[dict]) -> tuple[list[dict], list[str]]:
    selected = [sample for sample in samples
                if isinstance(sample, dict) and sample.get("field") == field]
    errors: list[str] = []
    seen_ids: set[str] = set()
    for index, sample in enumerate(selected, start=1):
        prefix = f"{field} örnek {index}"
        sample_id = sample.get("id")
        if not isinstance(sample_id, str) or not sample_id.strip():
            errors.append(f"{prefix}: id zorunlu")
        elif sample_id in seen_ids:
            errors.append(f"{prefix}: yinelenen id ({sample_id})")
        else:
            seen_ids.add(sample_id)
        if not isinstance(sample.get("fixture"), str) or not sample["fixture"].strip():
            errors.append(f"{prefix}: fixture yolu zorunlu")
        sample_class = sample.get("class")
        human_label = sample.get("human_label")
        if sample_class not in ("positive", "negative"):
            errors.append(f"{prefix}: class positive|negative olmalı")
        if type(human_label) is not bool:
            errors.append(f"{prefix}: human_label bool olmalı")
        elif sample_class in ("positive", "negative") and (
            human_label is not (sample_class == "positive")
        ):
            errors.append(f"{prefix}: class ile human_label çelişiyor")
        if type(sample.get("human_visible")) is not bool:
            errors.append(f"{prefix}: human_visible bool olmalı")
        if sample.get("split") not in ("train", "held-out"):
            errors.append(f"{prefix}: split train|held-out olmalı")
        _, prediction_errors = _prediction(sample)
        errors.extend(f"{prefix}: {error}" for error in prediction_errors)

    total = len(selected)
    negatives = sum(sample.get("class") == "negative" for sample in selected)
    held_out = sum(sample.get("split") == "held-out" for sample in selected)
    if total < MIN_SAMPLES:
        errors.append(f"{field}: en az {MIN_SAMPLES} örnek gerekli (gelen: {total})")
    if negatives < MIN_NEGATIVES:
        errors.append(f"{field}: en az {MIN_NEGATIVES} negatif gerekli (gelen: {negatives})")
    if held_out < math.ceil(total * MIN_HELD_OUT_FRACTION):
        errors.append(
            f"{field}: örneklerin en az yarısı held-out olmalı "
            f"(gelen: {held_out}/{total})"
        )
    for split in ("train", "held-out"):
        split_classes = {
            sample.get("class") for sample in selected if sample.get("split") == split
        }
        if split_classes != {"positive", "negative"}:
            errors.append(f"{field}: {split} split'i pozitif ve negatif sınıfları taşımalı")
    return selected, errors


def _rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 1.0


def _report_field(field: str, samples: list[dict]) -> bool:
    train = [sample for sample in samples if sample["split"] == "train"]
    held_out = [sample for sample in samples if sample["split"] == "held-out"]
    held_predictions = [(sample, _prediction(sample)[0]) for sample in held_out]
    visible = [(sample, prediction) for sample, prediction in held_predictions
               if sample["human_visible"]]
    negatives = [(sample, prediction) for sample, prediction in visible
                 if sample["human_label"] is False]
    positives = [(sample, prediction) for sample, prediction in visible
                 if sample["human_label"] is True]
    false_pass = _rate(sum(prediction is True for _, prediction in negatives), len(negatives))
    false_reject = _rate(sum(prediction is False for _, prediction in positives), len(positives))
    null_rate = _rate(sum(prediction is None for _, prediction in visible), len(visible))
    promoted = false_pass <= 0.10 and false_reject <= 0.20 and null_rate <= 0.30
    train_pos = sum(sample["class"] == "positive" for sample in train)
    held_pos = sum(sample["class"] == "positive" for sample in held_out)
    print(f"{field}:")
    print(f"  train: {len(train)} örnek ({train_pos} pozitif, {len(train) - train_pos} negatif)")
    print(f"  held-out: {len(held_out)} örnek "
          f"({held_pos} pozitif, {len(held_out) - held_pos} negatif)")
    print(f"  held-out yanlış-geçiş: {false_pass:.1%}")
    print(f"  held-out yanlış-red: {false_reject:.1%}")
    print(f"  held-out gözlemlenebilir-null: {null_rate:.1%}")
    print(f"  terfi: {'İZİN VERİLEBİLİR' if promoted else 'İZİN VERİLMEZ'}")
    return promoted


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--field", action="append", choices=ROCK_B_FIELDS, required=True)
    args = parser.parse_args(argv)

    samples, errors = _load_manifest(args.manifest)
    validated: dict[str, list[dict]] = {}
    for field in dict.fromkeys(args.field):
        selected, field_errors = _validate_field(field, samples)
        validated[field] = selected
        errors.extend(field_errors)
    if errors:
        for error in errors:
            print(f"HATA: {error}", file=sys.stderr)
        print(
            "TERFİYE İZİN VERİLMEZ: manifest yok, eksik veya P7 asgari protokolünü karşılamıyor. "
            "Desteklenmeyen doğruluk/metrik sayısı raporlanmadı.",
            file=sys.stderr,
        )
        return 1

    permitted = True
    for field, field_samples in validated.items():
        permitted = _report_field(field, field_samples) and permitted
    return 0 if permitted else 1


if __name__ == "__main__":
    raise SystemExit(main())
