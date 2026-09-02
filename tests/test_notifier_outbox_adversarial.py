"""ROCK 2 düşman testleri , Visionary incelemesi.

Codex'in tests/test_notifier_entity_fallback.py dosyası sözleşmedeki (a)-(g)'yi
kapsıyor. Bu dosya onun kapsamadıklarını kovalar:
  - 1 Eylül'ün GERÇEK alarm metniyle canlı hatanın yeniden üretilmesi
  - token/chat id'nin istisna yolunda loga sızmaması (Codex bunu ekledi, sertçe sınanıyor)
  - `approver.py`'nin bağlı olduğu `.get("message_id")` geriye uyumu
  - bozuk/dev outbox dosyasının koşuyu çökertmemesi
  - outbox'ın persist_state.sh'in COMMIT ETTİĞİ yolun içinde olması (yoksa kayıt uçar)
"""
from __future__ import annotations

import json
import logging
import pathlib
from unittest import mock

from series import notifier

REPO = pathlib.Path(__file__).resolve().parents[1]

# 1 Eylul 19:29:15'te Telegram'in REDDETTIGI gercek metin (byte offset 89).
LIVE_ALERT = ("⏸️ *Unnatural Lab* Part 25 zorunlu QC tarafından değerlendirilemedi. "
              "Durum awaiting_approval; otomatik üretim ve yayın durduruldu.")


class _Resp:
    def __init__(self, payload, status=200):
        self._p, self.status_code = payload, status

    def json(self):
        return self._p


# --- 1. CANLI HATANIN yeniden uretimi -------------------------------------

def test_live_alert_text_is_sent_without_parse_mode():
    """Kritik alarm parse_mode TASIMAMALI , canli hatanin tam sebebi buydu."""
    sent = {}

    def fake_post(url, data=None, files=None, timeout=None):
        sent.update(data or {})
        return _Resp({"ok": True, "result": {"message_id": 7}})

    with mock.patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "t", "TELEGRAM_CHAT_ID": "c"}), \
         mock.patch.object(notifier.requests, "post", side_effect=fake_post):
        res = notifier.send_plain_message(LIVE_ALERT)

    assert res.delivered is True
    assert "parse_mode" not in sent, (
        "kritik alarm hala parse_mode gonderiyor , 1 Eylul hatasi geri geldi"
    )
    assert "awaiting_approval" in sent["text"]


def test_markdown_path_would_still_have_failed_proving_the_fix_matters():
    """Karsit kanit: parse_mode ile ayni metin Telegram tarafindan REDDEDILIR."""
    def fake_post(url, data=None, files=None, timeout=None):
        if (data or {}).get("parse_mode"):
            return _Resp({"ok": False, "description":
                          "Bad Request: can't parse entities: Can't find end of the "
                          "entity starting at byte offset 89"})
        return _Resp({"ok": True, "result": {"message_id": 1}})

    with mock.patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "t", "TELEGRAM_CHAT_ID": "c"}), \
         mock.patch.object(notifier.requests, "post", side_effect=fake_post):
        markdown = notifier.send_message(LIVE_ALERT)
        plain = notifier.send_plain_message(LIVE_ALERT)

    assert markdown.delivered is False and "parse entities" in (markdown.error or "")
    assert plain.delivered is True


# --- 2. Token / chat id loga SIZMAMALI ------------------------------------

def test_exception_path_never_leaks_token_or_chat_id(caplog):
    """requests istisnasi istek URL'sini (dolayisiyla TOKEN'i) tasiyabilir."""
    token = "123456:SUPER-GIZLI-BOT-TOKEN"
    chat = "987654321"

    def boom(url, data=None, files=None, timeout=None):
        raise RuntimeError(f"connection failed for {url} chat_id={chat}")

    with mock.patch.dict("os.environ",
                         {"TELEGRAM_BOT_TOKEN": token, "TELEGRAM_CHAT_ID": chat}), \
         mock.patch.object(notifier.requests, "post", side_effect=boom), \
         caplog.at_level(logging.DEBUG):
        res = notifier.send_plain_message("merhaba")

    blob = caplog.text + " " + (res.error or "")
    assert res.delivered is False
    assert token not in blob, "BOT TOKEN loga/hata metnine SIZDI"
    assert chat not in blob, "CHAT ID loga/hata metnine SIZDI"


# --- 3. Geriye uyum: approver.py .get("message_id") kullaniyor -------------

def test_send_result_preserves_legacy_message_id_access():
    with mock.patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "t", "TELEGRAM_CHAT_ID": "c"}), \
         mock.patch.object(notifier.requests, "post",
                           return_value=_Resp({"ok": True, "result": {"message_id": 42}})):
        res = notifier.send_message("kart")
    assert res.get("message_id") == 42, "eski .get('message_id') kullanimi kirildi"
    assert res.message_id == 42
    assert bool(res) is True


def test_failed_send_is_falsy_so_legacy_truth_checks_still_work():
    with mock.patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "t", "TELEGRAM_CHAT_ID": "c"}), \
         mock.patch.object(notifier.requests, "post",
                           return_value=_Resp({"ok": False, "description": "nope"})):
        res = notifier.send_message("kart")
    assert not res, "basarisiz gonderim truthy , eski `if send_message(...)` kontrolleri bozulur"
    assert res.get("message_id") is None


# --- 4. Outbox dayanikliligi ----------------------------------------------

def test_corrupt_outbox_is_never_treated_as_empty(tmp_path):
    """ASIL GUVENLIK OZELLIGI: bozuk outbox "bos" sayilmamali.

    `_read_alert_outbox` varsayilanda toleransli ([] doner) ama GERCEK
    cagiranlarin UCU DE strict=True kullaniyor. Bu test bayraga degil
    OZELLIGE bakiyor: bozuk dosyada
      - bekleyen alarm VAR sayilir (kosu yesil gorunmez)
      - bosaltma basarisiz doner
      - yeni alarm eklemek eski kuyruğu SESSIZCE EZMEZ
    Aksi halde bozuk bir dosya kuyruktaki kritik alarmi yok ederdi.
    """
    bad = tmp_path / "alert_outbox.json"
    bad.write_text("{ bu gecerli json degil", encoding="utf-8")
    with mock.patch.object(notifier, "alert_outbox_path", return_value=bad):
        assert notifier.has_pending_critical_alerts("advers") is True,             "bozuk outbox BOS sayildi , kosu yesil gorunur ve alarm kaybolur"
        assert notifier.drain_critical_alerts("advers") is False
        raised = False
        try:
            notifier.enqueue_critical_alert("advers", "yeni", "hata")
        except ValueError:
            raised = True
        assert raised, "bozuk kuyruk uzerine yazildi , eski alarmlar silinirdi"
    # dosya DOKUNULMADAN durmali ki insan bakabilsin
    assert bad.read_text(encoding="utf-8").startswith("{ bu gecerli")


def test_every_real_caller_uses_strict_mode():
    """Toleransli varsayilan yanlislikla kullanilirsa ozellik sessizce kaybolur."""
    src = (REPO / "series" / "notifier.py").read_text(encoding="utf-8")
    body = src[src.index("def enqueue_critical_alert"):src.index("def send_media_group")]
    calls = [ln for ln in body.splitlines() if "_read_alert_outbox(" in ln]
    assert len(calls) == 3, f"beklenmeyen cagri sayisi: {calls}"
    for ln in calls:
        assert "strict=True" in ln, f"toleransli okuma: {ln.strip()}"


def test_corrupt_outbox_does_not_block_production(tmp_path):
    """Duzeltme turunun kilidi: bozuk/dolu outbox URETIMI DURDURMAMALI.

    Ilk insada `--drain-alerts-only` adimi sys.exit(1) ile tum kosuyu
    durduruyordu; Telegram bir gun duserse kanal hic yayin yapamazdi ve bu
    CORE FOCUS ile ("her gun 1 video") celisiyordu. Alarm teslimi ile video
    uretimi BAGIMSIZ olmali; kosu sonda kirmizi biter, uretim yine calisir.
    """
    src = (REPO / "series" / "series_runner.py").read_text(encoding="utf-8")
    i = src.index("_drain_outboxes(outbox_slugs)")
    tail = src[i:i + 400]
    assert "sys.exit(1)" not in tail.split("if drain_only")[0], (
        "outbox bosaltma hala uretimden ONCE sys.exit(1) yapiyor , kanal durur"
    )
    assert "uretim devam" in tail or "devam edecek" in tail


def test_outbox_is_not_unbounded(tmp_path):
    """Haftalarca teslim edilemeyen alarm dosyayi sinirsiz buyutmemeli.

    Sinir yoksa bu test DAVRANISI kayit altina alir; sinir varsa dogrular.
    """
    path = tmp_path / "alert_outbox.json"
    with mock.patch.object(notifier, "alert_outbox_path", return_value=path):
        for i in range(300):
            notifier.enqueue_critical_alert("advers", f"alarm {i}", f"hata {i}")
        entries = notifier._read_alert_outbox("advers")
    assert len(entries) <= 300
    # en yeni kayit her zaman korunmali (en eskisi dusebilir)
    assert any("alarm 299" in json.dumps(e, ensure_ascii=False) for e in entries), \
        "en YENI alarm outbox'tan dusuruldu"


def test_outbox_write_is_atomic_no_partial_file(tmp_path):
    path = tmp_path / "alert_outbox.json"
    with mock.patch.object(notifier, "alert_outbox_path", return_value=path):
        notifier.enqueue_critical_alert("advers", "ilk", "hata")
        notifier.enqueue_critical_alert("advers", "ikinci", "hata")
    # dosya her zaman gecerli JSON olmali
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, list) and len(data) == 2


# --- 5. Outbox GERCEKTEN commit edilen yolda mi? ---------------------------

def test_outbox_lives_inside_a_path_persist_state_commits():
    """Outbox persist_state.sh'in add ettigi yolun DISINDA kalirsa kayit ucar.

    unnatural-lab.yml persist adimi sentinal_ihsan/ dizinini commit'liyor;
    alert_outbox.json serinin data_dir'inde, yani o dizinin altinda olmali.
    """
    from series.bible import data_dir
    outbox = notifier.alert_outbox_path("unnatural-lab").resolve()
    assert outbox.parent == data_dir("unnatural-lab").resolve()

    wf = (REPO / ".github" / "workflows" / "unnatural-lab.yml").read_text(encoding="utf-8")
    assert "sentinal_ihsan/" in wf, "persist adimi sentinal_ihsan/ dizinini commit etmiyor"
    # ve outbox gercekten o agacin altinda
    assert "sentinal_ihsan" in str(outbox).replace("\\", "/"), \
        f"outbox commit edilen agacin disinda: {outbox}"


def test_drain_step_runs_before_produce_in_the_workflow():
    """Sira baglayici: bosaltma URETIMDEN once olmali."""
    wf = (REPO / ".github" / "workflows" / "unnatural-lab.yml").read_text(encoding="utf-8")
    drain = wf.index("--drain-alerts-only")
    produce = wf.index("series.series_runner --series unnatural-lab 2>&1")
    persist = wf.index("persist_state.sh")
    assert drain < produce < persist, "adim sirasi bozuk , outbox kaydi ucabilir"
