"""Kill-gate olcumu: sabit yasta L/1k ve C/1k, ve karar VERMEYI reddedebilen rapor.

Plan (PLAN_GERCEKCILIK_v1 > KILL-GATE): donmus stack uzerinde 10 ardisik yayin, her
video 72 saat yasinda olculur.
  * Oldur:  L/1k medyani < 10  -> icerik havuzu yeniden ele alinir
  * Alarm:  C/1k medyani < 0.3 -> begeni gelse bile yorum motoru calismiyor demektir
  * Basari: L/1k >= 30 VE C/1k >= 1.0
  * Ara bant (L/1k 10-29): "ilerleme var", en fazla BIR ek karar penceresi

Bu modul olcumu ve karari AYIRIR: ham snapshot'lardan bolum metriklerini cikarir,
sonra yalnizca pencere DOLU ve olgun oldugunda karar uretir. Olgunlasmamis veride
karar uretmek, kill-gate'i anlamsiz kilar; o yuzden burada acikca reddedilir.

Views 0 olan bir bolumde oran tanimsizdir: bolum "olculemedi" sayilir, uydurma sifir
uretilmez.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from statistics import median

MATURITY_HOURS = 72
LATEST_USABLE_DAYS = 7

KILL_L_PER_1K = 10.0
SUCCESS_L_PER_1K = 30.0
COMMENT_ALARM_C_PER_1K = 0.3
SUCCESS_C_PER_1K = 1.0
DEFAULT_WINDOW = 10


@dataclass
class EpisodeMetric:
    video_id: str
    published: datetime
    views: int | None = None
    likes: int | None = None
    comments: int | None = None
    measured_at: date | None = None
    reason: str | None = None
    stack_sha256: str | None = None

    @property
    def mature(self) -> bool:
        return self.reason is None and bool(self.views)

    @property
    def likes_per_1k(self) -> float | None:
        if not self.mature or self.likes is None:
            return None
        return (float(self.likes) / float(self.views)) * 1000.0

    @property
    def comments_per_1k(self) -> float | None:
        if not self.mature or self.comments is None:
            return None
        return (float(self.comments) / float(self.views)) * 1000.0


@dataclass
class KillGateReport:
    window: int
    episodes: list[EpisodeMetric] = field(default_factory=list)
    verdict: str = "karar_yok"
    reasons: list[str] = field(default_factory=list)
    median_l_per_1k: float | None = None
    median_c_per_1k: float | None = None
    comment_alarm: bool = False

    @property
    def mature_episodes(self) -> list[EpisodeMetric]:
        return [episode for episode in self.episodes if episode.mature]


def measure_episode(snapshots, channel_name: str, video_id: str,
                    published: datetime,
                    stack_sha256: str | None = None) -> EpisodeMetric:
    """Yayindan >=72 saat sonraki ILK kullanilabilir snapshot'tan olc."""
    metric = EpisodeMetric(
        video_id=video_id,
        published=published,
        stack_sha256=stack_sha256,
    )
    target = published + timedelta(hours=MATURITY_HOURS)
    latest_usable = published.date() + timedelta(days=LATEST_USABLE_DAYS)
    for snapshot_date, snapshot in snapshots:
        if snapshot_date < target.date():
            continue
        if snapshot_date > latest_usable:
            metric.reason = "gec_snapshot"
            return metric
        channel = (snapshot.get("channels") or {}).get(channel_name)
        if not isinstance(channel, dict):
            continue
        video = (channel.get("videos") or {}).get(video_id)
        if not isinstance(video, dict):
            continue
        views = video.get("views")
        metric.views = int(views) if isinstance(views, (int, float)) else None
        metric.likes = int(video.get("likes") or 0)
        metric.comments = int(video.get("comments") or 0)
        metric.measured_at = snapshot_date
        if not metric.views:
            # Sifir izlenmede oran tanimsizdir; uydurma sifir uretmeyiz.
            metric.reason = "izlenme_yok"
        return metric
    metric.reason = "olgunlasmadi"
    return metric


def build_report(episodes: list[EpisodeMetric], window: int = DEFAULT_WINDOW) -> KillGateReport:
    """Pencere DOLU ve olgun degilse karar URETME; eksigi acikca soyle."""
    report = KillGateReport(window=window, episodes=list(episodes))
    mature = report.mature_episodes
    if len(report.episodes) < window:
        report.reasons.append(
            f"pencere dolmadi: {len(report.episodes)}/{window} yayin"
        )
    missing = [e for e in report.episodes if not e.mature]
    if missing:
        detail = ", ".join(f"{e.video_id}:{e.reason or 'bilinmiyor'}" for e in missing[:5])
        report.reasons.append(f"olculemeyen bolum var ({len(missing)}): {detail}")
    if len(mature) < window:
        report.verdict = "karar_yok"
        report.reasons.append(
            f"olgun olcum {len(mature)}/{window}; kill-gate karari VERILMEDI"
        )
        # Yine de gorunur olsun diye medyanlari hesapla ama karara sokma.
        if mature:
            report.median_l_per_1k = median(e.likes_per_1k for e in mature)
            report.median_c_per_1k = median(e.comments_per_1k for e in mature)
        return report

    report.median_l_per_1k = median(e.likes_per_1k for e in mature[:window])
    report.median_c_per_1k = median(e.comments_per_1k for e in mature[:window])
    report.comment_alarm = report.median_c_per_1k < COMMENT_ALARM_C_PER_1K
    if report.comment_alarm:
        report.reasons.append(
            f"YORUM ALARMI: C/1k medyani {report.median_c_per_1k:.2f} < "
            f"{COMMENT_ALARM_C_PER_1K:g}; yorum motoru calismiyor"
        )

    # Kill-gate yalniz ayni uretim tarifiyle uretilmis tam bir pencereyi tartar.
    # Kayit tarafindaki eksik iz burada sessizce sayilmaz; karar fail-closed kalir.
    decision_window = mature[:window]
    missing_stack = [e for e in decision_window if not e.stack_sha256]
    if missing_stack:
        videos = ", ".join(e.video_id for e in missing_stack)
        report.reasons.append(
            f"stack parmak izi yok ({len(missing_stack)} bolum): {videos}"
        )
        return report
    stacks = {e.stack_sha256 for e in decision_window}
    if len(stacks) > 1:
        short = ", ".join(sorted(stack[:8] for stack in stacks))
        report.reasons.append(
            f"pencerede {len(stacks)} farkli stack var: {short}; "
            "kill-gate donmus stack ister"
        )
        return report

    if report.median_l_per_1k < KILL_L_PER_1K:
        report.verdict = "oldur"
        report.reasons.append(
            f"L/1k medyani {report.median_l_per_1k:.1f} < {KILL_L_PER_1K:g}: "
            "icerik havuzu yeniden ele alinmali"
        )
    elif (report.median_l_per_1k >= SUCCESS_L_PER_1K
          and report.median_c_per_1k >= SUCCESS_C_PER_1K):
        report.verdict = "basari"
        report.reasons.append(
            f"L/1k {report.median_l_per_1k:.1f} >= {SUCCESS_L_PER_1K:g} ve "
            f"C/1k {report.median_c_per_1k:.2f} >= {SUCCESS_C_PER_1K:g}"
        )
    else:
        report.verdict = "ara_bant"
        report.reasons.append(
            f"L/1k medyani {report.median_l_per_1k:.1f} ara bantta "
            f"({KILL_L_PER_1K:g}-{SUCCESS_L_PER_1K:g}): en fazla BIR ek karar penceresi"
        )
    return report


def format_report(report: KillGateReport, series: str = "") -> str:
    lines = [f"KILL-GATE RAPORU{(' - ' + series) if series else ''}"]
    lines.append(f"pencere: {report.window} yayin | olgun olcum: {len(report.mature_episodes)}")
    decision_window = report.mature_episodes[:report.window]
    window_stacks = {e.stack_sha256 for e in decision_window if e.stack_sha256}
    if (len(decision_window) == report.window
            and len(window_stacks) == 1
            and all(e.stack_sha256 for e in decision_window)):
        lines.append(f"pencere stack: {next(iter(window_stacks))[:8]}")
    for episode in report.episodes:
        short_stack = episode.stack_sha256[:8] if episode.stack_sha256 else "yok"
        if episode.mature:
            lines.append(
                f"  {episode.video_id}: stack={short_stack} izlenme={episode.views} "
                f"L/1k={episode.likes_per_1k:.1f} C/1k={episode.comments_per_1k:.2f} "
                f"(olcum {episode.measured_at})"
            )
        else:
            lines.append(
                f"  {episode.video_id}: stack={short_stack} OLCULEMEDI ({episode.reason})"
            )
    if report.median_l_per_1k is not None:
        lines.append(f"medyan L/1k: {report.median_l_per_1k:.1f}")
        lines.append(f"medyan C/1k: {report.median_c_per_1k:.2f}")
    lines.append(f"KARAR: {report.verdict}")
    for reason in report.reasons:
        lines.append(f"  - {reason}")
    return "\n".join(lines)
