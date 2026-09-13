# -*- coding: utf-8 -*-
"""Daktilo kunye modu + alcak-gecirenli muzik yatagi sozlesme testleri.

Dayanak: shadowedhistory/REELYZE-RAPOR.md , "@one__create referans analizi".
Olculen referansta kunye harf harf yaziliyor (TO > TOKYO 22 > TOKYO 2247,
~0,5 sn), sol ust kosede, siyah, kutusuz; ses ~2 kHz'de tavanlaniyor.

Bu dosyanin ASIL isi GERILEME KORUMASI: yeni alanlarin hepsi opt-in ve
varsayilanlari eski davranisi BIREBIR korumak zorunda, cunku ayni fonksiyonu
next-stop ve diger canli seritler de kullaniyor.
"""

import pathlib
import shutil
import subprocess
import sys
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core import ffmpeg_tools                       # noqa: E402
from series.bible import Bible                      # noqa: E402
from series.replenish import validate_title_card    # noqa: E402


FFMPEG = bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))


def _luma(video: pathlib.Path, t: float, crop: str) -> float:
    """Verilen anda, verilen kirpma kutusundaki ortalama parlaklik (YAVG)."""
    out = subprocess.run(
        ["ffmpeg", "-ss", f"{t}", "-i", str(video), "-frames:v", "1",
         "-vf", f"crop={crop},format=gray,signalstats,metadata=print:file=-",
         "-f", "null", "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    for line in (out.stdout or "").splitlines():
        if "YAVG" in line:
            return float(line.split("=")[-1])
    raise AssertionError("YAVG okunamadi")


def _band_db(video: pathlib.Path, lo: int, hi: int) -> float:
    """Bir frekans bandindaki ortalama seviye (dB). Iki asamali suzgec = 24 dB/oktav."""
    out = subprocess.run(
        ["ffmpeg", "-i", str(video), "-af",
         f"highpass=f={lo}:poles=2,highpass=f={lo}:poles=2,"
         f"lowpass=f={hi}:poles=2,lowpass=f={hi}:poles=2,volumedetect",
         "-f", "null", "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    for line in (out.stderr or "").splitlines():
        if "mean_volume" in line:
            return float(line.split("mean_volume:")[1].replace("dB", "").strip())
    raise AssertionError("mean_volume okunamadi")


def _make_bible(data) -> Bible:
    b = Bible.__new__(Bible)
    b.data = data
    return b


class TitleCardSemaTests(unittest.TestCase):
    """validate_title_card: subtitle_required ve genisletilmis yil araligi."""

    def test_alt_yazi_VARSAYILAN_olarak_hala_zorunlu(self):
        # GERILEME KORUMASI: alan yazilmadiginda eski davranis aynen surer.
        bible = _make_bible({"series": {"slug": "t", "title_card": {"enabled": True}}})
        errors = validate_title_card(
            bible, {"title_card": {"title": "ISTANBUL 2512", "subtitle": ""}}
        )
        self.assertTrue(errors)
        self.assertIn("subtitle", errors[0])

    def test_subtitle_required_false_iken_tek_satir_gecer(self):
        bible = _make_bible({"series": {"slug": "t", "title_card": {
            "enabled": True, "subtitle_required": False}}})
        errors = validate_title_card(
            bible, {"title_card": {"title": "ISTANBUL 2512", "subtitle": ""}}
        )
        self.assertEqual(errors, [])

    def test_subtitle_required_false_BASLIGI_hala_zorunlu_kilar(self):
        bible = _make_bible({"series": {"slug": "t", "title_card": {
            "enabled": True, "subtitle_required": False}}})
        errors = validate_title_card(
            bible, {"title_card": {"title": "", "subtitle": ""}}
        )
        self.assertTrue(errors)

    def test_2512_kabul_ediliyor(self):
        # Eski regex 20[0-9]{2} ile sinirliydi; 2512 kunyeden GECEMIYORDU.
        bible = _make_bible({"series": {"slug": "t", "title_card": {
            "enabled": True, "subtitle_required": False}}})
        self.assertEqual(
            validate_title_card(bible, {"title_card": {
                "title": "ISTANBUL 2512", "subtitle": ""}}),
            [],
        )

    def test_eski_yillar_BOZULMADI(self):
        bible = _make_bible({"series": {"slug": "t", "title_card": {"enabled": True}}})
        for title, sub in [("Barcelona", "1909"), ("Halifax", "1917"), ("Mars", "2026")]:
            with self.subTest(year=sub):
                self.assertEqual(
                    validate_title_card(bible, {"title_card": {
                        "title": title, "subtitle": sub}}),
                    [],
                )

    def test_yilsiz_kunye_HALA_REDDEDILIR(self):
        bible = _make_bible({"series": {"slug": "t", "title_card": {
            "enabled": True, "subtitle_required": False}}})
        errors = validate_title_card(
            bible, {"title_card": {"title": "ISTANBUL", "subtitle": ""}}
        )
        self.assertTrue(errors)


class MusicLowpassBibleTests(unittest.TestCase):
    def test_alan_yoksa_None(self):
        self.assertIsNone(_make_bible({"series": {"slug": "t"}}).music_lowpass_hz)

    def test_sifir_ve_negatif_None_sayilir(self):
        for value in (0, -1):
            with self.subTest(value=value):
                self.assertIsNone(
                    _make_bible({"series": {"slug": "t",
                                            "music_lowpass_hz": value}}).music_lowpass_hz)

    def test_sayi_olmayan_deger_ValueError(self):
        with self.assertRaises(ValueError):
            _ = _make_bible({"series": {"slug": "t",
                                        "music_lowpass_hz": "cok"}}).music_lowpass_hz

    def test_gecerli_deger_float_doner(self):
        self.assertEqual(
            _make_bible({"series": {"slug": "t",
                                    "music_lowpass_hz": 2000}}).music_lowpass_hz,
            2000.0,
        )


@unittest.skipUnless(FFMPEG, "ffmpeg/ffprobe gerekiyor")
class TitleCardRenderTests(unittest.TestCase):
    """Gercek render: daktilo fiilen harf harf yaziyor mu."""

    @classmethod
    def setUpClass(cls):
        import tempfile
        cls.tmp = pathlib.Path(tempfile.mkdtemp(prefix="kunye_"))
        cls.src = cls.tmp / "src.mp4"
        subprocess.run(
            ["ffmpeg", "-y", "-v", "error",
             "-f", "lavfi", "-i", "color=c=#cfe2f3:s=1080x1920:d=6:r=24",
             "-f", "lavfi", "-i", "sine=f=100:d=6",
             "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest",
             str(cls.src)],
            check=True, capture_output=True,
        )
        # Kunye seridi: ustten %16-24, tam genislik.
        cls.crop = "iw:ih*0.08:0:ih*0.16"

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_daktilo_harf_harf_yaziyor(self):
        out = self.tmp / "type.mp4"
        ffmpeg_tools.title_card_overlay(
            self.src, out, title="ISTANBUL 2512", subtitle="", duration=4.0,
            typewriter=0.5, align="left", margin_pct=6, color="black", box=False,
        )
        # Siyah yazi acik zeminde: harf arttikca ortalama parlaklik DUSER.
        erken = _luma(out, 0.05, self.crop)
        orta = _luma(out, 0.30, self.crop)
        tam = _luma(out, 0.60, self.crop)
        self.assertLess(orta, erken, "0,3 sn'de yazi 0,05 sn'dekinden uzun olmali")
        self.assertLess(tam, orta, "0,6 sn'de yazi tamamlanmis olmali")

    def test_daktilo_bittikten_sonra_SABIT_kalir(self):
        out = self.tmp / "hold.mp4"
        ffmpeg_tools.title_card_overlay(
            self.src, out, title="ISTANBUL 2512", subtitle="", duration=4.0,
            typewriter=0.5, align="left", margin_pct=6, color="black", box=False,
        )
        self.assertAlmostEqual(_luma(out, 1.0, self.crop),
                               _luma(out, 3.0, self.crop), delta=1.0)

    def test_sure_sonunda_SOLUYOR(self):
        out = self.tmp / "fade.mp4"
        ffmpeg_tools.title_card_overlay(
            self.src, out, title="ISTANBUL 2512", subtitle="", duration=4.0,
            typewriter=0.5, align="left", margin_pct=6, color="black", box=False,
        )
        # 4,0 sn'de kunye tamamen gitmis olmali: serit bos zemin kadar acik.
        self.assertGreater(_luma(out, 4.2, self.crop),
                           _luma(out, 3.0, self.crop) + 2.0)

    def test_sol_hizalama_yaziyi_SOLA_koyar(self):
        sol = self.tmp / "sol.mp4"
        orta = self.tmp / "orta.mp4"
        for path, align in ((sol, "left"), (orta, "center")):
            ffmpeg_tools.title_card_overlay(
                self.src, path, title="ISTANBUL 2512", subtitle="", duration=3.0,
                align=align, color="black", box=False,
            )
        # Sol ucteki dilim: sola yaslanmis yazida koyulasir, ortalida bos kalir.
        kutu = "iw*0.25:ih*0.08:0:ih*0.16"
        self.assertLess(_luma(sol, 1.0, kutu), _luma(orta, 1.0, kutu) - 2.0)

    def test_VARSAYILANLAR_eski_davranisi_korur(self):
        """GERILEME KAPISI: yeni alanlar verilmeden uretilen video, yalniz eski
        parametrelerle uretilenle BIREBIR ayni olmali."""
        a = self.tmp / "a.mp4"
        b = self.tmp / "b.mp4"
        ffmpeg_tools.title_card_overlay(
            self.src, a, title="ISTANBUL", subtitle="2512", duration=3.0)
        ffmpeg_tools.title_card_overlay(
            self.src, b, title="ISTANBUL", subtitle="2512", duration=3.0,
            typewriter=0.0, align="center", margin_pct=6, color="white", box=True)
        self.assertEqual(a.read_bytes(), b.read_bytes())

    def test_bos_baslik_required_degilken_orijinali_gecirir(self):
        out = self.tmp / "bos.mp4"
        ffmpeg_tools.title_card_overlay(
            self.src, out, title="", subtitle="", duration=3.0, typewriter=0.5)
        self.assertEqual(out.read_bytes(), self.src.read_bytes())

    def test_turkce_karakterler_ve_kesme_isareti_cokmez(self):
        out = self.tmp / "tr.mp4"
        ffmpeg_tools.title_card_overlay(
            self.src, out, title="İSTANBUL'UN ÇAĞI 2512", subtitle="", duration=3.0,
            typewriter=0.5, align="left", color="black", box=False)
        self.assertTrue(out.exists() and out.stat().st_size > 0)


@unittest.skipUnless(FFMPEG, "ffmpeg/ffprobe gerekiyor")
class MusicLowpassRenderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import tempfile
        cls.tmp = pathlib.Path(tempfile.mkdtemp(prefix="lowpass_"))
        cls.src = cls.tmp / "src.mp4"
        cls.music = cls.tmp / "m.mp3"
        subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-f", "lavfi",
             "-i", "color=c=black:s=540x960:d=5:r=24",
             "-f", "lavfi", "-i", "sine=f=100:d=5",
             "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest",
             str(cls.src)], check=True, capture_output=True)
        subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-f", "lavfi",
             "-i", "anoisesrc=d=5:c=white:a=0.5", "-c:a", "libmp3lame", str(cls.music)],
            check=True, capture_output=True)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_lowpass_tizi_kesiyor(self):
        acik = self.tmp / "on.mp4"
        kapali = self.tmp / "off.mp4"
        ffmpeg_tools.mix_background_music(
            self.src, self.music, kapali, music_volume=0.9, replace_original=True)
        ffmpeg_tools.mix_background_music(
            self.src, self.music, acik, music_volume=0.9, replace_original=True,
            lowpass_hz=2000)
        # 8 kHz ustu pratikte kaybolmali (olculdu: ~51 dB dususu).
        self.assertLess(_band_db(acik, 8000, 16000),
                        _band_db(kapali, 8000, 16000) - 30.0)

    def test_lowpass_basi_BOZMUYOR(self):
        acik = self.tmp / "on2.mp4"
        kapali = self.tmp / "off2.mp4"
        ffmpeg_tools.mix_background_music(
            self.src, self.music, kapali, music_volume=0.9, replace_original=True)
        ffmpeg_tools.mix_background_music(
            self.src, self.music, acik, music_volume=0.9, replace_original=True,
            lowpass_hz=2000)
        self.assertAlmostEqual(_band_db(acik, 20, 80),
                               _band_db(kapali, 20, 80), delta=2.0)

    def test_lowpass_VERILMEDIGINDE_ses_birebir_ayni(self):
        """GERILEME KAPISI: alan yokken cikti eski yolla bayt-bayt ayni olmali."""
        a = self.tmp / "a.mp4"
        b = self.tmp / "b.mp4"
        ffmpeg_tools.mix_background_music(
            self.src, self.music, a, music_volume=0.9, replace_original=True)
        ffmpeg_tools.mix_background_music(
            self.src, self.music, b, music_volume=0.9, replace_original=True,
            lowpass_hz=None)
        self.assertEqual(a.read_bytes(), b.read_bytes())


if __name__ == "__main__":
    unittest.main()


class SabitDroneOptInTests(unittest.TestCase):
    """fps / master_lra / music_fade / music_offset_sec bible alanlari.

    Hepsi 13 Eylul 2026'da still-home ep01 OLCULDUKTEN sonra eklendi:
    teslim -13,1 LUFS ve LRA 7,1 cikmisti, referans -14,0 ve LRA 1,0-1,5.
    """

    def test_varsayilanlar_eski_davranis(self):
        b = _make_bible({"series": {"slug": "t"}})
        self.assertIsNone(b.fps)
        self.assertEqual(b.master_lra, 11.0)
        self.assertEqual(b.music_fade, (None, None))
        self.assertIsNone(b.music_offset_sec)

    def test_still_home_degerleri(self):
        b = _make_bible({"series": {"slug": "t", "fps": 24, "master_lra": 1.5,
                                    "music_fade": {"in": 0.05, "out": 0.05},
                                    "music_offset_sec": 12}})
        self.assertEqual(b.fps, 24)
        self.assertEqual(b.master_lra, 1.5)
        self.assertEqual(b.music_fade, (0.05, 0.05))
        self.assertEqual(b.music_offset_sec, 12.0)

    def test_sifir_ve_negatif_degerler(self):
        self.assertIsNone(_make_bible({"series": {"slug": "t", "fps": 0}}).fps)
        self.assertIsNone(
            _make_bible({"series": {"slug": "t", "music_offset_sec": 0}}).music_offset_sec)
        with self.assertRaises(ValueError):
            _ = _make_bible({"series": {"slug": "t", "music_offset_sec": -1}}).music_offset_sec
        with self.assertRaises(ValueError):
            _ = _make_bible({"series": {"slug": "t", "master_lra": 0}}).master_lra

    def test_bozuk_tipler_ValueError(self):
        for alan, deger in [("fps", "yirmidort"), ("master_lra", "az"),
                            ("music_offset_sec", "on"), ("music_fade", [0.1, 0.1])]:
            with self.subTest(alan=alan):
                with self.assertRaises(ValueError):
                    getattr(_make_bible({"series": {"slug": "t", alan: deger}}),
                            {"music_fade": "music_fade"}.get(alan, alan))


@unittest.skipUnless(FFMPEG, "ffmpeg/ffprobe gerekiyor")
class SabitDroneRenderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import tempfile
        cls.tmp = pathlib.Path(tempfile.mkdtemp(prefix="drone_"))
        cls.src = cls.tmp / "src.mp4"
        cls.music = cls.tmp / "m.wav"
        subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-f", "lavfi",
             "-i", "color=c=black:s=540x960:d=6:r=24",
             "-f", "lavfi", "-i", "sine=f=100:d=6",
             "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest",
             str(cls.src)], check=True, capture_output=True)
        # Ilk 4 sn SESSIZ, sonra sabit ton , Suno parcalarinin olculen bicimi.
        subprocess.run(
            ["ffmpeg", "-y", "-v", "error",
             "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo:d=4",
             "-f", "lavfi", "-i", "sine=f=120:d=20:sample_rate=48000",
             "-filter_complex", "[0:a][1:a]concat=n=2:v=0:a=1[a]",
             "-map", "[a]", "-c:a", "pcm_s16le", str(cls.music)],
            check=True, capture_output=True)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_offset_sessiz_girisi_atlar(self):
        """ASIL BULGU: parcanin sessiz girisini kullanmak LRA'yi patlatiyor."""
        bastan = self.tmp / "bastan.mp4"
        kaydirmali = self.tmp / "kaydirmali.mp4"
        ffmpeg_tools.mix_background_music(
            self.src, self.music, bastan, music_volume=0.9, replace_original=True,
            fade_in=0.05, fade_out=0.05)
        ffmpeg_tools.mix_background_music(
            self.src, self.music, kaydirmali, music_volume=0.9, replace_original=True,
            fade_in=0.05, fade_out=0.05, offset_sec=8)

        def lra(path):
            out = subprocess.run(
                ["ffmpeg", "-i", str(path), "-af", "ebur128=framelog=verbose",
                 "-f", "null", "-"],
                capture_output=True, text=True, encoding="utf-8", errors="replace")
            for line in (out.stderr or "").splitlines():
                if "LRA:" in line and "low" not in line and "high" not in line:
                    return float(line.split("LRA:")[1].replace("LU", "").strip())
            raise AssertionError("LRA okunamadi")

        self.assertGreater(lra(bastan) - lra(kaydirmali), 2.0,
                           "sessiz girisi atlamak LRA'yi belirgin dusurmeli")

    def test_offset_verilmeyince_ses_birebir_ayni(self):
        a, b = self.tmp / "a.mp4", self.tmp / "b.mp4"
        ffmpeg_tools.mix_background_music(
            self.src, self.music, a, music_volume=0.9, replace_original=True)
        ffmpeg_tools.mix_background_music(
            self.src, self.music, b, music_volume=0.9, replace_original=True,
            offset_sec=None, fade_in=None, fade_out=None)
        self.assertEqual(a.read_bytes(), b.read_bytes())

    def test_fps_override_uygulanir(self):
        out24 = self.tmp / "f24.mp4"
        ffmpeg_tools.final_export(self.src, out24, fps=24)
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=r_frame_rate", "-of", "csv=p=0", str(out24)],
            capture_output=True, text=True)
        self.assertEqual(r.stdout.strip(), "24/1")

    def test_fps_verilmeyince_varsayilan_30(self):
        out = self.tmp / "fdef.mp4"
        ffmpeg_tools.final_export(self.src, out)
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=r_frame_rate", "-of", "csv=p=0", str(out)],
            capture_output=True, text=True)
        self.assertEqual(r.stdout.strip(), "30/1")
