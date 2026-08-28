"""Parmak izi, URETIMIN KENDI yazdigi alanlardan etkilenmemeli.

2026-08-28, part22'nin CANLI yayininda olculdu: kosu bible'a
`kitchen_counter.ref_image_url` yazdi ve parmak izi ba617381 -> 6c18a9c5 kaydi.
Ucucu alan listesi `ref_url` diyordu, ama produce.py'nin gercekte yazdigi anahtar
`ref_image_url`. Duzeltilmeseydi part23 `bathroom_sink` referansini yazacak, pencere
iki farkli stack gorecek ve kill-gate SONSUZA DEK `karar_yok` verecekti - yani
olcum sessizce olurdu.

Bu paket iki isi yapar: (1) bilinen alanlarin davranisini sabitler,
(2) SINIFI yakalar - bible'a yeni bir uretim alani eklenirse test duser.
"""

import json
import pathlib
import re
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from core import stack_fingerprint as sf

SLUG = "unnatural-lab"

# Uretilmis GORUNEN her anahtar burada SINIFLANDIRILMIS olmali.
# Yeni bir anahtar eklenirse test duser ve birinin karar vermesi gerekir.
DELIBERATELY_HASHED = {
    "id",             # yapisal kimlik (ortam/karakter secimi ciktiyi belirler)
    "style_ref_url",  # operator stil karari; uretim yazmaz
    "audio_id",       # operator ses secimi (ornegin "algieba")
}
GENERATED_SHAPE = re.compile(r"(_url|_id|_local)$|^registered$")


def _all_keys(node):
    if isinstance(node, dict):
        for key, value in node.items():
            yield key
            yield from _all_keys(value)
    elif isinstance(node, list):
        for item in node:
            yield from _all_keys(item)


class VolatileFieldTests(unittest.TestCase):
    def setUp(self):
        self.path = sf.data_dir(SLUG) / "bible.json"
        self.raw = self.path.read_text(encoding="utf-8")
        self.addCleanup(lambda: self.path.write_text(self.raw, encoding="utf-8"))
        self.base = sf.fingerprint(SLUG)

    def _write(self, mutate):
        data = json.loads(self.raw)
        mutate(data)
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2),
                             encoding="utf-8")
        return sf.fingerprint(SLUG)

    def test_ortam_referansi_yazmak_izi_DEGISTIRMEZ(self):
        """Asil hata: canli yayinda olculdu."""
        def mutate(d):
            for env in d["environments"]:
                env["ref_image_url"] = f"https://i.ibb.co/x/{env['id']}.png"
        self.assertEqual(self._write(mutate), self.base)

    def test_karakter_referansi_ve_kayit_kimligi_izi_DEGISTIRMEZ(self):
        def mutate(d):
            for ch in d["characters"]:
                ch["ref_image_url"] = "https://i.ibb.co/x/yeni.jpg"
                ch["character_id"] = "yeni-kayit-kimligi"
                ch["voice"]["kie_audio_id"] = "uretilmis-ses-123"
        self.assertEqual(self._write(mutate), self.base)

    def test_yerel_dosya_yolu_izi_DEGISTIRMEZ(self):
        def mutate(d):
            d["environments"][0]["ref_image_local"] = "/tmp/baska/yol.png"
        self.assertEqual(self._write(mutate), self.base)

    def test_operator_ses_secimi_izi_DEGISTIRIR(self):
        """voice.audio_id bir GIRDIDIR; degisirse anlatim sesi degisir."""
        def mutate(d):
            d["characters"][0]["voice"]["audio_id"] = "baska-ses"
        self.assertNotEqual(self._write(mutate), self.base)

    def test_stil_referansi_izi_DEGISTIRIR(self):
        def mutate(d):
            d["style_ref_url"] = "https://example.com/yeni-stil.png"
        self.assertNotEqual(self._write(mutate), self.base)

    def test_ortam_TARIFI_izi_DEGISTIRIR(self):
        """Referans URL'si degil, ODANIN TARIFI ciktiyi sekillendirir."""
        def mutate(d):
            d["environments"][0]["desc"] = "Bambaska bir oda."
        self.assertNotEqual(self._write(mutate), self.base)

    def test_uretim_alani_suruklenme_bekcisi(self):
        """Bible'a yeni bir uretilmis alan eklenirse BIRI karar vermeli.

        Bu test, 2026-08-28'de kacirdigimiz SINIFI yakalar: listeyi ezberden
        yazmak yerine canli bible'i tarar.
        """
        bible = json.loads(self.raw)
        siniflandirilmamis = sorted({
            key for key in _all_keys(bible)
            if GENERATED_SHAPE.search(key)
            and key not in sf._BIBLE_VOLATILE_KEYS
            and key not in DELIBERATELY_HASHED
        })
        self.assertEqual(
            siniflandirilmamis, [],
            "bible'da siniflandirilmamis uretim-gorunumlu alan var: "
            f"{siniflandirilmamis}. Ya _BIBLE_VOLATILE_KEYS'e ekle (uretim yaziyorsa) "
            "ya da DELIBERATELY_HASHED'e ekle (operator girdisiyse).",
        )

    def test_surum_yukselmesi_izi_DEGISTIRIR(self):
        """sf1 ve sf2 sessizce esit gorunmemeli."""
        import unittest.mock as mock
        with mock.patch.object(sf, "STACK_VERSION", "sf1"):
            eski = sf.fingerprint(SLUG)
        self.assertNotEqual(eski, self.base)


if __name__ == "__main__":
    unittest.main()
