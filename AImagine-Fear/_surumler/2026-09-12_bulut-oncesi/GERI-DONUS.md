# 2026-09-12 bulut surumu oncesi tam yedek

Bu klasor, bulut gecis surumu uygulanmadan ONCEKI `canon/` ve `routes/`
klasorlerinin birebir kopyasidir.

## Ne degisti

IKI degisiklik var, bu yedek IKISINDEN DE oncesini tutuyor.

### 1) Bulut gecisi

`canon/NEGATIVES.md` icindeki tek satir. Once sehri gizleyen her kapali
gecit yasakti; simdi yasak sureye bagli ve seffaflik sart kosuluyor.

Eski satir:

    NO opaque slide. NO solid floor under the rider. NO enclosed dark tunnel that hides the city. NO glowing line that leaves the slide surface.

Yeni satir:

    NO opaque slide. NO solid floor under the rider. NO enclosed dark tunnel. NO passage that removes the city for longer than two seconds: inside any cloud the slide floor stays transparent and the city glow stays readable through it. NO glowing line that leaves the slide surface.

## Nasil geri donulur

Bu klasordeki `canon/` ve `routes/` klasorlerini proje kokune geri kopyala:

    cd AImagine-Fear
    cp -r _surumler/2026-09-12_bulut-oncesi/canon .
    cp -r _surumler/2026-09-12_bulut-oncesi/routes .
    python build.py --check

`--check` 'Built and validated' derse geri donus tamamdir.

Git de ayni yedegi tutuyor, ama bu klasor komut satiri bilmeden de gerisin
geri kopyalanabilsin diye duruyor.

### 2) Neon sureklilik kurali (ayni gun, sonradan eklendi)

`canon/MASTER-BLOCK.md` -> SLIDE bolumu. Uretilen videoda mor seritler
buluttan sonra sonuyordu. Kanon bunu zaten ima ediyordu ama acikca
yazmiyordu. Eklenen cumle seritlerin ilk kareden son kareye kadar,
bulut ve su dahil, ayni parlaklikta yanik kalmasini sart kosuyor.

Geri donus yontemi ayni: bu klasordeki `canon/` klasorunu koke kopyala.
