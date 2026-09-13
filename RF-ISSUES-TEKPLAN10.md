# RF-ISSUES — wild-encounter tek-plan-10 (ertelenenler)

- **scene_cut_fail gercek kapi.** Ayar su an olu: critic.py:1217-1231 her zaman
  "gated": False yaziyor, esik core/ffmpeg_tools.py:179-193 icinde 0.2'ye gomulu ve
  yalniz kirmizi-maviye gecen sentetik bir kesmeyle test edilmis. Tek plan formatinda
  kesme = ret olmali. Gercek kabul/ret Veo kliplerinden esik kalibre edilip
  kapi ayri bir is olarak baglanmali. ep07'nin kesik yayinlanmasinin sebebi budur.
- **PLATO_FORMAT surumlu goc.** "plato-3x8" adi artik formati anlatmiyor ama bir
  davranis anahtari (replenish.py:719,1215,1446,1496; produce.py:1225-1229) ve
  testler degeri pinliyor. Surumlu bir format kimligine gecis ayri bir is.
- **insect-giant ailesi.** Bocek/orumcek anatomisi "agza alinma" vurusunu yapamiyor
  (kendi ep07 olcumumuz) ve referans hesapta dev orumcek 72 begeni almis. Tek cekim
  formati oturduktan sonra aile listesi ayri bir karar olarak gozden gecirilmeli.
- **formatted_object sizintisi genel hali.** formatted_object = bool(format_version)
  oldugu icin format_version tanimlayan HER seri sabit-obje talimatlarindan pay
  aliyor. Bu dongude yalniz Plato dallari ayrildi; genel temizlik ayri bir is.
