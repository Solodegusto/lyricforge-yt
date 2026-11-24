# 🎵 LyricForge YT

YouTube müzik videolarından `yt-dlp` ve `faster-whisper` kullanarak otomatik şarkı sözü çıkaran, **Türkçe / İngilizce / İspanyolca** arayüz ve şarkı sözü çevirisi sunan açık kaynaklı Streamlit uygulaması.

## ✨ Özellikler

- **Tek Tıkla Çıkarma:** YouTube linkini yapıştırıp **Çıkar** butonuna basmanız yeterlidir.
- **Çok Dilli Arayüz (TR / EN / ES):** Sol menüden tüm arayüzü anında **Türkçe**, **İngilizce** veya **İspanyolca** yapabilirsiniz.
- **Zaman Damgalı Şarkı Sözü Çevirisi:** Çıkarılan sözleri **Türkçe (`tr`)**, **İngilizce (`en`)** veya **İspanyolca (`es`)** dillerine çevirir; zaman damgalarını koruyarak çeviri ve **iki dilli (Orijinal + Çeviri)** `.txt`, `.srt`, `.lrc` dosyaları oluşturur.
- **Otomatik Dil Algılama:** Türkçe ve İngilizce başta olmak üzere onlarca dili otomatik tanır.
- **GPU (CUDA) & CPU Optimizasyonu:** CUDA destekli GPU varsa `float16`, yalnızca CPU varsa `int8` hassasiyetiyle çalışır.
- **Otomatik Temizlik:** İndirilen geçici ses dosyaları (`try/finally` bloğu ile) işlem bittiğinde diskten otomatik silinir.

## 📁 Proje Yapısı

```text
lyricforge-yt/
├── app.py
├── requirements.txt
├── README.md
├── LICENSE
├── .gitignore
└── src/
    ├── __init__.py
    ├── audio.py
    ├── transcriber.py
    ├── translator.py
    └── i18n.py
```

## 🛠️ Kurulum

### 1. FFmpeg Kurulumu

Ses dönüştürme işlemleri için sisteminizde **FFmpeg** kurulu olmalıdır:

- **Windows (winget):**
  ```powershell
  winget install Gyan.FFmpeg
  ```
- **macOS (Homebrew):**
  ```bash
  brew install ffmpeg
  ```
- **Ubuntu / Debian:**
  ```bash
  sudo apt update && sudo apt install -y ffmpeg
  ```

### 2. Sanal Ortam ve Bağımlılıklar

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```

## ▶️ Çalıştırma

```bash
streamlit run app.py
```

Tarayıcınızda açılan `http://localhost:8501` adresinden uygulamayı kullanabilirsiniz.
