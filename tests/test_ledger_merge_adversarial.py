"""ROCK 1a düşman testleri (Visionary incelemesi, Codex'in setinden BAĞIMSIZ).

Codex'in tests/test_ledger_merge.py dosyası sözleşmedeki (a)-(g) vakalarını kapsıyor.
Bu dosya onun KAPSAMADIĞI kenar durumlarını kovalar: silinmiş anahtarın dirilmesi,
yön bağımsızlığı, idempotentlik, NaN/Infinity, sayı gibi görünen string, ve en
önemlisi GERÇEK canlı defter şekliyle uçtan uca bir yarış senaryosu.
"""
import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
MERGER_PATH = REPO_ROOT / "scripts" / "merge_credits_ledger.py"
LIVE_LEDGER_PATH = REPO_ROOT / "credits_ledger.json"


def run_merge(base, ours, theirs):
    """Gerçek CLI'ı gerçek git çakışma aşamalarıyla çalıştır; (rc, doc) döndür."""
    with tempfile.TemporaryDirectory() as temp:
        repo = pathlib.Path(temp)
        subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
        hashes = []
        for doc in (base, ours, theirs):
            content = (json.dumps(doc, ensure_ascii=False) + "\n").encode("utf-8")
            r = subprocess.run(
                ["git", "-C", str(repo), "hash-object", "-w", "--stdin"],
                input=content, capture_output=True, check=True,
            )
            hashes.append(r.stdout.decode().strip())
        index = "".join(
            f"100644 {h} {stage}\tcredits_ledger.json\n"
            for stage, h in enumerate(hashes, start=1)
        )
        subprocess.run(
            ["git", "-C", str(repo), "update-index", "--index-info"],
            input=index.encode(), capture_output=True, check=True,
        )
        target = repo / "credits_ledger.json"
        target.write_text(json.dumps(ours, ensure_ascii=False), encoding="utf-8")
        # DİKKAT: merger `git show :N:<yol>` kullanır; yol REPO-GÖRELİ olmalı,
        # mutlak yol verilirse aşamalar okunamaz ve doğru şekilde fail-closed olur.
        proc = subprocess.run(
            [sys.executable, str(MERGER_PATH), "credits_ledger.json"],
            cwd=str(repo), capture_output=True, text=True, encoding="utf-8",
        )
        doc = None
        if proc.returncode == 0:
            doc = json.loads(target.read_text(encoding="utf-8"))
        return proc.returncode, doc, (proc.stderr or "")


def led(entries=None, spend=None, **extra):
    d = {"entries": entries if entries is not None else []}
    if spend is not None:
        d["episode_spend"] = spend
    d.update(extra)
    return d


class Adversarial(unittest.TestCase):

    # --- 1. Silinmiş anahtarın dirilmesi -------------------------------------
    def test_unknown_key_deleted_on_BOTH_sides_is_resurrected(self):
        """Bilinen davranış farkı: iki taraf da sildiyse anahtar geri geliyor.

        Doğru 3-yollu birleştirme onu SİLERDİ. Kod `base[key]`e düşüyor.
        Veri kaybetmeyen (muhafazakâr) yön olduğu için kabul edilebilir, ama
        DAVRANIŞ KAYIT ALTINA ALINMALI ki sessiz bir sürpriz olmasın.
        """
        rc, doc, _ = run_merge(led(spend={}, legacy_flag=True), led(spend={}), led(spend={}))
        self.assertEqual(rc, 0)
        self.assertIn("legacy_flag", doc,
                      "davranış değişti: artık siliniyor - dokümante et")

    def test_episode_spend_deleted_on_both_sides_still_emitted(self):
        rc, doc, _ = run_merge(led(spend={"a:1": 10.0}), led(), led())
        self.assertEqual(rc, 0)
        # base'de vardı -> çıktıda episode_spend bloğu bulunmalı, kaybolmamalı
        self.assertIn("episode_spend", doc)
        self.assertEqual(doc["episode_spend"].get("a:1"), 10.0)

    # --- 2. Yön bağımsızlığı ve idempotentlik --------------------------------
    def test_direction_independence(self):
        base = led([{"ts": "1"}], {"s:1": 100.0})
        ours = led([{"ts": "1"}, {"ts": "3"}], {"s:1": 180.0, "s:2": 5.0})
        theirs = led([{"ts": "1"}, {"ts": "2"}], {"s:1": 140.0, "s:3": 7.0})
        rc1, d1, _ = run_merge(base, ours, theirs)
        rc2, d2, _ = run_merge(base, theirs, ours)
        self.assertEqual((rc1, rc2), (0, 0))
        self.assertEqual(d1["episode_spend"], d2["episode_spend"])
        self.assertEqual(
            sorted(json.dumps(e, sort_keys=True) for e in d1["entries"]),
            sorted(json.dumps(e, sort_keys=True) for e in d2["entries"]),
        )

    def test_idempotent_second_merge_is_a_fixed_point(self):
        base = led([{"ts": "1"}], {"s:1": 100.0})
        ours = led([{"ts": "1"}, {"ts": "2"}], {"s:1": 160.0})
        theirs = led([{"ts": "1"}, {"ts": "3"}], {"s:1": 130.0})
        rc, once, _ = run_merge(base, ours, theirs)
        self.assertEqual(rc, 0)
        rc2, twice, _ = run_merge(once, once, once)
        self.assertEqual(rc2, 0)
        self.assertEqual(once, twice, "birleştirme sabit nokta değil")

    # --- 3. Sayısal kenar durumlar -------------------------------------------
    def test_numeric_looking_string_is_rejected(self):
        rc, _, err = run_merge(led(spend={}), led(spend={"s:1": "500"}), led(spend={}))
        self.assertEqual(rc, 1, "sayı gibi görünen string kabul edildi")
        self.assertIn("episode_spend", err)

    def test_infinity_and_nan_are_rejected(self):
        for bad in (float("inf"), float("nan")):
            with self.subTest(value=bad):
                rc, _, _ = run_merge(led(spend={}), led(spend={"s:1": bad}), led(spend={}))
                self.assertEqual(rc, 1, f"{bad} kabul edildi")

    def test_floor_protects_when_base_exceeds_both_sides(self):
        """base iki taraftan da büyükse delta negatif olur; taban korumalı."""
        rc, doc, _ = run_merge(
            led(spend={"s:1": 900.0}), led(spend={"s:1": 400.0}), led(spend={"s:1": 500.0}))
        self.assertEqual(rc, 0)
        self.assertGreaterEqual(doc["episode_spend"]["s:1"], 500.0,
                                "eksik sayım: kredi tavanı zayıflar")

    def test_no_undercount_property_over_many_shapes(self):
        """Sözleşmenin ASIL güvenlik değişmezi: sonuç asla max(ours,theirs)'in altına düşmez."""
        cases = [
            (0, 0, 0), (0, 84, 0), (0, 0, 84), (436, 512, 436), (436, 512, 600),
            (436, 436, 436), (800, 100, 100), (100, 100.5, 100.25), (0, 1e9, 1),
        ]
        for b, o, t in cases:
            with self.subTest(base=b, ours=o, theirs=t):
                rc, doc, _ = run_merge(
                    led(spend={"k": float(b)}), led(spend={"k": float(o)}),
                    led(spend={"k": float(t)}))
                self.assertEqual(rc, 0)
                self.assertGreaterEqual(doc["episode_spend"]["k"], max(o, t))

    # --- 4. Şema saldırıları --------------------------------------------------
    def test_missing_entries_key_fails_closed(self):
        rc, _, _ = run_merge(led(), {"episode_spend": {}}, led())
        self.assertEqual(rc, 1)

    def test_episode_spend_wrong_type_fails_closed(self):
        rc, _, _ = run_merge(led(spend={}), {"entries": [], "episode_spend": []}, led(spend={}))
        self.assertEqual(rc, 1)

    def test_unicode_keys_survive(self):
        rc, doc, _ = run_merge(
            led(spend={}), led(spend={"şüpheli-seri:1": 5.0}), led(spend={"日本語:2": 7.0}))
        self.assertEqual(rc, 0)
        self.assertEqual(doc["episode_spend"]["şüpheli-seri:1"], 5.0)
        self.assertEqual(doc["episode_spend"]["日本語:2"], 7.0)

    # --- 5. GERÇEK canlı defterle uçtan uca yarış ----------------------------
    def test_real_live_ledger_as_base_two_concurrent_lines(self):
        """1 Eylül'ün gerçek senaryosu: canlı defter base, iki hat aynı anda harcıyor."""
        live = json.loads(LIVE_LEDGER_PATH.read_text(encoding="utf-8"))
        self.assertIn("episode_spend", live, "canlı defter şekli değişmiş")
        # Sentetik bolum numarasi CANLI defterden TURETILIR. Sabit 27 yazilmisti ve
        # 2026-09-02'de part 27 gercekten uretilince (848 kredi) bu test kirildi:
        # birlestirme 84 + 848 topladi. Test uretimle yarisamaz; carpismayan bir
        # numara sectigimizde konusu (iki hattin harcamasi + gecmis bozulmasin)
        # aynen korunur.
        used = [
            int(key.split(":")[1])
            for key in live["episode_spend"]
            if key.startswith("unnatural-lab:") and key.split(":")[1].isdigit()
        ]
        fresh_part = max(used, default=0) + 100
        fresh_key = f"unnatural-lab:{fresh_part}"
        self.assertNotIn(fresh_key, live["episode_spend"])
        ours = json.loads(json.dumps(live))
        theirs = json.loads(json.dumps(live))
        ours["entries"] = live["entries"] + [
            {"month": "2026-09", "series": "unnatural-lab", "part": fresh_part,
             "reserved": 800, "actual": 84.0, "ts": "2026-09-01T21:00:00Z"}]
        ours["episode_spend"][fresh_key] = 84.0
        theirs["entries"] = live["entries"] + [
            {"month": "2026-09", "series": "flashpoints", "part": 22,
             "reserved": 900, "actual": 105.0, "ts": "2026-09-01T21:05:00Z"}]
        theirs["episode_spend"]["flashpoints:22"] = 105.0
        rc, doc, _ = run_merge(live, ours, theirs)
        self.assertEqual(rc, 0)
        # iki hattın harcaması da hayatta
        self.assertEqual(doc["episode_spend"][fresh_key], 84.0)
        self.assertEqual(doc["episode_spend"]["flashpoints:22"], 105.0)
        # ve GEÇMİŞ hiç bozulmadı - asıl veri kaybı korkusu buydu
        for k, v in live["episode_spend"].items():
            self.assertEqual(doc["episode_spend"][k], v, f"geçmiş harcama bozuldu: {k}")
        self.assertEqual(len(doc["entries"]), len(live["entries"]) + 2)


if __name__ == "__main__":
    unittest.main()
