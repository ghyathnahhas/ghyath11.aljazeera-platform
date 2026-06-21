import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ghyath-university-platform-2026-super-secret-key-x9k2m'
    
    # 🌟 ذكاء الإعدادات: إذا وجد رابط PostgreSQL في خوادم الاستضافة يستخدمه، وإلا يستخدم SQLite المحلي
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///' + os.path.join(basedir, 'database', 'university.db'))
    
    # إصلاح بروتوكول PostgreSQL لبعض مزودي الخدمة
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 1,        # زيادة حجم الاتصالات لاستيعاب الآلاف
        'max_overflow': 2,      # سماح باتصالات إضافية عند الضغط القصوى
    }

    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
    LOGO_FOLDER = os.path.join(basedir, 'static', 'uploads', 'logo')
    LECTURE_FOLDER = os.path.join(basedir, 'static', 'uploads', 'lectures')
    EXCEL_FOLDER = os.path.join(basedir, 'static', 'uploads', 'excel')
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024
    BACKUP_FOLDER = os.path.join(basedir, 'backups')
    LANGUAGES = ['ar', 'en']
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = 3600