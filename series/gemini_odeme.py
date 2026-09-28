"""Gemini ODEME arizasini (402 / on odemeli kredi bitti / harcama tavani) gecici hatalardan ayirir.

2026-09-26..28: AI Studio on odemeli bakiyesi sifirlandi. Bakiye sifira inince
o fatura hesabina bagli TUM anahtarlar ayni anda 402 doner (GEMINI_API_KEY ve
GEMINI_API_KEY_QC ikisi de). Kod bu hatayi "RESOURCE_EXHAUSTED" gordugu icin
429 kotasi sandi: 30 sn araliklarla yeniden denedi, yedek modeli denedi (ayni
hesap, ayni 402), bolumu "altyapi yeniden denemesi" sayip 48 saatte needs_human
yapti ve uc kanal uc gun boyunca her gun Kie'ye klip odeyip cope atti
(yaklasik 1.100 kredi). Beklemek bu hatayi ACMAZ; yalniz insan kredi yukleyince
acilir. Bu yuzden ayri bir sinif.

Ayni sinifin ikinci yuzu AYLIK HARCAMA TAVANIDIR: fatura hesabi ya da proje
tavani dolunca Google 429 doner ("... exceeded its monthly spending cap") ve
servis ayin 1'ine kadar durur. Govde 429 oldugu icin eski kod onu da dakikalik
kota sanardi. Otomatik yukleme acildiktan sonra sirada bekleyen sinir budur.

DIKKAT: 429 govdesi de "check your plan and billing details" diyebilir. Bu
yuzden duz "BILLING" kelimesi isaret DEGILDIR; yalniz 402 kodu, on odeme metni
ve harcama tavani metni sayilir.
"""

from __future__ import annotations

import re

AI_STUDIO_URL = "https://aistudio.google.com"

_PREPAY_MARKERS = (
    "PREPAYMENT",
    "CREDITS ARE DEPLETED",
    "PAYMENT_REQUIRED",
    "PAYMENT REQUIRED",
)
_SPEND_CAP_MARKERS = (
    "SPENDING CAP",
    "SPEND CAP",
)

COZUM_METNI = (
    "Cozum: " + AI_STUDIO_URL + " > Billing. Bakiye bittiyse 'Buy credits' ve "
    "ayni sayfada 'Setup auto-reload' (acilirsa bakiye bir daha sifirlanmaz). "
    "Aylik harcama tavani dolduysa tavani yukselt; yukseltilmezse ayin 1'inde "
    "kendiliginden acilir. Odeme duzelince seriler bir sonraki kosuda "
    "kendiliginden devam eder; elle bir sey sifirlamak gerekmez."
)


def is_spend_cap_error(error: BaseException) -> bool:
    """Aylik harcama tavani doldu mu (fatura hesabi ya da proje tavani)?"""
    message = str(error).upper()
    return any(marker in message for marker in _SPEND_CAP_MARKERS)


def is_billing_error(error: BaseException) -> bool:
    """Hata, beklemeyle gecmeyen Gemini odeme arizasi mi (402 / on odeme / harcama tavani)?"""
    if getattr(error, "code", None) == 402 or getattr(error, "status_code", None) == 402:
        return True
    message = str(error).upper()
    if re.match(r"\s*402\b", message):
        return True
    if any(marker in message for marker in _PREPAY_MARKERS):
        return True
    return is_spend_cap_error(error)


def model_chain(env_name: str, default: tuple[str, ...]) -> tuple[str, ...]:
    """Model sirasi: ortam degiskeni (virgullu liste) varsa o, yoksa varsayilan.

    Google modelleri emekliye ayiriyor ("no longer available to new users");
    sira kod degistirmeden GitHub degiskeniyle guncellenebilsin.
    """
    import os

    raw = os.environ.get(env_name, "")
    chain = tuple(item.strip() for item in raw.split(",") if item.strip())
    return chain or default


def billing_headline(detail: str) -> str:
    """Alarm basligi: hangi odeme siniri doldu."""
    if is_spend_cap_error(RuntimeError(detail)):
        return "Gemini aylık harcama tavanı DOLDU"
    return "Gemini ön ödemeli kredisi BİTTİ (402)"
