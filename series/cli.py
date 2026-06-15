"""
series CLI — İhsan için basit Rich menü + (benim çağırmam için) alt-komutlar.

Kullanım:
  python -m series.cli                                  → interaktif Rich menü
  python -m series.cli credit                           → Kie kredi bakiyesi (ücretsiz)
  python -m series.cli voices [erkek|kadın]             → preset ses tablosu
  python -m series.cli list                             → mevcut dizileri listele
  python -m series.cli setup-refs <slug> [--dry-run]    → referansları hazırla
  python -m series.cli produce <slug> <plan.json> [--dry-run]  → bölüm üret
  python -m series.cli cost-report <slug>               → maliyet/üretim raporu
"""

import os
import sys

# Her yerden çalışabilmek için proje kökünü path'e ekle
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

from core.kie_api import check_credit
from series import produce, report, voices
from series.bible import Bible, bible_path, episodes_dir, SERIES_DATA_DIR

console = Console()

_GENDER_TR = {"erkek": "male", "kadın": "female", "kadin": "female", "nötr": "ungendered"}


# ─── Komutlar ──────────────────────────────────────────────────────────────────

def cmd_credit():
    console.print("[cyan]Kie AI kredi bakiyesi sorgulanıyor...[/]")
    data = check_credit()
    if data:
        console.print(Panel(str(data), title="💰 Kredi", border_style="green"))
    else:
        console.print("[red]Kredi bilgisi alınamadı.[/]")


def cmd_voices(gender: str | None = None):
    g = _GENDER_TR.get((gender or "").lower(), gender)
    table = Table(title="🎙️ Gemini Omni Preset Sesleri", show_lines=False)
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Cinsiyet")
    table.add_column("Açıklama", style="dim")
    for v in voices.list_voices(g):
        table.add_row(v["id"], v["gender"], v["description"])
    console.print(table)
    if voices.CUSTOM_VOICES and not g:
        ct = Table(title="Özel Sesler (kieAudioId)")
        ct.add_column("ID", style="magenta", no_wrap=True)
        ct.add_column("Ad")
        ct.add_column("Açıklama", style="dim")
        for v in voices.CUSTOM_VOICES:
            ct.add_row(v["id"], v["name"], v["description"])
        console.print(ct)


def cmd_list():
    if not SERIES_DATA_DIR.exists():
        console.print("[yellow]Henüz dizi yok.[/]")
        return
    table = Table(title="📺 Diziler")
    table.add_column("Slug", style="cyan")
    table.add_column("Başlık")
    table.add_column("Karakter")
    table.add_column("Bölüm klasörü")
    found = False
    for d in sorted(SERIES_DATA_DIR.iterdir()):
        if not (d.is_dir() and bible_path(d.name).exists()):
            continue
        found = True
        b = Bible.load(d.name)
        eps = episodes_dir(d.name)
        ep_count = len([x for x in eps.iterdir() if x.is_dir()]) if eps.exists() else 0
        table.add_row(b.slug, b.title, str(len(b.characters)), str(ep_count))
    if found:
        console.print(table)
    else:
        console.print("[yellow]Henüz dizi yok.[/]")


def cmd_setup_refs(slug: str, dry_run: bool = False):
    if not bible_path(slug).exists():
        console.print(f"[red]Bible bulunamadı: {bible_path(slug)}[/]")
        return
    produce.setup_references(slug, dry_run=dry_run)


def cmd_produce(slug: str, plan_path: str, dry_run: bool = False):
    if not bible_path(slug).exists():
        console.print(f"[red]Bible bulunamadı: {bible_path(slug)}[/]")
        return
    if not os.path.exists(plan_path):
        console.print(f"[red]Plan dosyası yok: {plan_path}[/]")
        return
    result = produce.produce_episode(slug, plan_path, dry_run=dry_run)
    if result:
        console.print(Panel(str(result), title="🎬 Bölüm hazır", border_style="green"))


def cmd_cost_report(slug: str):
    s = report.summarize(slug)
    rows = report.read_rows(slug)
    table = Table(title=f"📊 {slug} — Üretim Raporu")
    for c in ("bölüm", "çekim", "karakterler", "sesler", "süre_sn", "kredi", "dolar", "durum"):
        table.add_column(c)
    for r in rows[-30:]:
        table.add_row(*(str(r.get(c, "")) for c in
                        ("bölüm", "çekim", "karakterler", "sesler", "süre_sn", "kredi", "dolar", "durum")))
    console.print(table)
    console.print(Panel(
        f"Çekim: {s['çekim_sayısı']}  |  Başarılı: {s['başarılı']}  |  "
        f"Toplam kredi: {s['toplam_kredi']}  |  ~${s['toplam_dolar']}",
        title="Özet", border_style="cyan"))


# ─── İnteraktif menü (İhsan için) ──────────────────────────────────────────────

def interactive_menu():
    while True:
        console.print(Panel.fit(
            "[bold]Gemini Omni Mini-Dizi Motoru[/]\n"
            "[1] Kredi durumu\n"
            "[2] Dizileri listele\n"
            "[3] Referansları hazırla\n"
            "[4] Bölüm üret\n"
            "[5] Maliyet raporu\n"
            "[6] Ses listesi\n"
            "[0] Çıkış",
            border_style="cyan"))
        choice = Prompt.ask("Seçim", choices=["0", "1", "2", "3", "4", "5", "6"], default="0")
        if choice == "0":
            break
        elif choice == "1":
            cmd_credit()
        elif choice == "2":
            cmd_list()
        elif choice == "3":
            slug = Prompt.ask("Dizi slug")
            dry = Confirm.ask("Dry-run (kredi harcamadan dene)?", default=True)
            cmd_setup_refs(slug, dry_run=dry)
        elif choice == "4":
            slug = Prompt.ask("Dizi slug")
            plan = Prompt.ask("Plan dosyası (episode_plan.json yolu)")
            dry = Confirm.ask("Dry-run (kredi harcamadan dene)?", default=True)
            cmd_produce(slug, plan, dry_run=dry)
        elif choice == "5":
            slug = Prompt.ask("Dizi slug")
            cmd_cost_report(slug)
        elif choice == "6":
            cmd_voices()


# ─── Argüman dağıtımı ──────────────────────────────────────────────────────────

def main(argv: list[str]):
    if not argv:
        interactive_menu()
        return
    cmd, rest = argv[0], argv[1:]
    dry = "--dry-run" in rest
    rest = [a for a in rest if a != "--dry-run"]

    if cmd == "credit":
        cmd_credit()
    elif cmd == "voices":
        cmd_voices(rest[0] if rest else None)
    elif cmd == "list":
        cmd_list()
    elif cmd == "setup-refs" and rest:
        cmd_setup_refs(rest[0], dry_run=dry)
    elif cmd == "produce" and len(rest) >= 2:
        cmd_produce(rest[0], rest[1], dry_run=dry)
    elif cmd == "cost-report" and rest:
        cmd_cost_report(rest[0])
    else:
        console.print(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
