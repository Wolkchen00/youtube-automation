"""Gemini ODEME arizasini (402 / on odemeli kredi bitti) gecici hatalardan ayirir.

2026-09-26..28: AI Studio on odemeli bakiyesi sifirlandi. Bakiye sifira inince
o fatura hesabina bagli TUM anahtarlar ayni anda 402 doner (GEMINI_API_KEY ve
GEMINI_API_KEY_QC ikisi de). Kod bu hatayi "RESOURCE_EXHAUSTED" gordugu icin
429 kotasi sandi: 30 sn araliklarla yeniden denedi, yedek modeli denedi (ayni
hesap, ayni 402), bolumu "altyapi yeniden denemesi" sayip 48 saatte needs_human
yapti ve uc kanal uc gun boyunca her gun Kie'ye klip odeyip cope atti
(yaklasik 1.100 kredi). Beklemek bu hatayi ACMAZ; yalniz insan kredi yukleyince
acilir. Bu yuzden ayri bir sinif.

DIKKAT: 429 govdesi de "check your plan and billing details" diyebilir. Bu
yuzden duz "BILLING" kelimesi isaret DEGILDIR; yalniz 402 kodu ve on odeme
metni sayilir.
"""

from __future__ import annotations

import re

AI_STUDIO_URL = "https://aistudio.google.com"

_BILLING_MARKERS = (
    "PREPAYMENT",
    "CREDITS ARE DEPLETED",
    "PAYMENT_REQUIRED",
    "PAYMENT REQUIRED",
)

COZUM_METNI = (
    "Cozum: " + AI_STUDIO_URL + " > Billing > Buy credits. Ayni sayfada "
    "'Setup auto-reload' acilirsa bakiye bir daha sifirlanmaz. Kredi gelince "
    "seriler bir sonraki kosuda kendiliginden devam eder; elle bir sey "
    "sifirlamak gerekmez."
)


def is_billing_error(error: BaseException) -> bool:
    """Hata, beklemeyle gecmeyen Gemini odeme arizasi mi (402 / on odeme bitti)?"""
    if getattr(error, "code", None) == 402 or getattr(error, "status_code", None) == 402:
        return True
    message = str(error).upper()
    if re.match(r"\s*402\b", message):
        return True
    return any(marker in message for marker in _BILLING_MARKERS)
