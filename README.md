#  İş Takip Sistemi (İş Takip Pro)

İş Takip Sistemi, işletmeler ve ekipler için tasarlanmış, rol bazlı yetkilendirmeye sahip kapsamlı bir proje ve görev yönetim platformudur. Projelerin oluşturulması, ekiplerin atanması ve görevlerin yaşam döngüsünün takip edilmesi amacıyla geliştirilmiştir.

## 🌟 Özellikler

* **Rol Bazlı Erişim Kontrolü:** Sistemdeki her kullanıcının yetkileri, sahip olduğu role göre kısıtlanır veya genişletilir.
* **Proje Yönetimi:** Yeni projeler oluşturma, başlangıç ve bitiş (deadline) tarihleri belirleme ve proje sorumlusu atama işlemleri.
* **Görev (Task) Takibi:** Proje içindeki çalışanlara iş atama ve görev durumlarını (Yapılacak, Devam Ediyor, Sorun Var, Tamamlandı) anlık takip etme.
* **Yorum ve İletişim Sistemi:** Müşterilerin ve çalışanların görevler üzerinden yorum yapabilmesi ve proje adminiyle iletişim kurabilmesi.
* **Log ve Aktivite Kayıtları:** Sistem yöneticileri için kullanıcı hareketlerinin kaydedildiği detaylı log sistemi (ActionLog).
* **Güvenlik:** Parola sıfırlama sistemi, otomatik oturum zaman aşımı ve Vercel üzerinde güvenli barındırma altyapısı.

## 👥 Aktörler ve Roller

Sistem 4 temel aktör üzerine inşa edilmiştir:

* **Yönetici (Sistem Admini):** Projeleri oluşturur, iş dağılımını yapar, başlangıç ve deadline sürelerini belirler. Proje adminine iş atayabilir ve diğer yönetici rolleri hariç tüm kullanıcı rollerini değiştirebilir.
* **Proje Admini (Grup Lideri):** Atandığı projenin takımını oluşturur ve proje içi çalışanların rollerini yönetir. Görev süreçlerini takip edip yöneticiye raporlar.
* **Çalışan (Worker):** Sadece dahil olduğu projeleri görebilir. Kendisine atanan görevlerin durumunu günceller (tamamlandı, devam ediyor, sorun var vb.) ve süreç hakkında durum mesajları iletir.
* **Müşteri:** İlgili işin sürecini takip edebilir ve proje adminine yorum/geri bildirim yapabilir.


## 🛠️ Tech Stack

* **Backend:** Python 3.14, Django 6.0.5
* **Veritabanı:** MySQL (PyMySQL ve dj-database-url paketleri ile entegre)
* **Frontend:** HTML5, CSS3, JavaScript (Vanilla), Bootstrap 5
* **Ortam Yönetimi:** python-dotenv
* **Dağıtım (Deployment):** Vercel Serverless (wsgi entegrasyonu ile)

## Kurulum ve Çalıştırma

Projeyi yerel geliştirme ortamınızda çalıştırmak için aşağıdaki adımları izleyin:

**1. Projeyi Klonlayın ve Klasöre Girin:**
```bash
git clone <proje-repo-linki>
cd isTakipSistemi

**2. Sanal Ortam Oluşturun ve Aktif Edin:**
```bash
python -m venv .venv
# Windows için:
.venv\Scripts\activate
# macOS/Linux için:
source .venv/bin/activate
```

**3. Gerekli Paketleri Yükleyin:**
```bash
pip install -r requirements.txt

**4. .env dosyası oluşturun:**
SECRET_KEY=gizli_anahtariniz
DEBUG=TRUE
DATABASE_URL=mysql://kullanici_adi:sifre@host:port/veritabani_adi
EMAIL_HOST_PASSWORD=eposta_uygulama_sifreniz

**5. Veritabanı Migrations ve Süper Kullanıcı Oluşturun:**
python manage.py makemigrations
python manage.py migrate

**6. Varsayılan Rolleri ve Test Kullanıcılarını Oluşturun:**
python create_users.py

**7. Geliştirme Sunucusunu Başlatın:**
python manage.py runserver

**Tarayıcınızdan http://127.0.0.1:8000/ adresine giderek sistemi yerelinizde test edebilirsiniz.**