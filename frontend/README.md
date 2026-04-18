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
