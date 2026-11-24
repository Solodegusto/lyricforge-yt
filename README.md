# 🎵 LyricForge YT

Merak ettiğiniz şarkının YouTube bağlantısını yapıştırarak şarkı sözlerini ekranda okuyup **kopyalayabileceğiniz** ve **Türkçe / İngilizce / İspanyolca** dillerine çevirebileceğiniz açık kaynaklı Streamlit uygulaması. Dosya indirme yoktur; geçici ses verisi işlem sonunda otomatik silinir.

## ✨ Özellikler

- **Anında Bak & Kopyala:** Dosya indirme butonları olmadan şarkı sözlerini doğrudan ekranda görüntüleyin ve tek tıkla kopyalayın.
- **Çok Dilli Arayüz (TR / EN / ES):** Arayüzü **Türkçe**, **İngilizce** veya **İspanyolca** kullanın.
- **Şarkı Sözü Çevirisi (TR / EN / ES):** Orijinal sözleri hedef dile çevirin ve **İki Dilli Görünüm** ile yan yana/alt alta inceleyin.
- **Otomatik Dil Algılama & Donanım Optimizasyonu:** `faster-whisper` ile dili otomatik algılar; CUDA GPU varsa `float16`, CPU varsa `int8` kullanır.
- **Otomatik Temizlik:** Geçici ses dosyası işlem bittiğinde otomatik olarak silinir.

## 🛠️ Kurulum ve Çalıştırma

```bash
# FFmpeg kurulu olmalıdır (Windows: winget install Gyan.FFmpeg | macOS: brew install ffmpeg | Ubuntu: sudo apt install -y ffmpeg)
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```
