# İş Takip Sistemi - Copilot Talimatları

## Proje Özeti
**İş Takip Sistemi** (isTakipSistemi), Django tabanlı bir işletme yönetim ve görev takibi platformudur. Projeler, roller ve abonelik seviyeleri ile çok katmanlı kullanıcı yönetimini destekler.

## Mimari Genel Bakış

### Teknoloji Yığını
- **Framework**: Django 6.0
- **Veritabanı**: Varsayılan SQLite (SQLite3)
- **Kimlik Doğrulama**: Django AbstractUser tabanlı özel User modeli
- **Ana Yapı**: 
  - `ana_proje/`: Proje yapılandırması (settings.py, urls.py, wsgi.py)
  - `management_app/`: İş mantığı ve veri modelleri

### Veri Modeli ve İlişkiler
Aşağıdaki temel modeller vardır:

1. **SubscriptionLevel**: Abonelik seviyeleri (junior, medior, senior)
2. **User** (AbstractUser genişletmesi):
   - Roller: ADMIN, PROJECT_MANAGER, WORKER, CLIENT
   - Abonelik seviyesi ile bağlantılı (ForeignKey)
3. **Project**: Proje bilgileri (ad, başlangıç tarihi, bitiş tarihi)
4. **ActionLog**: Sistem denetim günlükleri (kim ne yaptığını kaydet)
5. **PasswordResetToken**: Şifre sıfırlama tokenları (geçerlilik süresi kontrol edilmeli)
6. **UserSession**: Oturum yönetimi ve zaman aşımı (IP ve session_key ile)

### Önemli Kod Kuralları
- **Türkçe Yorumlar**: Kod yorum satırlarında Türkçe kullanılmaktadır
- **Model Alanı Adlandırması**: camelCase kullanılır (ör: `projectName`, `startDate`, `subLevel`)
- **Django Konvansiyonları**: Models AbstractUser'ı genişletir; admin paneli kayıt edilmemiş durumda

## Geliştirici İş Akışları

### Ortam Kurulumu
```bash
# Virtual environment'i etkinleştir
.venv\Scripts\activate

# Bağımlılıkları yükle (Django 6.0 ile uyumlu)
python -m pip install -r requirements.txt

# Veritabanı migrationlarını çalıştır
python manage.py migrate

# Geliştirme sunucusunu başlat
python manage.py runserver
```

### Model Değişiklikleri
1. `management_app/models.py` dosyasını düzenle
2. Migration oluştur: `python manage.py makemigrations`
3. Migration'u uygula: `python manage.py migrate`

### Admin Paneli
- Şu anda modeller admin paneline kaydedilmemiştir
- Yeni modeller eklerken `management_app/admin.py` dosyasında kayıt yapılmalıdır
- Örnek:
  ```python
  from django.contrib import admin
  from .models import User, Project, SubscriptionLevel
  
  admin.site.register(User)
  admin.site.register(Project)
  admin.site.register(SubscriptionLevel)
  ```

## Kritik Notlar

### Eksik Uygulamalar
- **views.py**: Boş durumdadır, endpoint'ler henüz tanımlanmamıştır
- **admin.py**: Model kayıtları yapılmamıştır
- **urls.py**: Yalnızca admin route'u vardır, API/sayfa route'ları eklenmelidir
- **Project Modeli**: Proje-kullanıcı ilişkisi tanımlanmamıştır (manager, team üyeleri)

### Güvenlik Hususları
- `PasswordResetToken`: Token geçerlilik süresi (TTL) kontrol mekanizması eklenmeli
- `UserSession`: İP adresi değişimi / oturum hijacking koruması düşünülmeli
- `ActionLog`: Sistem genelinde tetiklenme noktaları belirlenmelidir

### Veritabanı Seçimi
Şu anda varsayılan SQLite3 kullanılmaktadır. Üretim ortamında PostgreSQL tercih edilmelidir:
```bash
pip install psycopg2
# settings.py'da DATABASES yapılandırmasını güncelle
```

## İntegrasyon Noktaları
- **Django Admin**: Yönetim arayüzü için ön tanımlı (admin/)
- **Kimlik Doğrulama**: AbstractUser genişletmesi, özel roller ile
- **Audit Trail**: ActionLog modeli sistem aktivitelerini kaydetmek için hazırlı

## Yeni Özellik Eklerken
1. Model tanımlamalarını `management_app/models.py` dosyasına ekle
2. Gerekirse `admin.py` dosyasına admin interface'i kaydet
3. `ana_proje/urls.py` dosyasına yeni route'ları ekle
4. `management_app/views.py` dosyasında view fonksiyonları/sınıfları tanımla
5. Migration'ları oluştur ve uygula

## Dosya Yapısı
```
isTakipSistemi/
├── manage.py                  # Django yönetim CLI
├── requirements.txt           # Bağımlılıklar
├── ana_proje/                 # Proje yapılandırması
│   ├── settings.py           # Django ayarları
│   ├── urls.py               # URL yönlendirmesi
│   └── wsgi.py               # Üretim sunucusu için
├── management_app/           # Ana uygulama
│   ├── models.py             # Veri modelleri
│   ├── views.py              # İstek işleyicileri (BOŞ)
│   ├── admin.py              # Admin paneli (BOŞ)
│   └── migrations/           # Veritabanı geçişleri
└── .github/
    └── copilot-instructions.md
```
