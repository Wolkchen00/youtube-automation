"""Offline preflight for doctrine, config/plan compatibility, and chain trace.

Usage:
  python -m series.preflight --series from-scratch --plan aimagine/from-scratch/plans/part06.json
"""

import argparse
import sys
from pathlib import Path

from .bible import Bible, doctrine_path, doctrine_repo_path, doctrine_sha256
from .omni_api import validate_ref_units
from .produce import chain_configuration_error, decide_shot_chain
from .replenish import (
    strict_plan_validation_enabled,
    validate_plan_against_config,
    validate_replenish_config,
)
from .series_meta import SeriesMeta
from .shots import load_plan, resolve_shot, validate_plan


def inspect(slug: str, plan_path: str | Path) -> tuple[list[str], list[dict]]:
    """Return ``(errors, chain_trace)`` without making any network calls or writes."""
    errors: list[str] = []
    trace: list[dict] = []
    meta = SeriesMeta.load(slug)
    bible = Bible.load(slug)
    if meta is None:
        return [f"series meta yüklenemedi: {slug}"], trace
    if bible is None:
        return [f"bible yüklenemedi: {slug}"], trace
    series_cfg = bible.data["series"]
    if "chain_scope" in series_cfg and str(series_cfg.get("chain_scope")).strip().lower() not in (
        "series", "episode"
    ):
        errors.append("bible: chain_scope yalnız 'series' veya 'episode' olabilir")
    chain_error = chain_configuration_error(bible)
    if chain_error:
        errors.append(f"bible: {chain_error}")
    if "required_layers" in series_cfg:
        raw_layers = series_cfg.get("required_layers")
        if (not isinstance(raw_layers, list)
                or any(not isinstance(layer, str) or not layer.strip() for layer in raw_layers)
                or len(set(raw_layers)) != len(raw_layers)):
            errors.append("bible: required_layers benzersiz, boş olmayan string listesi olmalı")
    try:
        bible.audio_fade
    except ValueError as error:
        errors.append(f"bible: {error}")
    try:
        plan = load_plan(plan_path)
    except Exception as error:
        return [f"plan yüklenemedi: {error}"], trace

    path = doctrine_path(slug)
    digest = None
    if path is None:
        errors.append("doktrin dosyası bulunamadı")
    else:
        try:
            text = path.read_bytes().decode("utf-8").replace("\r\n", "\n")
            if not text.strip():
                errors.append("doktrin dosyası boş")
            else:
                digest = doctrine_sha256(path)
        except (OSError, UnicodeError) as error:
            errors.append(f"doktrin okunamadı: {error}")
    if digest is not None:
        pinned = str(meta.data.get("doctrine_sha256") or "").strip().lower()
        plan_digest = str(plan.get("doctrine_sha256") or "").strip().lower()
        if "doctrine_sha256" in meta.data and pinned != digest:
            errors.append("series doctrine_sha256 pin'i güncel doktrinle eşleşmiyor")
        if "doctrine_sha256" in meta.data and not plan_digest:
            errors.append("pinli plan doctrine_sha256 damgası taşımıyor")
        elif plan_digest and plan_digest != digest:
            errors.append("plan doctrine_sha256 damgası güncel doktrinle eşleşmiyor")

    cfg = meta.auto_replenish
    errors.extend(f"cfg: {error}" for error in validate_replenish_config(cfg))
    if strict_plan_validation_enabled(cfg):
        errors.extend(f"plan/cfg: {error}" for error in validate_plan_against_config(plan, cfg))
    if "chain_breaks" in cfg and not bible.chain_frames:
        errors.append("cfg: chain_breaks için bible.series.chain_frames=true olmalı")
    unknown_layers = set(bible.required_layers) - {"hook_teaser", "music", "native_audio"}
    if unknown_layers:
        errors.append(f"bible: bilinmeyen required_layers: {sorted(unknown_layers)}")
    generic = validate_plan(plan, bible)
    errors.extend(f"plan: {error}" for error in generic["errors"])

    chain_url = None
    if bible.chain_frames and bible.chain_scope == "series":
        chain_url = meta.data.get("last_frame_url")
    shots = plan.get("shots") if isinstance(plan.get("shots"), list) else []
    for index, shot in enumerate(shots):
        if not isinstance(shot, dict):
            errors.append(f"çekim {index + 1}: JSON nesnesi değil")
            continue
        next_shot = shots[index + 1] if index + 1 < len(shots) else None
        decision = decide_shot_chain(shot, next_shot, bible.chain_frames, chain_url)
        entry = {
            "shot": shot.get("n", index + 1),
            "chain": shot.get("chain", "legacy"),
            "reset": decision.reset_before,
            "input": decision.start_url,
            "capture": decision.capture_last_frame,
            "status": "fail" if decision.error else "ok",
        }
        if decision.error:
            entry["error"] = decision.error
            errors.append(f"çekim {entry['shot']} zincir: {decision.error}")
        trace.append(entry)
        if strict_plan_validation_enabled(cfg) and bible.engine == "omni" and not decision.error:
            kwargs = resolve_shot(
                bible, shot, plan, chain_url=decision.start_url
            )["kwargs"]
            ok, units = validate_ref_units(kwargs.get("image_urls"), kwargs.get("character_ids"))
            if not ok:
                errors.append(f"çekim {entry['shot']}: zincir sonrası referans kotası {units}/7")
        if decision.capture_last_frame and not decision.error:
            chain_url = f"shot:{entry['shot']}:last-frame"
        else:
            chain_url = decision.start_url
    return errors, trace


def run(slug: str, plan_path: str | Path) -> int:
    errors, trace = inspect(slug, plan_path)
    meta = SeriesMeta.load(slug)
    path = doctrine_path(slug) if meta else None
    print(f"PREFLIGHT series={slug} plan={Path(plan_path)}")
    if path:
        print(f"doctrine={doctrine_repo_path(path)} sha256={doctrine_sha256(path)}")
    for entry in trace:
        print(
            f"shot {entry['shot']}: chain={entry['chain']} reset={entry['reset']} "
            f"input={entry['input'] or '-'} capture={entry['capture']} status={entry['status']}"
        )
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"PREFLIGHT FAIL ({len(errors)} violation)")
        return 1
    print("PREFLIGHT OK")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--series", required=True, help="series slug")
    parser.add_argument("--plan", required=True, help="episode plan JSON path")
    args = parser.parse_args(argv)
    return run(args.series, args.plan)


if __name__ == "__main__":
    raise SystemExit(main())
