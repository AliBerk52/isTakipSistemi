# ana_proje/email_settings.py

# ŞİMDİLİK: Geliştirme aşamasında mailleri VS Code terminalinde görmek için:
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# İLERİDE: Projeyi canlıya aldığında üstteki satırı silip (veya yoruma alıp) 
# aşağıdaki ayarları aktif edeceksin:

"""
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'bacaksizaliberk021@gmail.com'
EMAIL_HOST_PASSWORD = 'xqfcekcoejeunatv'
DEFAULT_FROM_EMAIL = 'İş Takip Sistemi <bacaksizaliberk021@gmail.com>'
"""