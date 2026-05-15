import qrcode

# Uygulamanı canlıya aldığında (Render/Vercel vb.) buraya gerçek URL'i yazmalısın.
# Lokal test için kendi ağındaki IP adresini yazabilirsin (Örn: http://192.168.1.X:5000)
BASE_URL = "https://127.0.0.1:5000"

def create_qr():
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(BASE_URL)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#1d3557", back_color="#ffffff")
    img.save("birthday_paradox_qr.png")
    print("QR Kod başarıyla 'birthday_paradox_qr.png' olarak oluşturuldu!")

if __name__ == "__main__":
    create_qr()