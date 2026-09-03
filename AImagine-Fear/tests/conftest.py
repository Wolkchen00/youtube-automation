"""build.py'yi proje kokunden ithal edilebilir yapar.

Bu olmadan `pytest AImagine-Fear/tests` depo kokunden calistirildiginda
"ModuleNotFoundError: No module named 'build'" veriyor; sadece AImagine-Fear
klasorunun icinden calisiyordu. CI kosusu depo kokunden calisiyor, o yuzden sart.
"""
import sys
from pathlib import Path

PROJE_KOKU = Path(__file__).resolve().parent.parent
if str(PROJE_KOKU) not in sys.path:
    sys.path.insert(0, str(PROJE_KOKU))
