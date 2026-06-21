import json
from datetime import datetime, timezone
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# ==========================================
# نموذج المستخدمين
# ==========================================
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, unique=True, nullable=True)
    first_name = db.Column(db.String(100), nullable=False)
    second_name = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.String(20), nullable=True)
    username = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    user_type = db.Column(db.String(20), nullable=False, default='student')
    college_id = db.Column(db.Integer, db.ForeignKey('colleges.id'), nullable=True, index=True)
    study_year = db.Column(db.String(50), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime, nullable=True)
    login_count = db.Column(db.Integer, default=0)

    @property
    def full_name(self):
        return f"{self.first_name} {self.second_name}"

    @property
    def is_admin(self):
        return self.user_type == 'admin'

    @property
    def is_teacher(self):
        return self.user_type == 'teacher'

    @property
    def is_student(self):
        return self.user_type == 'student'

    @property
    def is_guest(self):
        return self.user_type == 'guest'

    @property
    def can_manage(self):
        return self.is_admin or self.is_teacher

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# ==========================================
# نموذج الكليات والأقسام
# ==========================================
class College(db.Model):
    __tablename__ = 'colleges'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    name_en = db.Column(db.String(200), nullable=True)
    description = db.Column(db.Text, nullable=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('colleges.id'), nullable=True)
    level = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    children = db.relationship('College', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')
    years = db.relationship('StudyYear', backref='college', lazy='dynamic')


# ==========================================
# نموذج السنوات الدراسية
# ==========================================
class StudyYear(db.Model):
    __tablename__ = 'study_years'

    id = db.Column(db.Integer, primary_key=True)
    college_id = db.Column(db.Integer, db.ForeignKey('colleges.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    name_en = db.Column(db.String(200), nullable=True)
    description = db.Column(db.Text, nullable=True)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    semesters = db.relationship('Semester', backref='year', lazy='dynamic')


# ==========================================
# نموذج الفصول الدراسية
# ==========================================
class Semester(db.Model):
    __tablename__ = 'semesters'

    id = db.Column(db.Integer, primary_key=True)
    year_id = db.Column(db.Integer, db.ForeignKey('study_years.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    name_en = db.Column(db.String(200), nullable=True)
    semester_type = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=True)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    courses = db.relationship('Course', backref='semester', lazy='dynamic')


# ==========================================
# نموذج المقررات الدراسية
# ==========================================
class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    semester_id = db.Column(db.Integer, db.ForeignKey('semesters.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    name_en = db.Column(db.String(200), nullable=True)
    code = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    teacher = db.relationship('User', backref='courses')
    lectures = db.relationship('Lecture', backref='course', lazy='dynamic')
    tests = db.relationship('Test', backref='course', lazy='dynamic')
    enrollments = db.relationship('StudentEnrollment', backref='course', lazy='dynamic')
    sessions = db.relationship('LiveSession', backref='course', lazy='dynamic')


# ==========================================
# نموذج المحاضرات
# ==========================================
class Lecture(db.Model):
    __tablename__ = 'lectures'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    name_en = db.Column(db.String(200), nullable=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    files = db.relationship('LectureFile', backref='lecture', lazy='dynamic')


# ==========================================
# نموذج ملفات المحاضرات
# ==========================================
class LectureFile(db.Model):
    __tablename__ = 'lecture_files'

    id = db.Column(db.Integer, primary_key=True)
    lecture_id = db.Column(db.Integer, db.ForeignKey('lectures.id'), nullable=False)
    file_type = db.Column(db.String(50), nullable=False, default='pdf')
    file_name = db.Column(db.String(255), nullable=True)
    file_path = db.Column(db.String(500), nullable=True)
    file_size = db.Column(db.Integer, nullable=True)
    external_link = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    @property
    def embed_url(self):
        if not self.external_link:
            return None
        url = self.external_link.strip()
        try:
            if 'youtube.com/watch' in url and 'v=' in url:
                vid = url.split('v=')[1].split('&')[0]
                return f"https://www.youtube.com/embed/{vid}"
            elif 'youtu.be/' in url:
                vid = url.split('youtu.be/')[1].split('?')[0]
                return f"https://www.youtube.com/embed/{vid}"
            elif 'drive.google.com' in url and '/d/' in url:
                file_id = url.split('/d/')[1].split('/')[0]
                return f"https://drive.google.com/file/d/{file_id}/preview"
        except Exception:
            return None
        return None


# ==========================================
# نموذج الاختبارات
# ==========================================
class Test(db.Model):
    __tablename__ = 'tests'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    test_type = db.Column(db.String(50), nullable=True)
    total_mark = db.Column(db.Float, default=100)
    per_question_mark = db.Column(db.Float, default=1)
    duration_minutes = db.Column(db.Integer, default=60)
    deadline = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    questions = db.relationship('Question', backref='test', lazy='dynamic')
    results = db.relationship('TestResult', backref='test', lazy='dynamic')


# ==========================================
# نموذج الأسئلة
# ==========================================
class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(50), nullable=True)
    options = db.Column(db.Text, nullable=True)
    correct_answer = db.Column(db.String(255), nullable=True)
    marks = db.Column(db.Float, default=1)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    # دالة لاستخراج الخيارات من قاعدة البيانات كقائمة بايثونية بدلاً من نص JSON
    def get_options(self):
        if not self.options:
            return []
        try:
            parsed = json.loads(self.options)
            if isinstance(parsed, list):
                return parsed
            return [parsed]
        except (json.JSONDecodeError, TypeError):
            if isinstance(self.options, str) and self.options.strip():
                return [self.options]
            return []

# ==========================================
# نموذج نتائج الاختبارات
# ==========================================
class TestResult(db.Model):
    __tablename__ = 'test_results'

    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    score = db.Column(db.Float, default=0)
    total_marks = db.Column(db.Float, default=0)
    percentage = db.Column(db.Float, default=0)
    answers = db.Column(db.Text, nullable=True)
    ai_evaluation = db.Column(db.Text, nullable=True)
    submitted_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship('User', backref='test_results')


# ==========================================
# نموذج تسجيل الطلاب
# ==========================================
class StudentEnrollment(db.Model):
    __tablename__ = 'student_enrollments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    is_approved = db.Column(db.Boolean, default=False)
    enrolled_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship('User', backref='enrollments')

    def get_student_name(self):
        if self.user:
            return self.user.full_name
        return "غير معروف"
    def get_course_name(self):
        if self.course:
            return self.course.name
        return "غير معروف"

# ==========================================
# نموذج الإعلانات والتنبيهات
# ==========================================
class Announcement(db.Model):
    __tablename__ = 'announcements'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=True)
    title = db.Column(db.String(200), nullable=True)
    message = db.Column(db.Text, nullable=False)
    msg_type = db.Column(db.String(50), default='general')
    priority = db.Column(db.String(50), default='normal')
    deadline = db.Column(db.DateTime, nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_announcements')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_announcements')


# ==========================================
# نموذج شعار الجامعة
# ==========================================
class UniversityLogo(db.Model):
    __tablename__ = 'university_logos'

    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


# ==========================================
# نموذج سجل النسخ الاحتياطي
# ==========================================
class BackupLog(db.Model):
    __tablename__ = 'backup_logs'

    id = db.Column(db.Integer, primary_key=True)
    file_path = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(50), default='success')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


# ==========================================
# نموذج جوائز الطلاب
# ==========================================
class StudentReward(db.Model):
    __tablename__ = 'student_rewards'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reward_type = db.Column(db.String(100), nullable=True)
    reward_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    points = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship('User', backref='rewards')


# ==========================================
# نموذج متابعة الطلاب
# ==========================================
class StudentTracking(db.Model):
    __tablename__ = 'student_trackings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    action_type = db.Column(db.String(200), nullable=True)
    action_details = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship('User', backref='tracking')
    course = db.relationship('Course', backref='tracking')


# ==========================================
# نموذج تعيين المدرسين للكليات
# ==========================================
class TeacherAssignment(db.Model):
    __tablename__ = 'teacher_assignments'

    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    college_id = db.Column(db.Integer, db.ForeignKey('colleges.id'), nullable=False)
    study_year_id = db.Column(db.Integer, db.ForeignKey('study_years.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    teacher = db.relationship('User', backref='assignments')
    college = db.relationship('College', backref='teacher_assignments')
    study_year = db.relationship('StudyYear', backref='teacher_assignments')


# ==========================================
# نموذج منتدى المقررات (المشاركات)
# ==========================================
class ForumPost(db.Model):
    __tablename__ = 'forum_posts'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=True)
    is_pinned = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    course = db.relationship('Course', backref='forum_posts')
    user = db.relationship('User', backref='forum_posts')
    replies = db.relationship('ForumReply', backref='post', lazy='dynamic')


# ==========================================
# نموذج منتدى المقررات (الردود)
# ==========================================
class ForumReply(db.Model):
    __tablename__ = 'forum_replies'

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('forum_posts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship('User', backref='forum_replies')


# ==========================================
# نموذج الرسائل النصية (الشات)
# ==========================================
class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    course = db.relationship('Course', backref='chat_messages')
    user = db.relationship('User', backref='chat_messages')


# ==========================================
# نموذج الجلسات الحية والأرشيف
# ==========================================
class LiveSession(db.Model):
    __tablename__ = 'live_sessions'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    session_number = db.Column(db.Integer, default=1)
    title = db.Column(db.String(200), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), default='upcoming')
    recording_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


# ==========================================
# نموذج مزامنة السبورة (لحفظ ضربات الفرشاة) - جديد
# ==========================================
class WhiteboardStroke(db.Model):
    __tablename__ = 'whiteboard_strokes'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    stroke_data = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    course = db.relationship('Course', backref='whiteboard_strokes')
    user = db.relationship('User', backref='whiteboard_strokes')