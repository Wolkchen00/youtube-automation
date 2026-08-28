"""Opt-in, unpublished experiment execution and durable credit accounting.

Nothing in this module is used by the normal scheduler.  Operators enter it
explicitly with ``python -m series.experiment``.
"""

from __future__ import annotations

import argparse
import datetime
import json
import logging
import os
from numbers import Real
from pathlib import Path
import re
import sys
import time
import uuid

from core.config import OUTPUT_DIR, PROJECT_ROOT
from core.kie_api import (
    check_credit,
    generate_seedance_video,
    generate_veo_video,
    generate_video,
)
from series.bible import Bible, atomic_write_json, bible_path
from series.omni_api import generate_omni_shot
from series.series_meta import series_meta_path
from series import credit_gate, produce


logger = logging.getLogger("series.experiment")

LEDGER_PATH = PROJECT_ROOT / "experiments_ledger.json"
EXPERIMENT_OUTPUT_ROOT = OUTPUT_DIR / "experiments"

DEFAULT_TOTAL_CAP = 4000
DEFAULT_STAGE_CAPS = {
    "pilot": 800,
    "preflight": 300,
    "bakeoff": 2400,
    "holdout": 500,
}

_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


class ExperimentLedgerCorruptError(RuntimeError):
    """The durable experiment ledger cannot safely authorize paid work."""


class UnknownExperimentStageError(ValueError):
    """The requested stage is not authorized by the experiment ledger."""


def _timestamp() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _empty_ledger() -> dict:
    return {"experiments": {}}


def _valid_credit(value, *, positive: bool = False) -> bool:
    return (
        not isinstance(value, bool)
        and isinstance(value, Real)
        and float(value) >= (1 if positive else 0)
    )


def _validate(data: object) -> dict:
    if not isinstance(data, dict) or not isinstance(data.get("experiments"), dict):
        raise ValueError("ledger root requires an experiments object")
    for experiment_id, entry in data["experiments"].items():
        if not isinstance(experiment_id, str) or not experiment_id:
            raise ValueError("experiment id is invalid")
        if not isinstance(entry, dict):
            raise ValueError(f"experiment {experiment_id!r} is not an object")
        if not _valid_credit(entry.get("total_cap"), positive=True):
            raise ValueError(f"experiment {experiment_id!r} total_cap is invalid")
        stages = entry.get("stage_caps")
        if not isinstance(stages, dict) or not stages:
            raise ValueError(f"experiment {experiment_id!r} stage_caps is invalid")
        for stage, cap in stages.items():
            # Sifir kapak asamayi kapatir; defter kaydini gecersiz kilmaz.
            if not isinstance(stage, str) or not stage or not _valid_credit(cap):
                raise ValueError(f"experiment {experiment_id!r} has an invalid stage cap")
        reservations = entry.get("reservations", [])
        if not isinstance(reservations, list):
            raise ValueError(f"experiment {experiment_id!r} reservations is invalid")
        for reservation in reservations:
            if not isinstance(reservation, dict):
                raise ValueError("experiment reservation is not an object")
            required_strings = ("reservation_id", "stage", "call_type", "engine", "ts")
            if any(not isinstance(reservation.get(key), str) or not reservation[key]
                   for key in required_strings):
                raise ValueError("experiment reservation identity is invalid")
            if reservation["stage"] not in stages:
                raise ValueError("experiment reservation uses an unknown stage")
            if not _valid_credit(reservation.get("reserved")):
                raise ValueError("experiment reservation estimate is invalid")
            actual = reservation.get("actual")
            if actual is not None and not _valid_credit(actual):
                raise ValueError("experiment reservation actual is invalid")
            duration = reservation.get("duration")
            if duration is not None and not isinstance(duration, str):
                raise ValueError("experiment reservation duration is invalid")
        measurements = entry.get("measurements", [])
        if not isinstance(measurements, list):
            raise ValueError(f"experiment {experiment_id!r} measurements is invalid")
        for measurement in measurements:
            if (not isinstance(measurement, dict)
                    or not isinstance(measurement.get("engine"), str)
                    or not isinstance(measurement.get("params"), dict)
                    or not _valid_credit(measurement.get("measured_credits"))
                    or not isinstance(measurement.get("ts"), str)):
                raise ValueError("experiment price measurement is invalid")
    return data


def _save(data: dict) -> None:
    path = Path(LEDGER_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(f"{path.name}.tmp-{os.getpid()}-{time.time_ns()}")
    try:
        temp_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        os.replace(temp_path, path)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def _shelve_corrupt(raw: bytes, error: Exception) -> None:
    path = Path(LEDGER_PATH)
    stamp = int(time.time())
    aside = path.with_name(f"experiments_ledger.corrupt-{stamp}.json")
    while aside.exists():
        stamp += 1
        aside = path.with_name(f"experiments_ledger.corrupt-{stamp}.json")
    logger.error("Experiment ledger corrupt: %s. Forensic copy: %s", error, aside)
    try:
        aside.write_bytes(raw)
    except Exception:
        logger.exception("Could not copy the corrupt experiment ledger")


def _load() -> dict:
    path = Path(LEDGER_PATH)
    if not path.exists():
        return _empty_ledger()
    raw = path.read_bytes()
    try:
        return _validate(json.loads(raw.decode("utf-8")))
    except Exception as error:
        _shelve_corrupt(raw, error)
        raise ExperimentLedgerCorruptError(
            f"experiment ledger corrupt: {error}"
        ) from error


def _caps(stage_caps: dict | None = None) -> dict[str, float]:
    source = DEFAULT_STAGE_CAPS if stage_caps is None else stage_caps
    if not isinstance(source, dict) or not source:
        raise ValueError("stage_caps must be a non-empty object")
    normalized = {}
    for stage, cap in source.items():
        if not isinstance(stage, str) or not stage.strip() or not _valid_credit(cap, positive=True):
            raise ValueError("stage caps require non-empty names and positive numbers")
        normalized[stage.strip()] = float(cap)
    return normalized


def configure_experiment(experiment_id: str, *, total_cap: float = DEFAULT_TOTAL_CAP,
                         stage_caps: dict | None = None) -> dict:
    """Create or explicitly reconfigure one durable experiment entry."""
    if not isinstance(experiment_id, str) or not experiment_id.strip():
        raise ValueError("experiment_id is required")
    if not _valid_credit(total_cap, positive=True):
        raise ValueError("total_cap must be positive")
    normalized_caps = _caps(stage_caps)
    data = _load()
    existing = data["experiments"].get(experiment_id)
    if existing is None:
        existing = {
            "total_cap": float(total_cap),
            "stage_caps": normalized_caps,
            "reservations": [],
            "measurements": [],
        }
        data["experiments"][experiment_id] = existing
    else:
        existing["total_cap"] = float(total_cap)
        existing["stage_caps"] = normalized_caps
        existing.setdefault("reservations", [])
        existing.setdefault("measurements", [])
        _validate(data)
    _save(data)
    return existing


def _entry(data: dict, experiment_id: str) -> dict:
    entry = data["experiments"].get(experiment_id)
    if entry is None:
        entry = {
            "total_cap": float(DEFAULT_TOTAL_CAP),
            "stage_caps": {key: float(value) for key, value in DEFAULT_STAGE_CAPS.items()},
            "reservations": [],
            "measurements": [],
        }
        data["experiments"][experiment_id] = entry
    return entry


def _charge(reservation: dict) -> float:
    actual = reservation.get("actual")
    return float(reservation["reserved"] if actual is None else actual)


def _usage(entry: dict, stage: str | None = None) -> float:
    return sum(
        _charge(item) for item in entry["reservations"]
        if stage is None or item["stage"] == stage
    )


def _reserve(experiment_id: str, stage: str, call_type: str, engine: str,
             duration=None) -> tuple[str, float] | None:
    from core.cost_tracker import conservative_credit_estimate

    estimate = conservative_credit_estimate(call_type, engine, duration)
    if estimate is None:
        logger.error(
            "EXPERIMENT GATE REFUSED unknown estimate: experiment=%s stage=%s "
            "call=%s engine=%s duration=%s",
            experiment_id, stage, call_type, engine, duration,
        )
        return None
    try:
        data = _load()
    except ExperimentLedgerCorruptError as error:
        logger.error("EXPERIMENT LEDGER FATAL; paid call refused: %s", error)
        return None
    entry = _entry(data, experiment_id)
    if stage not in entry["stage_caps"]:
        logger.error(
            "EXPERIMENT GATE REFUSED unknown stage: experiment=%s stage=%s",
            experiment_id, stage,
        )
        return None
    stage_used = _usage(entry, stage)
    total_used = _usage(entry)
    stage_cap = float(entry["stage_caps"][stage])
    total_cap = float(entry["total_cap"])
    if stage_used + float(estimate) > stage_cap:
        logger.error(
            "EXPERIMENT GATE REFUSED stage cap overflow: experiment=%s stage=%s "
            "used=%g next=%g cap=%g",
            experiment_id, stage, stage_used, float(estimate), stage_cap,
        )
        return None
    if total_used + float(estimate) > total_cap:
        logger.error(
            "EXPERIMENT GATE REFUSED total cap overflow: experiment=%s "
            "used=%g next=%g cap=%g",
            experiment_id, total_used, float(estimate), total_cap,
        )
        return None
    # ROCK D0: deney tavani gecti; ORTAK bakiye tabani da gecmeli. Deney harcamasi
    # kill-gate rezervasyonuna ait DEGILDIR: sahipsiz (owner=None) yetkilendirilir,
    # yani sahip etiketli rezervasyonlarin korudugu krediyi yiyemez.
    from series import balance_floor
    try:
        decision = balance_floor.authorize_spend(float(estimate), owner=None)
    except balance_floor.BalanceFloorError as error:
        logger.error("EXPERIMENT GATE REFUSED balance floor fatal: %s", error)
        return None
    if not decision.allowed:
        logger.error(
            "EXPERIMENT GATE REFUSED balance floor: experiment=%s stage=%s %s",
            experiment_id, stage, decision.reason,
        )
        return None
    reservation_id = uuid.uuid4().hex
    entry["reservations"].append({
        "reservation_id": reservation_id,
        "stage": stage,
        "call_type": str(call_type),
        "engine": str(engine),
        "duration": None if duration is None else str(duration),
        "reserved": float(estimate),
        "actual": None,
        "ts": _timestamp(),
    })
    try:
        _save(data)
    except OSError as error:
        logger.error("EXPERIMENT LEDGER FATAL; reservation was not durable: %s", error)
        return None
    logger.info(
        "EXPERIMENT GATE reserved: experiment=%s stage=%s call=%s "
        "estimate=%g stage_total=%g total=%g",
        experiment_id, stage, call_type, float(estimate),
        stage_used + float(estimate), total_used + float(estimate),
    )
    return reservation_id, float(estimate)


def authorize(experiment_id: str, stage: str, call_type: str, engine: str,
              duration=None) -> bool:
    """Durably reserve a conservative charge against stage and total caps."""
    return _reserve(experiment_id, stage, call_type, engine, duration) is not None


def record(experiment_id: str, actual: float | int | None, *,
           reservation_id: str | None = None) -> bool:
    """Settle one experiment reservation; ``None`` preserves the estimate."""
    if actual is None:
        return True
    if not _valid_credit(actual):
        logger.error("Experiment settlement refused: invalid actual=%r", actual)
        return False
    try:
        data = _load()
    except ExperimentLedgerCorruptError as error:
        logger.error("EXPERIMENT LEDGER FATAL; settlement failed: %s", error)
        return False
    entry = data["experiments"].get(experiment_id)
    if entry is None:
        logger.error("Experiment settlement failed: unknown experiment=%s", experiment_id)
        return False
    match = None
    for candidate in reversed(entry["reservations"]):
        if reservation_id is not None and candidate["reservation_id"] != reservation_id:
            continue
        if candidate.get("actual") is None:
            match = candidate
            break
    if match is None:
        logger.error("Experiment settlement failed: no open reservation")
        return False
    match["actual"] = float(actual)
    match["settled_ts"] = _timestamp()
    _save(data)
    stage_used = _usage(entry, match["stage"])
    total_used = _usage(entry)
    overflow = (
        stage_used > float(entry["stage_caps"][match["stage"]])
        or total_used > float(entry["total_cap"])
    )
    if overflow:
        logger.error(
            "EXPERIMENT GATE actual overflow: experiment=%s stage=%s "
            "stage_used=%g total_used=%g",
            experiment_id, match["stage"], stage_used, total_used,
        )
        return False
    return True


def record_measurement(experiment_id: str, engine: str, params: dict,
                       measured_credits: float | int) -> dict:
    if not _valid_credit(measured_credits):
        raise ValueError("measured_credits must be non-negative")
    data = _load()
    entry = _entry(data, experiment_id)
    measurement = {
        "engine": str(engine),
        "params": dict(params),
        "measured_credits": float(measured_credits),
        "ts": _timestamp(),
    }
    entry["measurements"].append(measurement)
    _save(data)
    return measurement


class ExperimentGate:
    """Stateful adapter matching ``HardCreditCap``'s authorize/settle protocol."""

    def __init__(self, experiment_id: str, stage: str):
        self.experiment_id = experiment_id
        self.stage = stage
        self.blocked_reason: str | None = None
        self._last_reservation_id: str | None = None
        self._last_estimate: float | None = None

    @property
    def blocked(self) -> bool:
        return self.blocked_reason is not None

    @property
    def last_estimate(self) -> float | None:
        return self._last_estimate

    @property
    def remaining(self) -> float | None:
        try:
            data = _load()
        except ExperimentLedgerCorruptError as error:
            self.blocked_reason = str(error)
            return None
        entry = _entry(data, self.experiment_id)
        if self.stage not in entry["stage_caps"]:
            return None
        return max(0.0, min(
            float(entry["total_cap"]) - _usage(entry),
            float(entry["stage_caps"][self.stage]) - _usage(entry, self.stage),
        ))

    def authorize(self, call_type: str, engine: str, duration=None,
                  optional: bool = False) -> bool:
        reserved = _reserve(
            self.experiment_id, self.stage, call_type, engine, duration
        )
        if reserved is None:
            if not optional:
                self.blocked_reason = (
                    f"experiment budget refused {call_type}/{engine}/{duration}"
                )
            return False
        self._last_reservation_id, self._last_estimate = reserved
        return True

    def settle_last(self, actual: float | int | None) -> bool:
        if actual is None:
            return True
        if self._last_reservation_id is None:
            self.blocked_reason = "experiment settlement has no reservation"
            return False
        ok = record(
            self.experiment_id, actual,
            reservation_id=self._last_reservation_id,
        )
        if not ok:
            self.blocked_reason = "experiment settlement failed or exceeded its cap"
        return ok


def _safe_path_component(value: str, label: str) -> str:
    if not isinstance(value, str) or not _SAFE_ID.fullmatch(value):
        raise ValueError(f"{label} must match {_SAFE_ID.pattern}")
    return value


def run_experiment(slug: str, plan_path: str | Path, experiment_id: str,
                   stage: str = "pilot", dry_run: bool = False):
    """Produce one unpublished episode in an experiment-only artifact tree."""
    safe_slug = _safe_path_component(slug, "slug")
    safe_experiment = _safe_path_component(experiment_id, "experiment_id")
    # Asama kaynagi deney defteridir; dry-run da yazim hatasini gizlememeli.
    entry = _entry(_load(), experiment_id)
    if stage not in entry["stage_caps"]:
        valid_stages = ", ".join(sorted(entry["stage_caps"]))
        raise UnknownExperimentStageError(
            f"bilinmeyen asama {stage!r}; bu deneyde gecerli asamalar: {valid_stages}"
        )
    source_plan = Path(plan_path)
    plan = json.loads(source_plan.read_text(encoding="utf-8"))
    try:
        number = int((plan.get("episode") or {}).get("number"))
    except (TypeError, ValueError):
        raise ValueError("plan requires an integer episode.number")

    bible = Bible.load(slug)
    if bible is None:
        raise FileNotFoundError(f"bible not found for series {slug!r}")
    state_paths = [series_meta_path(slug), bible_path(slug), source_plan]
    before = {path.resolve(): path.read_bytes() for path in state_paths if path.exists()}

    output_area = Path(EXPERIMENT_OUTPUT_ROOT) / safe_experiment / f"{safe_slug}-part{number:02d}"
    output_area.mkdir(parents=True, exist_ok=True)
    isolated_plan = output_area / "plan.json"
    if isolated_plan.exists():
        existing = json.loads(isolated_plan.read_text(encoding="utf-8"))
        if existing != plan:
            raise FileExistsError(
                f"experiment output already contains a different plan: {isolated_plan}"
            )
    else:
        atomic_write_json(isolated_plan, plan)
    isolated_bible = output_area / "bible.json"
    if not isolated_bible.exists():
        atomic_write_json(isolated_bible, bible.data)

    authorizer = None
    if not dry_run:
        episode_limit = produce.episode_credit_cap(bible)
        if episode_limit <= 0:
            raise RuntimeError("episode credit cap must be positive")
        episode_gate = credit_gate.HardCreditCap(episode_limit, 0.0)
        experiment_gate = ExperimentGate(experiment_id, stage)
        authorizer = credit_gate.CompositeCreditCap(episode_gate, experiment_gate)

    try:
        result = produce.produce_episode(
            slug,
            isolated_plan,
            dry_run=dry_run,
            typed_result=True,
            hard_cap=authorizer,
            output_area=output_area,
            experiment_id=experiment_id,
        )
    finally:
        changed = [
            str(path) for path, content in before.items()
            if not path.exists() or path.read_bytes() != content
        ]
        if changed:
            raise RuntimeError(
                "experiment touched production source state: " + ", ".join(changed)
            )
    return result


def _balance_value(payload) -> float | None:
    if isinstance(payload, Real) and not isinstance(payload, bool):
        return float(payload)
    if isinstance(payload, dict):
        for key in ("balance", "credit", "credits", "remaining"):
            value = payload.get(key)
            if isinstance(value, Real) and not isinstance(value, bool):
                return float(value)
    return None


def _default_generate(engine: str, params: dict):
    eng = str(engine).strip().lower()
    values = dict(params)
    if eng in ("veo3_fast", "veo3", "veo3_lite"):
        values["model"] = eng
        return generate_veo_video(**values)
    if eng in ("seedance", "seedance-2", "seedance_fast", "bytedance/seedance-2-fast"):
        return generate_seedance_video(**values)
    if eng == "omni":
        return generate_omni_shot(**values)
    if eng in ("kling", "kling-2.6"):
        return generate_video(**values)
    raise ValueError(f"unsupported preflight engine: {engine}")


def preflight_price(experiment_id: str, engine: str, params: dict, *,
                    stage: str = "preflight", balance_checker=check_credit,
                    generator=None, fleet_reserve: float | None = None) -> dict:
    """Run exactly one adapter invocation and persist its real balance delta.

    Tests inject both callables.  The CLI is deliberately opt-in and is the only
    path that can invoke the live defaults.
    """
    before = _balance_value(balance_checker())
    if before is None:
        raise RuntimeError("preflight balance-before check failed; no paid call made")
    duration = params.get("duration")
    gate = ExperimentGate(experiment_id, stage)
    if not gate.authorize("main_shot", engine, duration):
        raise RuntimeError(gate.blocked_reason or "experiment gate refused preflight")
    estimate = float(gate.last_estimate or 0)
    reserve = float(credit_gate.episode_cap() if fleet_reserve is None else fleet_reserve)
    if before - estimate < reserve:
        gate.settle_last(0)
        raise RuntimeError(
            f"fleet reserve refused preflight: balance={before:g}, "
            f"estimate={estimate:g}, reserve={reserve:g}"
        )

    adapter = generator or _default_generate
    result = adapter(engine, dict(params))
    after = _balance_value(balance_checker())
    if after is None:
        raise RuntimeError(
            "preflight balance-after check failed; conservative reservation retained"
        )
    measured = before - after
    if measured < 0:
        raise RuntimeError(
            "preflight balance increased during measurement; reservation retained"
        )
    if not gate.settle_last(measured):
        raise RuntimeError(gate.blocked_reason or "preflight settlement failed")
    measurement = record_measurement(experiment_id, engine, params, measured)
    return {**measurement, "result": result}


def _params_from_args(args) -> dict:
    if args.params_json:
        params = json.loads(Path(args.params_json).read_text(encoding="utf-8"))
        if not isinstance(params, dict):
            raise ValueError("--params-json must contain a JSON object")
        return params
    params = {"prompt": args.prompt, "duration": args.duration}
    if args.engine.lower().startswith("veo"):
        params.update({
            "generation_type": args.generation_type,
            "image_urls": args.image_url,
            "aspect_ratio": args.aspect_ratio,
            "resolution": args.resolution,
        })
    return params


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    run = commands.add_parser("run", help="produce one isolated unpublished episode")
    run.add_argument("slug")
    run.add_argument("--plan", required=True)
    run.add_argument("--experiment-id", required=True)
    run.add_argument("--stage", default="pilot")
    run.add_argument("--dry-run", action="store_true")

    preflight = commands.add_parser("preflight", help="measure one real adapter price")
    preflight.add_argument("engine")
    preflight.add_argument("--experiment-id", required=True)
    preflight.add_argument("--stage", default="preflight")
    preflight.add_argument("--prompt", default="Single neutral preflight motion study.")
    preflight.add_argument("--duration", default="8")
    preflight.add_argument("--generation-type", default="TEXT_2_VIDEO")
    preflight.add_argument("--image-url", action="append", default=[])
    preflight.add_argument("--aspect-ratio", default="9:16")
    preflight.add_argument("--resolution", default="1080p")
    preflight.add_argument("--params-json")
    preflight.add_argument("--fleet-reserve", type=float)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "run":
        try:
            result = run_experiment(
                args.slug, args.plan, args.experiment_id,
                stage=args.stage, dry_run=args.dry_run,
            )
        except UnknownExperimentStageError as error:
            print(f"error: {error}", file=sys.stderr)
            return 2
        if getattr(result, "status", None) == "ok":
            print(str(result.path))
            return 0
        if args.dry_run:
            print("dry-run complete")
            return 0
        print(getattr(result, "reason", None) or "experiment generation failed")
        return 1
    params = _params_from_args(args)
    measurement = preflight_price(
        args.experiment_id, args.engine, params,
        stage=args.stage, fleet_reserve=args.fleet_reserve,
    )
    print(json.dumps(measurement, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
