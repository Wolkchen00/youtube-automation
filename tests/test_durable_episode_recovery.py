"""ROCK E kaniti - kosu sinirini gecen bolum eseri ve yayin mutabakati.

Iki kosuluk bir kanit, hayatta kalan YEREL dosyalar ya da mock'lanmis bir
onbellek kabulu yuzunden SAHTE gecebilir. Bu yuzden burada:

  * birinci kosunun TUM calisma dosyalari (output/) silinir; yalniz kalici
    olanlar (git'te duran seri klasoru, qc_log.jsonl ve uzak eser deposu)
    ayakta kalir;
  * kredi defteri GERCEKTIR (series.credit_gate, gercek JSON dosyasi) ve QC
    kapisi GERCEKTIR (critic.qc_pass_exists, gercek qc_log.jsonl);
  * videolar ffmpeg ile GERCEKTEN uretilir, butunluk ffprobe ile GERCEKTEN
    olculur; mock'lanan tek sey depolama TASIYICISIDIR (gh CLI).

Olculen kusur: ``_persist_release`` yalniz ``mode == "approval"`` dalindan
cagriliyordu, ``publish_mode: auto`` olan unnatural-lab'de kalici Release HIC
olusmuyordu. Bolum 25, 26, 28 ve 30: 436 + 932 + 680 + 848 = 2896 kredi,
sifir video.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from contextlib import ExitStack
from pathlib import Path
from unittest import mock

import pytest

from core import cost_tracker, ffmpeg_tools
from series import approver, credit_gate, critic, durable_artifact, produce, series_runner
from series.bible import Bible, episode_dir, shots_dir

SLUG = "durable-lab"
SHOT_CREDITS = 220          # gercek harcama: 4 x 220 = 880
CONSERVATIVE_PER_SHOT = 100  # omni / 6 sn korumaci taban (cost_tracker tablosu)
SHOT_COLORS = ("0x101010", "0x204020", "0x403060", "0x605020")


# --- gercek medya -------------------------------------------------------------

def _require_ffmpeg() -> None:
    if not (shutil.which("ffmpeg") and shutil.which("ffprobe")):
        pytest.skip("ffmpeg ve ffprobe gerekli (gercek butunluk olcumu)")


def _write_mp4(path: Path, color: str, seconds: float = 1.0) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-f", "lavfi", "-i", f"color=c={color}:s=64x64:r=8:d={seconds}",
         "-pix_fmt", "yuv420p", str(path)],
        check=True, capture_output=True,
    )
    return path


# --- kalici depo TASIYICISI (gh CLI yerine) -----------------------------------

class FakeReleaseStore:
    """GitHub Release tasiyicisinin dosya sistemi ikizi.

    ONBELLEK DEGILDIR: manifest uretimi, ozetler, QC kapisi ve defter gercektir.
    Burada yalniz "baytlar kosu sinirini gecti mi" sorusu modellenir.
    """

    def __init__(self, root: Path):
        self.root = root
        self.reachable = True
        self.download_calls = 0
        self.persist_calls: list[str] = []
        self.deleted: list[str] = []

    def persist(self, slug: str, n: int, video_path, extra_assets=None):
        tag = f"pending-{slug}-part{n}"
        dest = self.root / tag
        shutil.rmtree(dest, ignore_errors=True)
        dest.mkdir(parents=True, exist_ok=True)
        for src in [video_path, *(extra_assets or [])]:
            shutil.copy2(str(src), dest / Path(src).name)
        self.persist_calls.append(tag)
        return tag

    def fetch(self, tag: str, dest_dir):
        self.download_calls += 1
        if not self.reachable:
            return None, "gh: connection reset by peer"
        src = self.root / str(tag)
        if not src.is_dir():
            return None, "release not found"
        dest = Path(dest_dir)
        dest.mkdir(parents=True, exist_ok=True)
        files = {}
        for item in sorted(src.iterdir()):
            target = dest / item.name
            shutil.copy2(item, target)
            files[item.name] = target
        return files, ""

    def delete(self, tag: str) -> None:
        self.deleted.append(str(tag))
        shutil.rmtree(self.root / str(tag), ignore_errors=True)


# --- sahte uretim (paralı cagrilarin tek noktasi) -----------------------------

class RecordingProducer:
    """Yalniz EKSIK cekimi uretir, gercek deftere GERCEK harcama yazar."""

    def __init__(self):
        self.calls = 0
        self.generated_shots: list[int] = []

    def __call__(self, slug, plan, dry_run=False, chain_start_url=None,
                 typed_result=True, **kwargs):
        self.calls += 1
        number = int(plan["episode"]["number"])
        bible = Bible.load(slug)
        qc_cfg = critic.qc_config(bible)
        root = shots_dir(slug, number)
        root.mkdir(parents=True, exist_ok=True)
        for shot in plan["shots"]:
            n = int(shot["n"])
            clip = root / f"shot_{n:02d}.mp4"
            if clip.exists() and critic.qc_pass_exists(
                slug, number, n, critic.content_sha256(clip), qc_cfg
            ):
                continue
            _write_mp4(clip, SHOT_COLORS[(n - 1) % len(SHOT_COLORS)])
            self.generated_shots.append(n)
            assert credit_gate.record_episode_spend(slug, number, SHOT_CREDITS)
            critic._log_event(slug, {
                "event": "qc_pass", "episode": number, "shot": n, "attempt": 0,
                "content_sha256": critic.content_sha256(clip),
                "clip": clip.name, "face_present": False,
            })
        master = episode_dir(slug, number) / f"ep{number:02d}_master.mp4"
        _write_mp4(master, "0x123456", seconds=2.0)
        return produce.ProduceResult("ok", master)


class RecordingUploader:
    """Platform basina sonuc uretir ve HER cagriyi sayar (mukerrer gonderi kaniti)."""

    def __init__(self, outcomes: dict[str, object]):
        self.outcomes = outcomes
        self.calls: list[str] = []

    FORBIDDEN = object()   # bu platforma yapilan her cagri MUKERRER gonderidir

    def __call__(self, src, title, desc, user=None, platform="youtube",
                 tags="", social_caption="", **kwargs):
        self.calls.append(platform)
        outcome = self.outcomes.get(platform)
        if outcome is RecordingUploader.FORBIDDEN:
            raise AssertionError(f"MUKERRER GONDERI: {platform} ikinci kez yuklendi")
        return outcome

    def count(self, platform: str) -> int:
        return len([c for c in self.calls if c == platform])


# --- ortam --------------------------------------------------------------------

class Env:
    def __init__(self, tmp_path: Path, *, cap: int = 1000,
                 platforms: list[str] | None = None,
                 required: list[str] | None = None):
        self.tmp = tmp_path
        self.data_root = tmp_path / "channel"
        self.artifact_root = tmp_path / "output" / "series"
        self.remote = tmp_path / "remote"
        self.ledger = tmp_path / "credits_ledger.json"
        self.cost_log = tmp_path / "logs" / "cost_tracking.json"
        self.cap = cap
        self.platforms = platforms or ["youtube"]
        self.required = required or ["youtube"]
        self.store = FakeReleaseStore(self.remote)
        self.alerts: list[str] = []
        (self.data_root / SLUG / "plans").mkdir(parents=True, exist_ok=True)
        self.artifact_root.mkdir(parents=True, exist_ok=True)
        self.remote.mkdir(parents=True, exist_ok=True)
        self._write_bible()
        self._write_meta()
        self._write_plan()

    # -- kalici kaynak dosyalar --
    @property
    def series_data(self) -> Path:
        return self.data_root / SLUG

    def _write_bible(self) -> None:
        (self.series_data / "bible.json").write_text(json.dumps({
            "series": {
                "slug": SLUG,
                "title": "Durable Lab",
                "state_machine_version": 2,
                "engine": "omni",
                "aspect_ratio": "9:16",
                "resolution": "1080p",
                "required_platforms": list(self.required),
                "credit_hard_cap": True,
                "credit_hard_cap_value": self.cap,
                "durable_credit_ledger": True,
                "durable_artifacts": True,
                "qc": {
                    "enabled": True,
                    "require_no_face": True,
                    "revalidate_cache": True,
                },
            },
            "art_style": "plain documentary realism",
            "characters": [],
            "environments": [{
                "id": "kitchen_counter",
                "name": "kitchen counter",
                "desc": "a worn kitchen counter in daylight",
                "ref_image_url": "https://example.invalid/env-v1.png",
            }],
            "props": [],
        }, ensure_ascii=False, indent=2), encoding="utf-8")

    def _write_meta(self) -> None:
        (self.series_data / "series.json").write_text(json.dumps({
            "slug": SLUG,
            "base_title": "Durable Lab",
            "logline": "one episode that must survive a run boundary",
            "language": "en",
            "upload_profile": "durable-profile",
            "platforms": list(self.platforms),
            "hashtags": "#shorts",
            "total_parts": 3,
            "next_part": 1,
            "status": "active",
            "publish_mode": "auto",
            "parts": {},
        }, ensure_ascii=False, indent=2), encoding="utf-8")

    def plan_path(self) -> Path:
        return self.series_data / "plans" / "part01.json"

    def _write_plan(self) -> None:
        self.plan_path().write_text(json.dumps({
            "episode": {"number": 1, "title": "Something Is WRONG With This ICE CUBE"},
            "shots": [
                {"n": i, "duration": 6, "prompt": f"shot {i} prompt v1"}
                for i in range(1, 5)
            ],
            "prop_ref_urls": ["https://example.invalid/prop-v1.png"],
            "ref_prompt_sha256": "a" * 64,
        }, ensure_ascii=False, indent=2), encoding="utf-8")

    # -- durum okuma --
    def meta_data(self) -> dict:
        return json.loads((self.series_data / "series.json").read_text(encoding="utf-8"))

    def part(self, n: int = 1) -> dict:
        return self.meta_data()["parts"][str(n)]

    def ledger_bytes(self) -> bytes:
        return self.ledger.read_bytes() if self.ledger.exists() else b""

    def spent(self, n: int = 1) -> float:
        """GERCEK kalici defterden bu bolumun toplam harcamasini oku."""
        if not self.ledger.exists():
            return 0.0
        data = json.loads(self.ledger.read_text(encoding="utf-8"))
        return float((data.get("episode_spend") or {}).get(f"{SLUG}:{n}", 0.0))

    def wipe_working_files(self) -> None:
        """Birinci kosunun TUM calisma dosyalarini sil (bulutta temiz checkout)."""
        shutil.rmtree(self.tmp / "output", ignore_errors=True)
        self.artifact_root.mkdir(parents=True, exist_ok=True)

    def patches(self, producer, uploader, *, pop_failure=None):
        stack = ExitStack()
        p = stack.enter_context
        import series.bible as bible_mod

        p(mock.patch.object(bible_mod, "_SEARCH_ROOTS", [self.data_root]))
        p(mock.patch.object(bible_mod, "SERIES_DIR", self.artifact_root))
        p(mock.patch.object(credit_gate, "LEDGER_PATH", self.ledger))
        p(mock.patch.object(cost_tracker, "COST_LOG", self.cost_log))
        p(mock.patch.object(series_runner, "check_credit",
                            return_value={"balance": 100000}))
        p(mock.patch.object(series_runner.produce, "produce_episode",
                            side_effect=producer))
        p(mock.patch.object(series_runner, "_persist_release",
                            side_effect=self.store.persist))
        p(mock.patch.object(series_runner, "_fetch_release_assets",
                            side_effect=self.store.fetch))
        p(mock.patch.object(series_runner, "_delete_release",
                            side_effect=self.store.delete))
        p(mock.patch.object(series_runner, "upload_to_platform",
                            side_effect=uploader))
        p(mock.patch.object(series_runner, "pop_upload_failure",
                            side_effect=pop_failure or (lambda platform: None)))
        p(mock.patch.object(series_runner.time, "sleep"))
        p(mock.patch.object(series_runner, "_alert",
                            side_effect=lambda msg: self.alerts.append(msg) or True))
        return stack

    def run(self, producer, uploader, *, pop_failure=None) -> bool:
        with self.patches(producer, uploader, pop_failure=pop_failure):
            return series_runner.run_next(SLUG, publish=True, force=True)


def _env(tmp_path: Path, **kwargs) -> Env:
    _require_ffmpeg()
    return Env(tmp_path, **kwargs)


def _first_run(env: Env, uploader: RecordingUploader, **kwargs) -> RecordingProducer:
    """Uretimi basarili, yayini eksik birakan birinci kosu."""
    producer = RecordingProducer()
    assert env.run(producer, uploader, **kwargs) is False
    assert producer.generated_shots == [1, 2, 3, 4]
    assert env.spent() == 4 * SHOT_CREDITS
    assert env.meta_data()["next_part"] == 1
    return producer


# --- 1) Iki kosuluk kanit -----------------------------------------------------

def test_second_run_recovers_artifact_and_regenerates_zero_shots(tmp_path: Path):
    env = _env(tmp_path)
    failing = RecordingUploader({"youtube": None})
    first = _first_run(env, failing)

    # Birinci kosu eseri KALICILASTIRDI (publish_mode 'auto' oldugu halde).
    assert env.store.persist_calls == [f"pending-{SLUG}-part1"]
    assert env.part()["artifact"]["release_tag"] == f"pending-{SLUG}-part1"

    ledger_after_first = env.ledger_bytes()
    entries_after_first = len(json.loads(ledger_after_first)["entries"])

    # Calisma dosyalari SILINIR; yalniz kalici olanlar kalir.
    env.wipe_working_files()
    assert not shots_dir(SLUG, 1).exists()
    assert not (episode_dir(SLUG, 1) / "ep01_master.mp4").exists()
    assert (env.series_data / "qc_log.jsonl").exists()

    # Kurtarma OLMASAYDI tamamlanma kapisi bu bolumu oldururdu: tam olarak
    # part 28'de olculen tablo (kalan < asgari < tavan).
    bible = None
    plan = json.loads(env.plan_path().read_text(encoding="utf-8"))
    with env.patches(first, failing):
        bible = Bible.load(SLUG)
        minimum = produce.minimum_remaining_completion_cost(SLUG, 1, bible, plan)
        remaining = env.cap - env.spent()
    assert minimum == 4 * CONSERVATIVE_PER_SHOT
    assert remaining < minimum

    second = RecordingProducer()
    winning = RecordingUploader({"youtube": {"results": {"youtube": {"video_id": "yt-2"}}}})
    assert env.run(second, winning) is True

    # SIFIR yeniden uretim, SIFIR taze harcama, tavan asilmadi.
    assert second.calls == 0
    assert second.generated_shots == []
    assert env.spent() == 4 * SHOT_CREDITS <= env.cap
    assert json.loads(env.ledger_bytes())["entries"] == json.loads(ledger_after_first)["entries"]
    assert len(json.loads(env.ledger_bytes())["entries"]) == entries_after_first

    # Eser indirildi, bolum yayinlandi, kuyruk ilerledi.
    assert env.store.download_calls == 1
    assert env.part()["status"] == "published"
    assert env.part()["platforms_ok"] == ["youtube"]
    assert env.meta_data()["next_part"] == 2
    # Yayin tamamlandiktan SONRA kalici eser birakilir.
    assert env.store.deleted == [f"pending-{SLUG}-part1"]
    assert "artifact" not in env.part()


# --- 2) Kimlik: plan ve referans degisince eser GECERSIZ ----------------------

def test_plan_change_invalidates_artifact_and_forces_regeneration(tmp_path: Path):
    env = _env(tmp_path, cap=5000)
    failing = RecordingUploader({"youtube": None})
    _first_run(env, failing)
    env.wipe_working_files()

    plan = json.loads(env.plan_path().read_text(encoding="utf-8"))
    plan["shots"][2]["prompt"] = "shot 3 prompt v2 (yeniden yazildi)"
    env.plan_path().write_text(json.dumps(plan, ensure_ascii=False, indent=2),
                               encoding="utf-8")

    second = RecordingProducer()
    winning = RecordingUploader({"youtube": {"results": {"youtube": {"video_id": "yt-3"}}}})
    assert env.run(second, winning) is True
    # Bayat eser KABUL EDILMEDI: bolum bastan uretildi.
    assert second.generated_shots == [1, 2, 3, 4]
    assert env.spent() == 8 * SHOT_CREDITS


def test_reference_change_invalidates_artifact(tmp_path: Path):
    env = _env(tmp_path, cap=5000)
    _first_run(env, RecordingUploader({"youtube": None}))
    env.wipe_working_files()

    bible_path = env.series_data / "bible.json"
    data = json.loads(bible_path.read_text(encoding="utf-8"))
    data["environments"][0]["ref_image_url"] = "https://example.invalid/env-v2.png"
    bible_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    second = RecordingProducer()
    winning = RecordingUploader({"youtube": {"results": {"youtube": {"video_id": "yt-4"}}}})
    assert env.run(second, winning) is True
    assert second.generated_shots == [1, 2, 3, 4]


def test_identity_fields_reject_stale_plan_reference_and_qc_policy(tmp_path: Path):
    """``series:episode`` + bayt butunlugu YETMEZ; dort eksen de baglanir."""
    env = _env(tmp_path)
    _first_run(env, RecordingUploader({"youtube": None}))

    with env.patches(RecordingProducer(), RecordingUploader({})):
        bible = Bible.load(SLUG)
        plan = json.loads(env.plan_path().read_text(encoding="utf-8"))
        manifest = json.loads(
            (env.remote / f"pending-{SLUG}-part1"
             / durable_artifact.MANIFEST_ASSET_NAME).read_text(encoding="utf-8")
        )
        video = env.remote / f"pending-{SLUG}-part1" / manifest["video_name"]

        # Bozulmamis eser gecer.
        assert durable_artifact.verify(SLUG, 1, bible, plan, manifest, video).status == "ok"

        # 1) Normalize TAM PLAN ozeti.
        moved = dict(plan)
        moved["shots"] = [dict(s) for s in plan["shots"]]
        moved["shots"][0]["prompt"] = "degisti"
        verdict = durable_artifact.verify(SLUG, 1, bible, moved, manifest, video)
        assert verdict.status == "invalid" and "plan" in verdict.reason

        # Anahtar SIRASI kimligi degistirmez (normalize edilmis ozet).
        reordered = dict(reversed(list(plan.items())))
        assert durable_artifact.verify(
            SLUG, 1, bible, reordered, manifest, video).status == "ok"

        # 2) Referans icerigi.
        changed_ref = json.loads(json.dumps(bible.data))
        changed_ref["environments"][0]["ref_image_url"] = "https://example.invalid/other.png"
        verdict = durable_artifact.verify(
            SLUG, 1, Bible(changed_ref), plan, manifest, video)
        assert verdict.status == "invalid" and "referans" in verdict.reason

        # 3) QC politika parmak izi.
        changed_qc = json.loads(json.dumps(bible.data))
        changed_qc["series"]["qc"]["artifact_threshold"] = 3
        verdict = durable_artifact.verify(
            SLUG, 1, Bible(changed_qc), plan, manifest, video)
        assert verdict.status == "invalid" and "QC politikasi" in verdict.reason

        # 4) Bayt butunlugu: indirme BASARILI, icerik bozuk -> KESIN bozulma.
        corrupt = env.tmp / "corrupt.mp4"
        corrupt.write_bytes(video.read_bytes() + b"\x00bozuk")
        verdict = durable_artifact.verify(SLUG, 1, bible, plan, manifest, corrupt)
        assert verdict.status == "invalid" and "bozul" in verdict.reason

        # Baska bolume ait manifest de kesin reddedilir.
        foreign = dict(manifest, episode=2)
        assert durable_artifact.verify(
            SLUG, 1, bible, plan, foreign, video).status == "invalid"


def test_media_probe_tool_failure_blocks_but_confirmed_no_stream_is_invalid(tmp_path: Path):
    env = _env(tmp_path)
    _first_run(env, RecordingUploader({"youtube": None}))

    with env.patches(RecordingProducer(), RecordingUploader({})):
        bible = Bible.load(SLUG)
        plan = json.loads(env.plan_path().read_text(encoding="utf-8"))
        manifest = json.loads(
            (env.remote / f"pending-{SLUG}-part1"
             / durable_artifact.MANIFEST_ASSET_NAME).read_text(encoding="utf-8")
        )
        video = env.remote / f"pending-{SLUG}-part1" / manifest["video_name"]

        with mock.patch.object(ffmpeg_tools.subprocess, "run", side_effect=FileNotFoundError):
            unavailable = durable_artifact.verify(SLUG, 1, bible, plan, manifest, video)
        with mock.patch.object(
            ffmpeg_tools.subprocess, "run",
            return_value=subprocess.CompletedProcess([], 0, stdout="", stderr=""),
        ):
            no_stream = durable_artifact.verify(SLUG, 1, bible, plan, manifest, video)

    assert unavailable.status == "blocked"
    assert no_stream.status == "invalid"


# --- 3) QC gecis kaniti olmadan geri yuklenen cekim KABUL EDILMEZ -------------

def test_artifact_without_persisted_qc_evidence_is_not_accepted(tmp_path: Path):
    env = _env(tmp_path)
    _first_run(env, RecordingUploader({"youtube": None}))
    env.wipe_working_files()
    before = env.ledger_bytes()

    # Kalici QC kaniti kaybolsun (cekim 3'un qc_pass satiri silinir).
    log = env.series_data / "qc_log.jsonl"
    kept = [
        line for line in log.read_text(encoding="utf-8").splitlines()
        if not (line.strip() and json.loads(line).get("shot") == 3)
    ]
    log.write_text("\n".join(kept) + "\n", encoding="utf-8")

    second = RecordingProducer()
    assert env.run(second, RecordingUploader({"youtube": None})) is False
    # Kanit yoksa eser KABUL EDILMEZ; ama belirsizlik taze krediye de donmez.
    assert second.calls == 0
    assert env.ledger_bytes() == before
    assert any("QC gec" in a or "QC geç" in a for a in env.alerts), env.alerts


def test_manifest_evidence_is_rejudged_against_todays_qc_policy(tmp_path: Path):
    """Esere yapisik kanit, BUGUNKU kapilarla yeniden yargilanir."""
    env = _env(tmp_path)
    _first_run(env, RecordingUploader({"youtube": None}))
    manifest = json.loads(
        (env.remote / f"pending-{SLUG}-part1"
         / durable_artifact.MANIFEST_ASSET_NAME).read_text(encoding="utf-8")
    )
    assert set(manifest["shots"]) == {"1", "2", "3", "4"}
    for entry in manifest["shots"].values():
        assert entry["qc_pass"]["event"] == "qc_pass"
        assert entry["qc_pass"]["face_present"] is False

    with env.patches(RecordingProducer(), RecordingUploader({})):
        bible = Bible.load(SLUG)
        plan = json.loads(env.plan_path().read_text(encoding="utf-8"))
        video = env.remote / f"pending-{SLUG}-part1" / manifest["video_name"]
        broken = json.loads(json.dumps(manifest))
        broken["shots"]["2"]["qc_pass"]["face_present"] = True
        verdict = durable_artifact.verify(SLUG, 1, bible, plan, broken, video)
    assert verdict.status == "blocked"
    assert "QC" in verdict.reason


# --- 4) Depolama erisilemezken TAZE HARCAMA YOK ------------------------------

def test_unreachable_storage_stops_the_run_without_fresh_spend(tmp_path: Path):
    env = _env(tmp_path)
    _first_run(env, RecordingUploader({"youtube": None}))
    env.wipe_working_files()
    before = env.ledger_bytes()

    env.store.reachable = False
    second = RecordingProducer()
    assert env.run(second, RecordingUploader({"youtube": None})) is False

    assert second.calls == 0                     # tek bir ucretli cagri yok
    assert env.ledger_bytes() == before          # defter BIT-DEGISMEZ
    assert env.spent() == 4 * SHOT_CREDITS
    assert env.meta_data()["next_part"] == 1
    assert env.part()["artifact"]["release_tag"] == f"pending-{SLUG}-part1"
    assert env.alerts and "artifact" in env.alerts[-1]
    assert "connection reset" in env.alerts[-1]


def test_vanished_release_is_uncertain_not_a_licence_to_respend(tmp_path: Path):
    """404 ile ag arizasi ayirt edilemez; ikisi de yeniden uretimi HAKLI CIKARMAZ."""
    env = _env(tmp_path)
    _first_run(env, RecordingUploader({"youtube": None}))
    env.wipe_working_files()
    before = env.ledger_bytes()

    shutil.rmtree(env.remote / f"pending-{SLUG}-part1")
    second = RecordingProducer()
    assert env.run(second, RecordingUploader({"youtube": None})) is False
    assert second.calls == 0
    assert env.ledger_bytes() == before
    assert env.alerts and "release not found" in env.alerts[-1]


def test_failed_release_upload_leaves_intent_and_blocks_regeneration(tmp_path: Path):
    env = _env(tmp_path, cap=5000)
    first = RecordingProducer()
    failing = RecordingUploader({"youtube": None})
    with env.patches(first, failing), mock.patch.object(
        series_runner, "_persist_release", return_value=None,
    ):
        assert series_runner.run_next(SLUG, publish=True, force=True) is False

    intent = env.part()["artifact"]
    assert intent["release_tag"] == f"pending-{SLUG}-part1"
    assert intent["confirmed"] is False
    spent = env.spent()
    env.wipe_working_files()

    second = RecordingProducer()
    assert env.run(second, RecordingUploader({"youtube": None})) is False
    assert env.store.download_calls == 1
    assert second.calls == 0
    assert env.spent() == spent


def test_release_intent_recovers_crash_after_remote_create(tmp_path: Path):
    env = _env(tmp_path)
    first = RecordingProducer()

    def persist_then_crash(slug, n, video_path, extra_assets=None):
        env.store.persist(slug, n, video_path, extra_assets=extra_assets)
        raise RuntimeError("crash after gh release create")

    with env.patches(first, RecordingUploader({})), mock.patch.object(
        series_runner, "_persist_release", side_effect=persist_then_crash,
    ), pytest.raises(RuntimeError, match="after gh release create"):
        series_runner.run_next(SLUG, publish=True, force=True)

    assert env.part()["artifact"]["confirmed"] is False
    assert (env.remote / f"pending-{SLUG}-part1").is_dir()
    spent = env.spent()
    env.wipe_working_files()

    second = RecordingProducer()
    winning = RecordingUploader({"youtube": {"results": {"youtube": {"video_id": "yt"}}}})
    assert env.run(second, winning) is True
    assert second.calls == 0
    assert env.spent() == spent


# --- 5) Yayin kurtarma: zaten yayinlanmis platform ATLANIR --------------------

def _three_platform_env(tmp_path: Path) -> Env:
    return _env(
        tmp_path,
        platforms=["youtube", "instagram", "tiktok"],
        required=["youtube"],
    )


def test_remote_success_then_local_crash_skips_already_published_platforms(tmp_path: Path):
    env = _three_platform_env(tmp_path)
    partial = RecordingUploader({
        "youtube": None,
        "instagram": {"results": {"instagram": {"media_id": "ig-1"}}},
        "tiktok": {"results": {"tiktok": {"post_id": "tt-1"}}},
    })
    _first_run(env, partial)

    # Uzak taraf IG ve TikTok icin BASARILI dondu ve bu KALICI olarak yazildi.
    state = env.part()["publish_state"]
    assert state["instagram"]["status"] == "ok" and state["instagram"]["identifier"] == "ig-1"
    assert state["tiktok"]["status"] == "ok" and state["tiktok"]["identifier"] == "tt-1"
    assert state["youtube"]["status"] == "failed"

    # Yerel cokme: calisma dosyalari gitti, kalici durum kaldi.
    env.wipe_working_files()

    second = RecordingProducer()
    retry = RecordingUploader({
        "youtube": {"results": {"youtube": {"video_id": "yt-9"}}},
        # cagrilirsa mukerrer gonderi demektir: uploader AssertionError firlatir
        "instagram": RecordingUploader.FORBIDDEN,
        "tiktok": RecordingUploader.FORBIDDEN,
    })
    assert env.run(second, retry) is True

    assert second.calls == 0
    assert retry.calls == ["youtube"]            # SADECE eksik platform
    assert retry.count("instagram") == 0
    assert retry.count("tiktok") == 0
    assert sorted(env.part()["platforms_ok"]) == ["instagram", "tiktok", "youtube"]
    assert env.meta_data()["next_part"] == 2


def test_publish_state_from_old_video_is_ignored_after_regeneration(tmp_path: Path):
    env = _env(
        tmp_path, cap=5000,
        platforms=["youtube", "instagram", "tiktok"], required=["youtube"],
    )
    _first_run(env, RecordingUploader({
        "youtube": None,
        "instagram": {"results": {"instagram": {"media_id": "ig-old"}}},
        "tiktok": {"results": {"tiktok": {"post_id": "tt-old"}}},
    }))
    old_state = env.part()["publish_state"]
    assert all(entry.get("video_sha256") for entry in old_state.values())
    old_hash = old_state["instagram"]["video_sha256"]

    env.wipe_working_files()
    plan = json.loads(env.plan_path().read_text(encoding="utf-8"))
    plan["shots"][0]["prompt"] = "new artifact identity"
    env.plan_path().write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")

    class ChangedMasterProducer(RecordingProducer):
        def __call__(self, *args, **kwargs):
            result = super().__call__(*args, **kwargs)
            _write_mp4(Path(result.path), "0xabcdef", seconds=2.0)
            return result

    uploader = RecordingUploader({
        "youtube": {"results": {"youtube": {"video_id": "yt-new"}}},
        "instagram": {"results": {"instagram": {"media_id": "ig-new"}}},
        "tiktok": {"results": {"tiktok": {"post_id": "tt-new"}}},
    })
    assert env.run(ChangedMasterProducer(), uploader) is True

    assert uploader.calls == ["youtube", "instagram", "tiktok"]
    new_state = env.part()["publish_state"]
    assert all(entry["video_sha256"] != old_hash for entry in new_state.values())


def test_pending_request_id_is_reconciled_before_any_repost(tmp_path: Path):
    env = _three_platform_env(tmp_path)
    async_failure = {
        "async": True,
        "reason": "600s dogrulama zaman asimi",
        "request_id": "ig-request-1",
        "job_id": "ig-job-1",
    }
    partial = RecordingUploader({
        "youtube": None,
        "instagram": None,
        "tiktok": {"results": {"tiktok": {"post_id": "tt-1"}}},
    })
    _first_run(
        env, partial,
        pop_failure=lambda platform: async_failure if platform == "instagram" else None,
    )

    # BEKLEYEN is kimligi kalicilastirildi.
    pending = env.part()["publish_state"]["instagram"]
    assert pending["status"] == "pending"
    assert pending["request_id"] == "ig-request-1"
    assert pending["job_id"] == "ig-job-1"

    env.wipe_working_files()

    # Mutabakat "success" derse platform yeniden GONDERILMEZ.
    reconciled = {"results": [{"platform": "instagram", "success": True,
                               "publication_id": "ig-late"}]}
    second = RecordingProducer()
    retry = RecordingUploader({
        "youtube": {"results": {"youtube": {"video_id": "yt-9"}}},
        "instagram": RecordingUploader.FORBIDDEN,
        "tiktok": RecordingUploader.FORBIDDEN,
    })
    with env.patches(second, retry), mock.patch.object(
        series_runner, "reconcile_async_upload",
        return_value=("success", "platform sonucu success=true", reconciled),
    ) as reconcile:
        assert series_runner.run_next(SLUG, publish=True, force=True) is True

    reconcile.assert_called_once()
    assert reconcile.call_args.kwargs["request_id"] == "ig-request-1"
    assert retry.count("instagram") == 0
    assert sorted(env.part()["platforms_ok"]) == ["instagram", "tiktok", "youtube"]


def test_unresolved_pending_job_is_never_reposted(tmp_path: Path):
    env = _three_platform_env(tmp_path)
    async_failure = {
        "async": True, "reason": "belirsiz", "request_id": "ig-request-2", "job_id": None,
    }
    partial = RecordingUploader({
        "youtube": None,
        "instagram": None,
        "tiktok": {"results": {"tiktok": {"post_id": "tt-1"}}},
    })
    _first_run(
        env, partial,
        pop_failure=lambda platform: async_failure if platform == "instagram" else None,
    )
    assert env.part()["publish_state"]["instagram"]["status"] == "pending"
    env.wipe_working_files()

    # Is HALA belirsizse ikinci gonderi YAPILMAZ; yalniz eksik platform denenir.
    retry = RecordingUploader({
        "youtube": {"results": {"youtube": {"video_id": "yt-9"}}},
        "instagram": RecordingUploader.FORBIDDEN,
        "tiktok": RecordingUploader.FORBIDDEN,
    })
    with env.patches(RecordingProducer(), retry), mock.patch.object(
        series_runner, "reconcile_async_upload",
        return_value=("pending", "is hala isleniyor", {"status": "processing"}),
    ):
        assert series_runner.run_next(SLUG, publish=True, force=True) is True
    assert retry.calls == ["youtube"]
    assert retry.count("instagram") == 0
    assert env.part()["publish_state"]["instagram"]["status"] == "pending"
    assert "instagram" not in env.part()["platforms_ok"]


# --- 6) Kapali seride davranis BIT-DEGISMEZ ----------------------------------

def test_flag_off_series_keeps_todays_behaviour(tmp_path: Path):
    """durable_artifacts kapaliyken ne Release yazilir ne publish_state tutulur."""
    env = _env(tmp_path)
    bible_path = env.series_data / "bible.json"
    data = json.loads(bible_path.read_text(encoding="utf-8"))
    data["series"].pop("durable_artifacts")
    bible_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    producer = RecordingProducer()
    uploader = RecordingUploader({"youtube": {"results": {"youtube": {"video_id": "yt-1"}}}})
    assert env.run(producer, uploader) is True
    assert env.store.persist_calls == []
    assert env.store.download_calls == 0
    assert "artifact" not in env.part()
    assert "publish_state" not in env.part()


def test_approval_flag_off_repersists_even_with_stale_release_tag(tmp_path: Path):
    env = _env(tmp_path)
    bible_path = env.series_data / "bible.json"
    bible_data = json.loads(bible_path.read_text(encoding="utf-8"))
    bible_data["series"].pop("durable_artifacts")
    bible_path.write_text(json.dumps(bible_data, ensure_ascii=False, indent=2), encoding="utf-8")
    meta_path = env.series_data / "series.json"
    meta_data = json.loads(meta_path.read_text(encoding="utf-8"))
    meta_data["publish_mode"] = "approval"
    meta_data["parts"]["1"] = {"status": "planned", "release_tag": "stale-release"}
    meta_path.write_text(json.dumps(meta_data, ensure_ascii=False, indent=2), encoding="utf-8")

    with env.patches(RecordingProducer(), RecordingUploader({})), \
            mock.patch.object(series_runner, "_sample_frames", return_value=[]), \
            mock.patch.object(series_runner.notifier, "enabled", return_value=True), \
            mock.patch.object(series_runner.notifier, "request_approval", return_value=17):
        assert series_runner.run_next(SLUG, publish=True, force=True) is True

    assert env.store.persist_calls == [f"pending-{SLUG}-part1"]
    assert env.part()["release_tag"] == f"pending-{SLUG}-part1"

    video = Path(env.part()["video"])
    digest = critic.content_sha256(video)
    assert series_runner._artifact_release_for_video({
        "artifact": {
            "confirmed": True,
            "release_tag": "matching-release",
            "video_sha256": digest,
        },
    }, video) == "matching-release"
    assert series_runner._artifact_release_for_video({
        "artifact": {
            "confirmed": True,
            "release_tag": "stale-release",
            "video_sha256": "0" * 64,
        },
    }, video) is None


def test_approved_partial_publish_keeps_release_and_pointer(tmp_path: Path):
    env = _three_platform_env(tmp_path)
    video = tmp_path / "approved.mp4"
    _write_mp4(video, "0x334455")

    with env.patches(RecordingProducer(), RecordingUploader({})):
        meta = series_runner.SeriesMeta.load(SLUG)
        part = meta.get_part(1)
        part.update({
            "status": "awaiting_approval",
            "approved": True,
            "release_tag": f"pending-{SLUG}-part1",
            "video": str(video),
        })
        meta.save()
        with mock.patch.object(approver, "_download_release", return_value=video), \
                mock.patch.object(approver, "_publish_part", return_value=["instagram"]) as publish, \
                mock.patch.object(approver, "_cleanup_release") as cleanup, \
                mock.patch.object(approver, "_series_alert"):
            assert approver._publish_approved(meta, 1, part) is False

    assert meta.next_part == 1
    assert part["status"] == "awaiting_approval"
    publish.assert_called_once()
    assert publish.call_args.kwargs["durable"] is True
    cleanup.assert_not_called()


def test_recovered_episode_keeps_delivery_annotations(tmp_path: Path):
    """Dusen cekim ve butunluk notlari eserle birlikte kosu sinirini gecer."""
    env = _env(tmp_path)

    class DroppingProducer(RecordingProducer):
        def __call__(self, *args, **kwargs):
            result = super().__call__(*args, **kwargs)
            return produce.ProduceResult(
                "ok", result.path, dropped_shots=[4],
                coherence={"degraded": True, "loop_closed": False},
            )

    assert env.run(DroppingProducer(), RecordingUploader({"youtube": None})) is False
    env.wipe_working_files()

    second = RecordingProducer()
    winning = RecordingUploader({"youtube": {"results": {"youtube": {"video_id": "yt-5"}}}})
    assert env.run(second, winning) is True
    assert second.calls == 0
    part = env.part()
    assert part["dropped_shots"] == [4]
    assert part["coherence"]["degraded"] is True
    assert any("loop kapanmadi" in a for a in env.alerts), env.alerts
