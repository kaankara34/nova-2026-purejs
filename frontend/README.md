# Local preview

## Güncel sürüm notu — 26 Ekim 2026

Site, `tr-destekli-versiyon` branch'inin `3a238f1` sürümü esas alınarak güncellendi.
Bu branch'teki `en/` ve `tr/` sayfaları, eski `source-pages` şablonlarından daha yeni
elle yapılmış düzenlemeler içeriyor. Şablonlar eşitlenmeden tam i18n derlemesini çalıştırmayın.
Dil seçici tasarımını tek başına güncellemek için proje kökünden
`python scripts/language_toggle_markup.py` kullanılabilir; diğer sayfa içeriğini değiştirmez.
Glass toggle stilleri `css/styles.css` dosyasının sonundadır. Dil bağlantıları ve cPanel
dizin yapısı değiştirilmemiştir.

Son sürümde etiketler switch'in dışındadır; içeride yuvarlak cam knob ve açıkta kalan bayrak
bulunur. Bayrak artık oval gövdenin tamamını ve şeffaf knob'un altını kesintisiz kaplar.
Özgün Wikimedia Commons SVG'leri `media/flags/` içindedir; kaynak ve lisans bilgileri
`media/flags/SOURCES.md` dosyasında kayıtlıdır. SVG'leri yeniden çizmeyin veya oranlarını değiştirmeyin.
`js/language-toggle.js` ve `js/language-toggle-gesture.js` yerel dosyaları tıklama,
sürükleme ve bırakınca dil değiştirme davranışını sağlar. JavaScript çalışmasa bile TR/EN
etiketleri mevcut sayfa bağlantıları üzerinden çalışır. Bu dosyaları da diğer `js/` dosyalarıyla
birlikte koruyun; ek hizmet veya kurulum gerekmez.

The generated language pages use portable asset paths such as `../css`, `../js`, and
`../media`. They work both when `frontend/` is opened through VS Code Live Server and when
the contents of `frontend/` are deployed directly into cPanel `public_html/`.

No custom Live Server root setting is required. Both of these URL forms work, depending on
whether VS Code opened the repository folder or the `frontend` folder itself:

```text
http://127.0.0.1:5500/tr/index.html
http://127.0.0.1:5500/frontend/tr/index.html
```

# Nova Konut İnşaat - DarGlobal Clone

Tamamen vanilla HTML, CSS ve JavaScript ile yazılmış statik website.

## 📁 Klasör Yapısı

```
clean-site/
├── index.html              # Ana sayfa
├── css/
│   └── styles.css          # Tüm stiller
├── js/
│   └── script.js           # Tüm JavaScript kodları
├── media/
│   ├── images/             # Görseller
│   │   └── nova-logo.png
│   ├── videos/             # Videolar
│   │   └── collab-video.mp4
│   └── fonts/              # Fontlar (şu an Google Fonts CDN kullanılıyor)
└── README.md               # Bu dosya
```

## 🚀 Nasıl Çalıştırılır?

### Yöntem 1: VS Code Live Server (Önerilen)
1. VS Code'da bu klasörü açın
2. Live Server extension'ını yükleyin
3. `index.html`'e sağ tıklayın → "Open with Live Server"

### Yöntem 2: Python HTTP Server
```bash
python3 -m http.server 8000
```
Sonra: http://localhost:8000

### Yöntem 3: Node.js http-server
```bash
npx http-server -p 8000
```

### Yöntem 4: cPanel / Hosting
Tüm dosyaları `public_html` klasörüne yükleyin. Hiçbir build veya compile gerekmiyor.

## 🌐 Canlıya Alma (Deploy)

Bu dosyalar herhangi bir web sunucusuna yüklenebilir:
- cPanel
- Netlify (drag & drop)
- Vercel
- GitHub Pages
- Herhangi bir hosting

Hiçbir Node.js, npm, build process gerekmez.

## 📝 Notlar

- Google Fonts CDN'den yüklenir (internet bağlantısı gerekir)
- Bazı görseller hala cdn.darglobal.co.uk'den yüklenir
- Tamamen responsive tasarım
- Hiçbir framework veya kütüphane kullanılmaz

## 📦 Bağımlılıklar

Yok! Pure HTML/CSS/JS.
