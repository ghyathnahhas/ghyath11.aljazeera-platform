import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from models import User, College, StudyYear, Semester, Course, Lecture, LectureFile
from models import Test, Question, TestResult, StudentEnrollment, Announcement
from models import UniversityLogo, BackupLog, StudentReward, StudentTracking, TeacherAssignment

def run_migration():
    app = create_app()
    with app.app_context():
        # التحقق من وجود الجدول وإنشاؤه إذا لم يكن موجوداً
        inspector = db.inspect(db.engine)
        table_names = inspector.get_table_names()

        # إضافة عمود جديدة لجدول users
        if 'users' in table_names:
            columns = [c['name'] for c in inspector.get_columns('users')]
            if 'study_year' not in columns:
                try:
                    db.session.execute('ALTER TABLE users ADD COLUMN study_year VARCHAR(100)')
                    db.session.commit()
                    print('تم إضافة عمود study_year')
                except Exception as e:
                    print(f'خطأ study_year: {e}')
                    db.session.rollback()

        # إنشاء جدول teacher_assignments إذا لم يكن موجوداً
        if 'teacher_assignments' not in table_names:
            db.create_all()
            print('تم إنشاء جدول teacher_assignments')
        else:
            print('جدول teacher_assignments موجود مسبقاً')

        # إعادة إنشاء الجداول المفقودة فقط
        all_models = [TeacherAssignment]
        for model in all_models:
            if model.__tablename__ not in table_names:
                db.create_all()
                print(f'تم إنشاء جدول {model.__tablename__}')

        print('تمت الهجرة بنجاح!')

if __name__ == '__main__':
    run_migration()
