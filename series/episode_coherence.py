"""
Bu modul bolum duzeyinde oz-incelemeyi (self-review) saglar: motor kendi
bitirdigi bolumu inceler.
"""

import math


def _is_usable_number(value):
    """Deger gecerli bir sayi mi? int/float, bool degil, sonsuz/NaN degil."""
    return (isinstance(value, (int, float))
            and not isinstance(value, bool)
            and math.isfinite(value))


def episode_coherence_report(shot_numbers, dropped_shots, *,
                             narration_expected, narration_ok,
                             duration_s, duration_band):
    """
    Bolum tutarliligi raporunu uretir.

    Parametreler:
      shot_numbers: Planlanan tum shot numaralari, sirali liste.
      dropped_shots: Dusen shot numaralari (iterable), bos veya None olabilir.
      narration_expected: Sesli anlatim bekleniyorsa True.
      narration_ok: Sesli anlatim gerceklestiyse True.
      duration_s: Olculen bolum suresi (saniye), None olabilir.
      duration_band: (alt, ust) araligi tuple/list, None olabilir.

    Donus: tam olarak altı anahtari olan sozluk.
    """
    # dropped_shots'i bir kere materyalize et, filtrele ve deduplicate et
    dropped = list(dropped_shots) if dropped_shots is not None else []
    dropped = [d for d in dropped if isinstance(d, int) and not isinstance(d, bool)]
    dropped = sorted(set(dropped))

    # loop_closed: son shot numarasi dropped icinde degilse True
    loop_closed = False
    if shot_numbers:
        try:
            last_shot = shot_numbers[-1]
            dropped_set = set(dropped)
            loop_closed = last_shot not in dropped_set
        except Exception:
            loop_closed = False

    # narration_delivered
    if narration_expected:
        narration_delivered = bool(narration_ok)
    else:
        narration_delivered = None

    # arc_roles_missing: her dusen shot icin rol adi, shot numarasina gore sirali
    arc_roles_missing = []
    if shot_numbers and dropped:
        try:
            dropped_in_plan = [d for d in dropped if d in shot_numbers]
            for d in dropped_in_plan:
                idx = shot_numbers.index(d)
                if len(shot_numbers) == 1:
                    role = "loop_seam"
                elif idx == 0:
                    role = "cold_open"
                elif idx == len(shot_numbers) - 1:
                    role = "loop_seam"
                else:
                    role = "episode_body"
                arc_roles_missing.append(role)
        except Exception:
            arc_roles_missing = []

    # duration_s: usable number ise yuvarla, degilse 0.0 (olcumlenmemis)
    duration_usable = _is_usable_number(duration_s)
    if duration_usable:
        duration_val = round(float(duration_s), 2)
    else:
        duration_val = 0.0

    # duration_in_band
    duration_in_band = None
    if duration_band is not None:
        try:
            if (isinstance(duration_band, (list, tuple)) and
                    len(duration_band) == 2):
                low, high = duration_band[0], duration_band[1]
                low_ok = _is_usable_number(low)
                high_ok = _is_usable_number(high)
                if low_ok and high_ok and low <= high:
                    if duration_usable:
                        duration_in_band = low <= duration_val <= high
                    else:
                        duration_in_band = None
        except Exception:
            duration_in_band = None

    # degraded: herhangi bir kotu durum True ise True, None degerler sayilmaz
    # olcumlenmemis sure (duration_usable False) degraded yapmaz
    degraded = False
    if loop_closed is False:
        degraded = True
    if arc_roles_missing:
        degraded = True
    if narration_delivered is False:
        degraded = True
    if duration_in_band is False:
        degraded = True

    return {
        "loop_closed": loop_closed,
        "narration_delivered": narration_delivered,
        "arc_roles_missing": arc_roles_missing,
        "duration_s": duration_val,
        "duration_in_band": duration_in_band,
        "degraded": degraded,
    }