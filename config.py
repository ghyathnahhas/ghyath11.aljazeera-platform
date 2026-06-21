import os
from urllib.parse import quote_plus

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ghyath-university-platform-2026-super-secret-key-x9k2m'
    
    # بناء رابط قاعدة البيانات بشكل آمن لتفادي مشاكل الرموز في كلمة المرور
    DB_HOST = os.environ.get('DB_HOST')
    if DB_HOST:
        DB_USER = os.environ.get('DB_USER', 'postgres')
        DB_PASS = os.environ.get('DB_PASSWORD', '')
        DB_PORT = os.environ.get('DB_PORT', '5432')
        DB_NAME = os.environ.get('DB_NAME', 'postgres')
        SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{quote_plus(DB_PASS)}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"
    else:
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///' + os.path.join(basedir, 'database', 'university.db'))
        if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
            SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 1,
        'max_overflow': 2
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