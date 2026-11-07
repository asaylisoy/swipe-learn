# Kaydır & Öğren — CLAUDE.md

Telefonda reels gibi kaydırılarak kullanılan kişisel öğrenme uygulaması.
Sahibi: Almanya'da Informatik öğrencisi, Werkstudent pozisyonuna hazırlanıyor, ileride siber güvenlikte çalışmak istiyor.
Kullanıcıyla **Türkçe** konuş. Kart içerikleri Türkçe; teknik terimler İngilizce kalır; “SAY” alanı (mülakat cümlesi) **Almanca**.

## Yapı

```
template.html        UI (tek dosya: HTML + CSS + vanilla JS, framework yok)
content/job.txt      Bölüm 1: Werkstudent & mülakat (Java, Python, SQL, Git, kodlama mülakatı, şirket/domain)
content/code.txt     Bölüm 1b: Kod Pratiği — LeetCode Easy soruları + sektörden mini görevler (ipucu + Java/Python çözüm)
content/arch.txt     Bölüm 2: SOLID, design patterns, mimari türleri, sistem tasarımı
content/cyber.txt    Bölüm 3: siber güvenlik temelleri (kavram + savunma + kariyer)
scripts/build.py     content/*.txt -> template.html içine gömer -> index.html
scripts/vtt_to_chunks.py   YouTube altyazısını zaman damgalı metin parçalarına böler
transcripts/         (gitignore) ham altyazılar ve parçalar
index.html           ÜRETİLEN dosya, elle düzenleme
public/              PWA dosyaları (manifest, sw.js, ikonlar) — workflow index.html ile birlikte yayınlar
scripts/make_icons.py  public/ içindeki PNG ikonları üretir
.github/workflows/pages.yml  main'e push -> build -> https://asaylisoy.github.io/swipe-learn/
```

Build: `python3 scripts/build.py .` (template.html içindeki `%%CARDS%%` yerine kartları koyar).
Not: build.py henüz repo içinde değilse şu mantıkla yaz: job/arch/cyber.txt'yi sırayla birleştir, `</script` içermediğini kontrol et, `%%CARDS%%` ile değiştir, index.html'e yaz.

## Kart formatı (content/*.txt)

```
@@ bölüm | Konu · Alt konu | Kart başlığı (genelde bir soru)
A: Açıklama. Birden çok satır olabilir. "- " ile başlayan satırlar madde olur. `kod` ve **kalın** desteklenir.
CODE:
çok satırlı kod (opsiyonel)
EX: Gerçek hayattan / sektörden örnek (opsiyonel ama tercih edilir)
SAY: Mülakatta söylenecek tek-iki cümle, Almanca (opsiyonel)
HINT: ipucu (sadece code bölümü, katlanır kutuda)
SOL:
Java çözümü (katlanır)
PY:
Python çözümü (katlanır)
```
- `code` bölümünde problem metni (A) her modda açık görünür; altında kullanıcının kendi yaklaşımını yazdığı bir kutu var (localStorage `ko-notes`).
- Yeni kod sorusu eklerken: A = kendi cümlelerinle problem + örnek, HINT = yaklaşımı ele vermeden yön göster, SOL/PY = çalışan çözüm, EX = karmaşıklık + gerçek hayattaki karşılığı. **Her çözümü örneklerle gerçekten çalıştırıp doğrula.**
- `bölüm` ∈ `job | code | arch | cyber`. Kart kimliği = bölüm + başlık → başlığı değiştirmek kullanıcının ilerlemesini sıfırlar; gerekmedikçe değiştirme.
- Uygulama içi “Kart içe aktar” JSON formatı: `[{"s":"cyber","t":"Konu","q":"Başlık","A":"...","EX":"...","CODE":"...","SAY":"..."}]`

## İçerik kuralları

1. **Doğruluk önce gelir.** Emin olmadığın sürüm/tarih/sayıyı yazma veya doğrula. Kod örnekleri derlenebilir/çalışabilir olmalı.
2. Bir kart = bir kavram. Telefon ekranına sığacak uzunluk: A ≤ ~90 kelime, CODE ≤ ~15 satır.
3. Her kartta mümkünse **gerçek hayat örneği**: tercihen lojistik / tedarik zinciri / B2B yazılım dünyasından (başvurulan firma: Dortmund, supply chain risk/demand/capacity management, Fraunhofer IML kooperasyonu, KI & Data Analytics).
4. Bölüm 1'de her önemli kavrama Almanca `SAY` cümlesi ekle (basit, doğal, B1–B2 seviyesi).
5. Kaynaklardan kopyalama yapma; kendi cümlelerinle anlat.
6. **Siber güvenlik kartları kavram, savunma ve kariyer odaklıdır.** “Nedir, neden önemli, nasıl tespit/önlenir, mülakatta nasıl anlatılır” formatı. Saldırı adımlarını, exploit/payload komutlarını veya hazır saldırı tariflerini karta yazma; uygulamalı kısım için kullanıcı videoları kendi izole lab'ında ve yasal platformlarda (TryHackMe, HackTheBox, PortSwigger Academy) takip eder.

## Video serisinden içerik çıkarma (Bölüm 3)

Kaynak: https://github.com/LuNiZz/siber-guvenlik-sss reposunun önerdiği playlist
https://www.youtube.com/playlist?list=PLLKT__MCUeiwBa7d7F_vN1GUwz_2TmVQj
(The Cyber Mentor, “Zero to Hero”, 11 uzun video, 2019).

Adımlar (kullanıcının bilgisayarında, Claude Code ile):

1. Altyazıları indir (video indirmeden):
   ```bash
   pipx install yt-dlp   # ya da: brew install yt-dlp / pip install yt-dlp
   yt-dlp --skip-download --write-auto-subs --sub-langs en --sub-format vtt \
     -o "transcripts/raw/%(playlist_index)02d_%(id)s.%(ext)s" \
     "https://www.youtube.com/playlist?list=PLLKT__MCUeiwBa7d7F_vN1GUwz_2TmVQj"
   ```
   Alternatif: `pip install youtube-transcript-api`. YouTube rate-limit verirse araya `--sleep-requests 2` ekle.
2. Parçala: `python3 scripts/vtt_to_chunks.py transcripts/raw transcripts/chunks --minutes 15`
3. Her parça için (tek tek, tüm videoyu tek seferde değil):
   - Parçayı oku, önce `transcripts/notes/<video>.md` dosyasına konu başlıkları + zaman damgaları çıkar.
   - Sonra o notlardan kural 6'ya uygun kartlar üret, `content/cyber.txt` sonuna ekle. Konu alanına `TCM · <konu>` yaz, EX alanının sonuna kaynak zamanı ekle: `(Video 4, ~01:12:30)`.
   - Aynı kavramın kartı zaten varsa yenisini ekleme, mevcut kartı zenginleştir.
4. `python3 scripts/build.py .` ile yeniden üret, değişikliği kullanıcıya özetle.

Otomatik altyazı hatalıdır (özellikle araç isimleri, komutlar). Terimleri bağlamdan ve resmi dokümantasyondan düzelt.

## Yol haritası (sıradaki işler)

- [x] PWA: `manifest.json` + service worker → offline çalışsın, ana ekrana ikonla eklensin
- [x] GitHub Pages'e deploy (GitHub Actions ile build + publish)
- [x] Spaced repetition: “Tekrar” kartlarını 1-3-7 gün aralıklarıyla geri getir (Leitner kutuları), localStorage'da
- [ ] Günlük hedef sayacı (ör. günde 15 kart) ve seri (streak)
- [ ] Kod Pratiği: NeetCode 150'nin Arrays & Hashing, Two Pointers, Stack, Binary Search bölümlerindeki Easy'leri tamamla; birkaç kolay Medium ekle
- [ ] Bölüm 3'e: transkript pipeline'ı ile 11 videonun kartları

## Kod kuralları

- Vanilla JS, bağımlılık yok, tek dosya çıktı (index.html) — telefonda hızlı açılsın.
- Kullanıcıdan/JSON'dan gelen her metin ekrana basılmadan önce `esc()` ile escape edilir. `innerHTML`'e ham veri koyma.
- localStorage erişimi her zaman try/catch içinde.
- Değişiklikten sonra 390×800 viewport'ta (telefon) kontrol et.
