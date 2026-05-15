import qrcode
import qrcode.image.svg

# Render'dan aldığın canlı link
BASE_URL = "https://dogum-gunu-paradoksu.onrender.com" 

# QR kodu SVG formatında üretmek için ayar
factory = qrcode.image.svg.SvgImage

# Kodu oluştur ve kaydet
img = qrcode.make(BASE_URL, image_factory=factory)
img.save("harika_qr.svg")

print("Canva için kusursuz SVG dosyan hazır!")