
import json, pathlib, sys, tempfile
from unittest import mock
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from series import series_runner
from series.produce import ProduceResult
from series.series_meta import SeriesMeta

def test_probe():
    meta = SeriesMeta({"slug":"probe","base_title":"p","total_parts":3,
                       "next_part":1,"status":"active","publish_mode":"auto",
                       "upload_profile":"p","platforms":["youtube"],"parts":{}})
    with tempfile.TemporaryDirectory() as tmp:
        hedef = pathlib.Path(tmp)
        with mock.patch("series.bible.data_dir", return_value=hedef):
            for kod in ("AUDIO_MASTER","EPISODE_DEGRADED"):
                series_runner._append_hold_log(meta, 7, "qc_retry",
                    ProduceResult("qc_hold", reason="x", reason_code=kod))
        f = hedef / "hold_log.jsonl"
        print("VAR MI:", f.exists())
        if f.exists():
            print("SATIRLAR:", repr(f.read_text(encoding="utf-8")))
        else:
            print("DIZIN:", list(hedef.iterdir()))
    assert False, "ciktiyi gor"
