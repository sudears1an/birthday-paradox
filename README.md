# 🎂 Doğum Günü Paradoksu - Canlı Deney Sistemi

Bu proje, Tekirdağ Namık Kemal Üniversitesi Bilgisayar Mühendisliği Olasılık ve İstatistik (BMB206) dersi için hazırlanmış interaktif bir web sistemidir. "Doğum Günü Paradoksu" teorisini kullanıcıların canlı olarak deneyimlemesini sağlar.

Sistem, insan beyninin doğrusal düşünme eğilimine karşı çıkarak; sadece 23 kişinin bulunduğu bir ortamda bile iki kişinin aynı doğum gününe sahip olma ihtimalinin %50'yi geçtiğini gerçek zamanlı verilerle test edip kanıtlamayı amaçlar.

## 🚀 Özellikler
* **Gerçek Zamanlı Veri Toplama:** Katılımcılar sadece gün ve ay bilgisini girerek anonim olarak sisteme dahil olurlar.
* **Dinamik Olasılık Hesaplama:** O anki toplam katılımcı sayısına göre matematiksel çakışma (collision) ihtimali anlık olarak hesaplanır.
* **Otomatik Çakışma Tespiti:** Sistem veritabanını tarayarak aynı gün doğan kişileri tespit eder ve listeler.
* **Güvenlik & Anti-Spam:** `Rate Limiting` (Hız Sınırlandırması) ve XSS koruması ile zararlı veya spam veri girişleri engellenir.
* **Çift Veri Tabanı Mimarisi:** Sistem, geliştirme ortamında (yerel) otomatik olarak **SQLite** kullanırken, canlı ortamda (production) kalıcı veri depolama için **PostgreSQL**'e geçer.

## 🛠️ Kullanılan Teknolojiler
* **Backend:** Python, Flask
* **Frontend:** HTML5, CSS3, Vanilla JavaScript
* **Veri Tabanı:** SQLite3 (Local) & PostgreSQL (Production)
* **Görselleştirme:** Chart.js, MathJax (LaTeX formatı için)
* **Ekstra:** QR Code Generatör

## 💻 Kurulum ve Çalıştırma (Local Development)

Projeyi kendi bilgisayarınızda çalıştırmak için aşağıdaki adımları izleyebilirsiniz:

1. Python yüklü olduğundan emin olun.
2. Repoyu bilgisayarınıza indirin ve klasörün içine girin.
3. Gerekli kütüphaneleri kurun:
   ```bash
   pip install -r requirements.txt
   
   🌍 Canlı Demo
Bu proje Render üzerinde canlı olarak barındırılmaktadır.
Canlı deney sistemine katılmak için: [https://dogum-gunu-paradoksu.onrender.com]

Geliştirici: Sude Arslan