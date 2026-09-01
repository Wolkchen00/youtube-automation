# RF-PLAN: Next Stop v2 ,  hızlı maskeli geçişler + yolcu fiziği (rev. 2, SPM R1 sonrası)

CORE FOCUS: Next Stop bölümlerini referans videoların temposuna ve fiziğine getirmek:
pencere manzarası ~3 saniyede bir TAM-MASKELİ geçişle değişir ve vagondaki yolcular
her darbede savrulup tepki verir ,  mevcut 6x10sn Omni + kare zinciri mimarisi değişmeden.

## Araştırma bulguları (referans analizi, 2026-08-31)

Kaynaklar: @ai.akshu "Next stop: World War II" (30s, ~8 tablo) ve "Next stop! Milky way"
(~31s içerik, ~17 vista). İkisi de Seedance 2.5/Higgsfield; 2 fps kontakt sayfalarıyla
kare kare incelendi. Bizim ep01/ep02 (56.2s) YouTube'dan indirilip aynı yöntemle ölçüldü.

| Metrik | Referans | Bizim ep01/ep02 |
|---|---|---|
| Vista değişim sıklığı | ~2.5-3.5 sn'de bir | ~6-8 sn'de bir |
| Sıradan dünyada geçen süre | 1-3 sn | 8-10 sn |
| Geçiş mekanizması | tam karartma (~0.5s) / patlama-parlaması; kısmi maskeler (yeşillik/duman) sadece doku | tek vista sürekli evrilir, maske yok |
| Vagon içi | MW: kalabalık, yolcular her darbede yalpalıyor/çığlık; WWII: minimal, tek el | boş duvar + tek el |
| Geçiş anı fiziği | her maske bir DARBE ile gelir: vagon sarsılır, kamera silkelenir, yolcular savrulur | sadece çekim başı judder |

Kritik içgörü: referanslardaki "hızlı kesme" kurgu değil ,  klibin İÇİNDE, camı bir
anlığına TAMAMEN kapatan olaylarla yapılan sahne değişimi. 6x10 zincir mimarimiz buna
hazır; eksik olan PROMPT KATMANI.

## Zamanlama sözleşmesi (bütün roklarda geçerli)

- micro_trim 0.45s baş+son: kritik hiçbir olay ham klibin ilk 0.5 ve son 0.6 saniyesine
  yazılmaz. Zincirli çekimlerin açılış darbesi ~1.0 saniyede (trim sonrası ~0.55'te
  görünür); son çekimin "Next stop-" kesilmesi 9.3'ten önce biter.
- Kadans: çekim başına ÜÇ vista, İKİ tam maske, maskeler ~3.0 ve ~6.5 saniyede.
  İstisnalar: çekim 1 (hook; maskeler ~4 ve ~7), çekim 6 (tek maske ~3; 4.5-6.0 arası
  teaser penceresi TEMİZ spektakl; anons ~8.0; kesilme ≤9.3).
- Zincir açılışı: çekim 2-6 önceki çekimin SON VİSTASININ İÇİNDE, sarsıntı ortasında
  açılır (seed karesiyle süreklilik); ilk tam maske ~1.0 saniyede gelir.
- Sahne değişimi YALNIZ cam tamamen kapalı (karartma) ya da tamamen patlamışken
  (beyaz pozlama) olur. Yeşillik/duman/serpinti/kıvılcım kısmi maskedir: doku verir,
  sahne DEĞİŞTİRMEZ. Ekranda morph/erime/ışınlanma yasak.
- Maske coğrafi sıçrama yapmaz: yeni vista aynı durağın aynı hat üzerindeki daha
  yakın/derin/uç bir kesimidir; maske kısa bir hat aralığını gizler/sıkıştırır.

## Roklar

### ROCK 1 ,  bible.json `art_style` v2 (canon değişimi)
Dosya: `aimagine/next-stop/bible.json`, yalnız `art_style` alanı. Aşağıdaki İngilizce
metin MEVCUT metnin yerine birebir geçer (başka alan değişmez):

```
Raw photorealistic amateur smartphone footage, one unbroken handheld take, vertical 9:16, recorded inside a commuter train travelling at extreme speed. THE WINDOW IS THE SUBJECT: a single dirty rectangular LEFT-SIDE train window fills at least three quarters of the frame and the camera looks straight out through it at 90 degrees to the direction of travel. Never look forward or rearward, never leave the carriage, never show the train exterior, no aerial view, no third-person view, no zoom, no cinematic camera move, no stabilization. The glass and its black rubber frame stay between camera and world at all times, with a hairline scratch in the lower-left corner. PASSENGERS RIDE INSIDE: between the camera and the window, hugging the lower and right edges of the frame and much closer to the lens than the glass, ride a few ordinary commuters ,  dark, dim, out-of-focus shapes: the back of a head, a shoulder in a worn coat, hands gripping vertical poles and overhead straps, one seated figure lit only by a phone screen held low. They stay on the camera's side of the glass at all times, and their silhouettes may overlap only the lowest sixth of the window; the rest of the glass stays clear. Beyond the glass there is only landscape: no person, no face, no body and no human reflection ever appears on the far side of the glass or mirrored in it, and no passenger face is ever sharp, lit or recognizable. THE PASSENGERS ARE THE SEISMOGRAPH: every jolt of the ride is read on their bodies ,  they sway with the curves, stumble on the impacts, clutch the poles, bump shoulders; on the hard hits they are thrown sideways and gasp or scream; between hits they slump back into tired commuter stillness, which makes the violence read harder. SPEED AND VIOLENCE: the train is always moving forward and never stops, never slows and never arrives, and the ride is violent rather than smooth: the glass, the poles and the whole frame carry constant high-frequency vibration. Anything within ten metres of the glass crosses the entire frame in under a fifth of a second and is an unreadable streak. Mid-distance structures sweep past in well under a second. Only the far horizon drifts. Light and shadow strobe continuously across the interior. OCCLUSION TRANSITIONS ,  THE VIEW CHANGES EVERY FEW SECONDS: the journey is cut inside the take by occlusion events, never by editing. Roughly every three seconds something slams between the lens and the landscape and covers the whole window for a fraction of a second ,  a tunnel wall, a bridge pier or a passing train that blacks the frame out, or a light event that blows the exposure to full white ,  and when the glass clears it looks onto a DIFFERENT stretch of the same destination, further along the same line: nearer, deeper, stranger, bigger. The scene resets ONLY while the window is fully covered or fully blown out; walls of foliage, smoke, spray and embers may lash the glass for texture, but they never change the scene. Nothing outside ever morphs, dissolves or teleports on screen, and the occlusion hides only a short stretch of the same route, never a leap to somewhere unconnected. Within each vista the world behaves physically: a landmark enters at the leading edge of the window already visible in the distance, grows as it crosses the glass, and exits the trailing edge with violent parallax. EVERY OCCLUSION IS AN IMPACT: the wipe arrives together with a physical blow ,  the carriage judders and lurches, the camera shakes hard, the poles rattle, the glass booms, the passengers are thrown and cry out ,  then the ride steadies onto the new vista. SEAM RULE: every shot after the first opens INSIDE the previous vista, mid-shake, and its first full occlusion wipes the window within the first second and a half. TRANSIT PHYSICS: the route is physically real and its direction is felt in the carriage ,  the pitch of the line, the lean of the bodies, the pressure, the temperature and the side the light comes from all follow it. This shot's own text states which way the journey goes; follow that text exactly and invent no other kind of travel. The world outside is always brighter, hotter and more saturated than the carriage interior. CONTRAST CLIMBS, IT NEVER WASHES OUT: once the train is past the threshold the sky becomes the darkest region of the landscape ,  every light outside comes from below or from the landmarks themselves ,  while the carriage interior stays darker still. Each shot is darker overhead and hotter in its light source than the one before it, and the final shot is the darkest and the most extreme of the episode. Pale overcast, white haze, flat daylight, dust bloom and low-contrast distance are forbidden after the threshold. NO TEXT ANYWHERE: no signage, no destination board, no letters, no numbers, no subtitles and no captions in frame. The interior panelling above the window is bare. Crooked off-centre framing, handheld shake, rolling-shutter skew, autofocus hunting, auto-exposure pumping, glare, blown highlights, shadow noise, low-bitrate compression, smeared motion blur. Diegetic audio only, never music: maglev hum, carriage rumble, rattling poles, vibrating glass, exterior sound muffled through closed glass, and the passengers themselves ,  breath, startled gasps, short screams on the hard impacts. No gore, no graphic injury, no real religious figures, no trademarked property.
```

Değişimin özü: (a) "NOBODY IS EVER VISIBLE" kalktı → yolcular kamera tarafında, alt/sağ
kenarda, karanlık/yüzsüz; cam ötesi + yansıma insan yasağı DURUYOR; siluet örtmesi
pencerenin en alt altıda biri ile sınırlı. (b) OCCLUSION TRANSITIONS + EVERY OCCLUSION
IS AN IMPACT eklendi; sahne sıfırlama yalnız TAM örtme/patlama anında. (c) SEAM RULE:
zincirli çekim önceki vistanın içinde açılır, ilk tam maske ≤1.5 sn. (d) Ses canon'una
insan katmanı eklendi. (e) Yaklaşma kuralı vista-içi ve yan-pencere geometrisine göre
yazıldı (leading edge → trailing edge). (f) "dışarısı parlak" ile "gök en karanlık"
çelişkisi çözüldü: gök MANZARANIN en karanlık bölgesi, vagon içi ondan da karanlık.

### ROCK 2 ,  series.json `auto_replenish` v2 (shot_plan + brief)
Dosya: `aimagine/next-stop/series.json`, yalnız `auto_replenish.shot_plan` ve
`auto_replenish.brief`. Diğer alanlar (families, title_style, title_patterns, batch,
min_queue, shots=6, shot_seconds="10", hook_shot=6, chain_breaks=[1], credit_hard_cap)
AYNEN kalır.

Yeni `shot_plan` (6 öğe; üretilen her çekim prompt'u kendi öğesiyle BİREBİR başlar):

1. `HOOK. Open already mid-motion on a dull grey routine commute, one ordinary object streaking past the glass at arm's length. At 1.5 seconds a two-note chime cuts in and a calm neutral announcer says the destination line; nobody reacts, one passenger keeps scrolling a phone. The train slams into acceleration. At about 4 seconds the first full occlusion wipes the window and the glass clears further down the same line, where ONE thing in the distance is unmistakably wrong and already growing. At about 7 seconds a harder occlusion wipes the window again: the wrong thing now owns a third of the horizon and the passengers' heads turn to the glass.`
2. `HARD BREACH. Open still inside the previous vista, mid-shake. At about 1 second a full blackout swallows the window with a blow that throws the passengers, and the ordinary world is gone for good: the glass clears onto the threshold of the destination. At about 3.5 seconds a second full occlusion opens onto the far side of the threshold, the line physically committed with no way back. At about 6.5 seconds a third occlusion clears onto the destination's first true landmark entering the leading edge of the window, still distant but growing.`
3. `ARRIVAL EDGE. Open still inside the previous vista, mid-shake. At about 1 second the exposure blows out or crushes to black and recovers with an impact: the first landmark is suddenly much closer, growing past the window until it no longer fits. At about 3.5 seconds a full occlusion clears onto how far down or how far up the place goes ,  the scale must be frightening. At about 6.5 seconds another occlusion clears onto the landmark's mass passing at arm's length, flooding the carriage with its light while the passengers grab the poles and stay braced.`
4. `FLYTHROUGH. Open still inside the previous vista, mid-shake, the landmark's mass strobing past the glass at close range. At about 1 second a full occlusion punches the view INSIDE the destination: structure whipping across the glass with maximum parallax. At about 3.5 seconds a gap opens through a full occlusion onto what lies beyond, revealing the true size of the place. At about 6.5 seconds a last occlusion clears onto a second district of the destination with something larger already entering the leading edge. Each impact rocks the carriage hard.`
5. `DEEPEST SCALE. Open still inside the previous vista, mid-shake. At about 1 second the hardest impact of the episode hits the glass ,  heat, pressure, spray or shockwave that jolts the camera and knocks the focus; the passengers scream. The occlusion clears onto a vista wider and deeper than anything before it. At about 3.5 seconds and about 6.5 seconds two more full occlusions each open a still wider and deeper view; the single most spectacular second of the episode lives in the final vista.`
6. `HEART AND PAYOFF. Open still inside the previous vista, mid-shake, the train passing through or beneath something colossal. At about 3 seconds one full occlusion clears onto the heart of the place, and from 4 to 7 seconds the view stays clear and spectacular ,  the only long look of the episode, still rushing past with violent parallax. At about 8 seconds a calm ordinary commuter announcer quietly says the arrival line. The chime sounds again, the same voice begins only "Next stop-" and is cut off mid-word just after 9 seconds while the train is still moving forward and something new is already growing ahead.`

Yeni `brief` (Türkçe; tam metin, mevcut brief'in yerine geçer):

```
NEXT STOP üretim brief'i v2. >>> ÇIKTI DİLİ İNGİLİZCE <<< Bu brief Türkçedir ama bölüm başlığı, synopsis ve tüm çekim prompt'ları İngilizce yazılır. DEĞİŞMEZ KURALLAR: (1) İMZA FORMAT: her bölüm TEK bir imkânsız durağa yapılan altı çekimlik, yaklaşık 60 saniyelik kesintisiz bir tren yolculuğudur. Kamera vagonu ASLA terk etmez ve hep aynı sol pencereden, gidiş yönüne 90 derece yandan bakar. Pencere karenin en az dörtte üçünü kaplar. (2) YOLCULAR İÇERİDE: kameranın tarafında, karenin alt ve sağ kenarında, camdan çok daha yakın birkaç sıradan yolcu vardır ,  karanlık, odak dışı, yüzü hiç seçilmeyen siluetler: ense, omuz, direği kavrayan eller, telefon ışığıyla aydınlanan tek oturan figür. Siluetler pencerenin yalnız en alt altıda birini örtebilir. Camın ÖTESİNDE ve camda YANSIMA olarak hiçbir insan görünmez; camın ötesinde yalnız manzara vardır. Yolcular sismograftır: her darbede savrulur, tutunur, nefesi kesilir, sert darbelerde kısa çığlık atar; darbeler arasında yorgun banliyö sükûnetine döner. Belirli bir yüz, kimlik ya da kalabalık tarif etme. (3) ZİNCİR: çekim 1 sahneyi açar (chain=false), çekim 2-6 önceki son kareden zincirlenir (chain=true) ve her biri ÖNCEKİ VİSTANIN İÇİNDE, sarsıntı ortasında açılır; ilk tam maskesi ~1.0 saniyede gelir. Bölümler arasında zincir yoktur. hook_shot her zaman 6'dır. (4) KADANS ,  HER ÇEKİMDE ÜÇ VISTA, İKİ TAM MASKE: her 10 saniyelik çekim, aynı durağın birbirinden gerçekten farklı ÜÇ görünümünü içerir; maskeler ~3.0 ve ~6.5 saniyededir. İstisna: çekim 1'de maskeler ~4 ve ~7'dedir; çekim 6'da TEK maske ~3'tedir, 4-7 arası tek uzun temiz bakıştır. Sahne değişimi YALNIZ cam tamamen kapalıyken (tünel duvarı, köprü ayağı, karşı tren → tam karartma) ya da pozlama tamamen patlamışken (beyaz) olur; yeşillik/duman/serpinti/kıvılcım kısmi maskedir, doku verir ama sahne DEĞİŞTİRMEZ. Manzara ASLA ekranda dönüşmez, erimez, ışınlanmaz; 'X, Y'ye dönüşür' YASAK; 'maske kareyi kapatır, cam açıldığında Z görünür' yaz. Yeni vista aynı durağın AYNI HAT üzerindeki daha yakın/derin/uç bir kesimidir; maske kısa bir hat aralığını gizler, coğrafi sıçrama yapmaz. (5) HER MASKE BİR DARBEDİR: maske anında vagon sarsılır, kamera silkelenir, direkler takırdar, yolcular savrulur; büyük darbelerde çığlık. Kesme hissi bu darbeden gelir. (6) ZAMANLAMA GÜVENLİĞİ: kritik hiçbir olay (maske, anons, çığlık zirvesi) çekimin ilk 0.5 ve son 0.6 saniyesine yazılmaz; çekim gövdesi shot_plan önekindeki saatlerle ÇELİŞEN başka saat yazamaz, önekin saatlerine kendi vista içeriğini doldurur. Son çekimde varış anonsu ~8.0'da, 'Next stop-' kesilmesi 9.3'ten önce biter. (7) HIZ: tren asla durmaz, yavaşlamaz, varmaz. Cama on metreden yakın her şey kareyi saniyenin beşte birinden kısa sürede geçer; orta mesafe bir saniyenin altında süzülür; sadece ufuk yavaş kayar. 'Yavaşça', 'sakince', 'süzülerek' yasak. (8) SIRADAN DÜNYA EN FAZLA 4 SANİYE: durağın yanlışlığı çekim 1'in 4. saniyesinde ufukta görünmüş olmalı, 7. saniyesinde ufkun üçte birini kaplamalı. (9) VİSTA-İÇİ YAKLAŞMA: vista sürerken landmark pencerenin ön kenarından uzakta girer, cam boyunca büyür, arka kenardan şiddetli paralaksla çıkar; vista içinde hiçbir şey aniden belirmez. (10) ÖLÇEK TIRMANIR: bölümün ~16 vistası boyunca ölçek büyür; her çekimin son vistası öncekilerden büyüktür ve hiçbir çekim durağan, çözülmüş, 'varılmış' bir görüntüyle bitmez (çekim 6 finali dahil ,  o da hâlâ hareket hâlindedir). Aynı görünüm tipi üst üste iki vista tekrar edemez (yakından geçiş, dibe bakış, altından geçiş, gökyüzü, kanyon, şehir dokusu... dönüşümlü). (11) YAZI YOK: tabela, pano, harf, rakam, altyazı hiçbir karede görünmez. Bölüm sonu kancası yalnız SESLEDİR: çan çalar, anons 'Next stop-' derken kesilir. (12) DURAK SEÇİMİ: her bölüm YENİ bir durak seçer, aile rotasyonuna uyar, kullanılmış durağı tekrar etmez. Durak, yan pencereden paralaks üretecek ve üç çekim boyunca farklı 'semtler' sunabilecek katmanlı bir MEKÂN olmalıdır. (13) GÜVENLİK: telifli evren/karakter/yer adı yok; kan, vahşet, işkence, ceset, insan ıstırabı, gerçek dinî figür tasviri yok. Korku ölçekten, ısıdan, karanlıktan, hızdan gelir; çığlıklar irkilmedir, ıstırap değil. (14) ANONS: cümleler tam olarak 'Next stop: X.' ve 'Welcome to X.' biçimindedir; X küresel izleyicinin tek hamlede anladığı kısa bir isimdir. (15) PALET TAAHHÜDÜ: her durak baskın bir renk ve ısı seçer ve ona bağlı kalır. Dışarısı her zaman vagon içinden daha parlak ve daha doygundur. Nötr gri, soluk beton, düşük kontrast yasak. (16) KONTRAST TIRMANIR, YIKANMAZ: eşikten sonra gökyüzü MANZARANIN en karanlık bölgesidir, dış ışık aşağıdan ya da landmark'lardan gelir, vagon içi ondan da karanlıktır. Her çekim öncekinden daha karanlık tepeli ve daha sıcak ışıklıdır; 4., 5. ve 6. çekimin gövdesinde karanlık AÇIKÇA yazılır (kare zinciri kareyi kendiliğinden aydınlatma eğilimindedir). (17) GEÇİŞ FİZİĞİ: her durak bir YÖN seçer ve yön vagonda hissedilir. AŞAĞI: hat öne eğilir, basınç ve ısı artar, ışık pencerenin altına iner. YUKARI VE DIŞARI: önce zeminden kopulur, dünya küçülüp kavis alır, gök maviden siyaha boşalır, varış GERÇEK bir atmosfere girişle başlar. İÇİNDEN: yatay ama gerçek bir sınır katmanından geçilir. Tren fiziksel olarak gidemeyeceği yere varmaz; maskeler yolculuğu atlamaz, kısa aralıkları sıkıştırır. (18) YÖN SADECE ÇEKİM GÖVDESİNDE YAZILIR: canon evrenseldir; bölümün yönü yalnız o bölümün çekim gövdelerinde adım adım anlatılır. Bir bölümün gövdesinde uzay/yıldız/atmosfere giriş geçiyorsa bu yalnız o bölüm içindir.
```

### ROCK 3 ,  PİLOT: yeni canon'u gerçek üretimle doğrula (2 çekim, ~252 kredi ≈ $1.26)
Rock 1-2 uygulandıktan sonra, kuyruk yenilenmeden ÖNCE:
1. `series/experiment.py` altyapısıyla (ya da yoksa elle yazılmış 2 çekimlik izole bir
   mini planla, `output/experiments/` altında) yeni art_style + yeni çekim gramerine
   uyan İKİ gerçek Omni çekimi üret: çekim A (chain=false, HOOK grameri), çekim B
   (chain=true, A'nın son karesinden, ARRIVAL EDGE grameri). Bölüm state'ine, plans/
   klasörüne ve series.json sayaçlarına DOKUNULMAZ; kredi deneme defterine yazılır.
2. Geçme ölçütü (Fable kendisi kare kare bakar, Codex'in raporu kanıt değildir):
   her klipte ÜÇ ayrık vista + İKİ tam maske (kararma/patlama) + görünür yolcu
   silueti ve en az bir savrulma tepkisi; camın ötesinde insan YOK; pencere içinde
   yansıma YOK. Üç vistadan azı çıkarsa prompt katmanı revize edilir ve pilot bir kez
   tekrarlanır; ikinci başarısızlıkta kadans hedefi kullanıcıya taşınır (Owner's Box).
3. Pilot kanıtı olmadan Rock 4-5'e geçilmez.

### ROCK 4 ,  kuyruğu yeni canon'la yeniden üret
Bugünkü 19:32 UTC koşusu bittikten ve `git pull` yapıldıktan sonra:
1. Doğrula: `gh run list` → next-stop koşusu yok; `series.json` next_part == 4;
   `plans/part04.json`-`part08.json` bugünkü koşunun ürünü olarak mevcut.
2. `plans/part04.json` … `part08.json` dosyalarının TAMAMINI sil (ardışık hiçbir artık
   kalmadığını `ls` ile doğrula ,  _adopt_orphans ardışık artıkları geri sahiplenir).
3. `series.json` içinde `total_parts` = 3 yap.
4. `python -X utf8 -m series.replenish --series next-stop` çalıştır (yalnız Gemini
   harcar, Kie kredisi HARCAMAZ) → part04-08 yeni brief'le yazılır.
5. Deterministik denetim: 30 prompt'un tamamında (5 plan × 6 çekim) küçük bir kontrol
   betiğiyle say: shot_plan öneki birebir mi; "occlusion/blackout/blows out" maske dili
   ve "at about N seconds" saat işaretleri çekim başına ≥2 mi (çekim 6'da ≥1); yolcu
   tepki dili var mı; part04.json ayrıca elle tam okunur. Betik `output/` altında kalır,
   pipeline koduna girmez.

### ROCK 5 ,  kanıt + yayına bağlama
1. `python -X utf8 -m series.cli produce next-stop aimagine/next-stop/plans/part04.json --dry-run`
   exit 0: prompt montajı (art_style v2 + önek + gövde), zincir kararları, kredi kapıları.
2. Rock 4.5 denetim betiği temiz.
3. Commit + push (yalnız bu işin dosyaları: bible.json, series.json, plans/part04-08,
   RF-PLAN-NEXTSTOP-V2.md, RF-SAME-PAGE-LOG-NEXTSTOP-V2.md; `git add -A` YASAK) , 
   yarınki 13:20 UTC koşusundan önce, o sırada workflow çalışmıyorken.

## Non-goals
- Motor değişikliği yok (omni kalır; Seedance 2.5 denemesi ayrı deney olarak not edilir).
- Bölüm uzunluğu/çekim sayısı değişmez (6x10, micro_trim 0.45, hook_teaser offset 4.5 aynı).
- `series/*.py` ve `core/*.py` koduna dokunulmaz; bir doğrulayıcı yeni brief'i fiziksel
  olarak engelliyorsa kod değiştirilmez, BLOCKED raporlanır.
- Diğer serilere ve `RF-PLAN-YAYIN-DURDU.md` dosyasına dokunulmaz.
- part01-03 yeniden yayınlanmaz; QC/critic kod iyileştirmesi (zaman-hedefli maske denetimi)
  ISSUES'a.

## Riskler
- Omni 10 sn'de 3 vistayı her koşuda tutturamayabilir → Rock 3 pilotu bunu ÖNceden ölçer;
  pilot ölçütü 3 vista, 2'ye düşüş "kabul edilebilir" DEĞİLDİR (başarısız pilot = revizyon).
- Yolcu siluetleri kare zincirinde tutarlılığını kaybedebilir → yüzsüz/karanlık tarif +
  cam-ötesi ve yansıma yasağı hem canon'da hem brief'te açık; pilot çekim B bunu ölçer.
- Bugünkü koşunun ürettiği part03 eski canon'la yayınlanır (bilinçli: koşu iptal edilmedi).
