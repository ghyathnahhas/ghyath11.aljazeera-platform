import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app, db
from models import (
    User, College, StudyYear, Semester, Course, Lecture,
    Test, Question, TestResult, StudentEnrollment,
    Announcement, UniversityLogo, BackupLog, StudentReward, StudentTracking
)

def init_database():
    with app.app_context():
        db.create_all()

        if not User.query.filter_by(username="admin").first():
            u = User(number=1, first_name="مدير", second_name="المنصة", mobile="0900000000", username="admin", user_type="admin")
            u.set_password("admin123")
            db.session.add(u)

        if not User.query.filter_by(username="teacher1").first():
            u = User(number=2, first_name="أحمد", second_name="المدرس", mobile="0910000000", username="teacher1", user_type="teacher")
            u.set_password("teacher123")
            db.session.add(u)

        if not User.query.filter_by(username="teacher2").first():
            u = User(number=5, first_name="سارة", second_name="الأستاذة", mobile="0911000000", username="teacher2", user_type="teacher")
            u.set_password("teacher123")
            db.session.add(u)

        if not User.query.filter_by(username="student1").first():
            u = User(number=1001, first_name="محمد", second_name="الطالب", mobile="0920000000", username="student1", user_type="student")
            u.set_password("student123")
            db.session.add(u)

        if not User.query.filter_by(username="guest1").first():
            u = User(number=3, first_name="زائر", second_name="ضيف", mobile="0930000000", username="guest1", user_type="guest")
            u.set_password("guest123")
            db.session.add(u)

        db.session.commit()

        # الكليات الرئيسية
        top_colleges = [
            ("كلية الصيدلة", "Pharmacy College", "كلية متخصصة في علوم الصيدلة والأدوية", 0),
            ("كلية الهندسة", "Engineering College", "كلية متخصصة في الهندسة والتكنولوجيا", 1),
            ("كلية إدارة الأعمال", "Business Administration College", "كلية متخصصة في إدارة الأعمال والتجارة", 2),
            ("وحدة متطلبات الجامعة", "University Requirements Unit", "وحدة متطلبات الجامعة الإجبارية والاختيارية", 3),
        ]
        for name, en, desc, order in top_colleges:
            if not College.query.filter_by(name=name).first():
                db.session.add(College(name=name, name_en=en, description=desc, level=0, sort_order=order))
        db.session.commit()

        # أقسام كلية الهندسة
        eng = College.query.filter_by(name="كلية الهندسة").first()
        eng_depts = [
            ("قسم الهندسة المعلوماتية", "Information Engineering", "قسم متخصص في هندسة المعلوماتية والحواسيب"),
            ("قسم الهندسة المدنية", "Civil Engineering", "قسم متخصص في الهندسة المدنية والإنشائية"),
            ("قسم الهندسة المعمارية", "Architecture Engineering", "قسم متخصص في الهندسة المعمارية وتصميم المباني"),
        ]
        for dname, den, ddesc in eng_depts:
            if eng and not College.query.filter_by(name=dname).first():
                db.session.add(College(name=dname, name_en=den, description=ddesc, parent_id=eng.id, level=1))
        db.session.commit()

        # المدرسين
        t1 = User.query.filter_by(username="teacher1").first()
        t2 = User.query.filter_by(username="teacher2").first()
        teachers = [t for t in [t1, t2] if t]

        # بيانات كل كلية/قسم مع السنوات والمقررات
        all_units = []

        # كلية الصيدلة
        pharma = College.query.filter_by(name="كلية الصيدلة").first()
        if pharma:
            for yi, (yn, ye) in enumerate([
                ("السنة الدراسية الأولى", "First Year"),
                ("السنة الدراسية الثانية", "Second Year"),
                ("السنة الدراسية الثالثة", "Third Year"),
                ("السنة الدراسية الرابعة", "Fourth Year"),
                ("السنة الدراسية الخامسة", "Fifth Year"),
            ], 1):
                all_units.append((pharma.id, yn, ye, yi, [
                    ("مقدمة في الصيدلة", "Intro to Pharmacy", "PH101"),
                    ("الكيمياء الدوائية", "Pharmaceutical Chemistry", "PH102"),
                    ("علم الأدوية", "Pharmacology", "PH103"),
                ] if yi <= 2 else [
                    ("الصيدلة السريرية", "Clinical Pharmacy", "PH20" + str(yi)),
                    ("التقنية الصيدلية", "Pharmaceutical Technology", "PH21" + str(yi)),
                    ("السموم", "Toxicology", "PH22" + str(yi)),
                ]))

        # أقسام الهندسة الثلاثة
        eng_dept_data = {
            "قسم الهندسة المعلوماتية": [
                ("مبادئ الحاسوب", "Computer Principles", "CS101"),
                ("برمجة الحاسوب", "Computer Programming", "CS102"),
                ("هياكل البيانات", "Data Structures", "CS103"),
            ],
            "قسم الهندسة المدنية": [
                ("ميكانيكا المواد", "Mechanics of Materials", "CE101"),
                ("الرسم الهندسي", "Engineering Drawing", "CE102"),
                ("مساحة الطرق", "Road Surveying", "CE103"),
            ],
            "قسم الهندسة المعمارية": [
                ("مبادئ التصميم المعماري", "Arch Design Principles", "AR101"),
                ("الرسم المعماري", "Architectural Drawing", "AR102"),
                ("تاريخ العمارة", "History of Architecture", "AR103"),
            ],
        }
        for dname, courses_data in eng_dept_data.items():
            dept = College.query.filter_by(name=dname).first()
            if dept:
                for yi, (yn, ye) in enumerate([
                    ("السنة الدراسية الأولى", "First Year"),
                    ("السنة الدراسية الثانية", "Second Year"),
                    ("السنة الدراسية الثالثة", "Third Year"),
                    ("السنة الدراسية الرابعة", "Fourth Year"),
                ], 1):
                    ycode = str(yi)
                    yr_courses = [
                        (c[0], c[1], c[2].replace("101", ycode+"01").replace("102", ycode+"02").replace("103", ycode+"03"))
                        for c in courses_data
                    ]
                    all_units.append((dept.id, yn, ye, yi, yr_courses))

        # كلية إدارة الأعمال
        bus = College.query.filter_by(name="كلية إدارة الأعمال").first()
        if bus:
            for yi, (yn, ye) in enumerate([
                ("السنة الدراسية الأولى", "First Year"),
                ("السنة الدراسية الثانية", "Second Year"),
                ("السنة الدراسية الثالثة", "Third Year"),
                ("السنة الدراسية الرابعة", "Fourth Year"),
            ], 1):
                all_units.append((bus.id, yn, ye, yi, [
                    ("مبادئ الإدارة", "Principles of Management", "BA"+str(yi)+"01"),
                    ("المحاسبة المالية", "Financial Accounting", "BA"+str(yi)+"02"),
                    ("الاقتصاد", "Economics", "BA"+str(yi)+"03"),
                    ("التسويق", "Marketing", "BA"+str(yi)+"04"),
                ]))

        # وحدة متطلبات الجامعة
        req = College.query.filter_by(name="وحدة متطلبات الجامعة").first()
        if req:
            for yi, (yn, ye) in enumerate([
                ("السنة الدراسية الأولى", "First Year"),
                ("السنة الدراسية الثانية", "Second Year"),
            ], 1):
                all_units.append((req.id, yn, ye, yi, [
                    ("اللغة العربية", "Arabic Language", "UR"+str(yi)+"01"),
                    ("اللغة الإنجليزية", "English Language", "UR"+str(yi)+"02"),
                    ("مهارات الحاسوب", "Computer Skills", "UR"+str(yi)+"03"),
                    ("التفكير النقدي", "Critical Thinking", "UR"+str(yi)+"04"),
                ]))

        # إنشاء السنوات والفصول والمقررات
        semesters_data = [
            ("الفصل الدراسي الأول", "First Semester", "first", 1),
            ("الفصل الدراسي الثاني", "Second Semester", "second", 2),
            ("الفصل الدراسي الصيفي", "Summer Semester", "summer", 3),
        ]

        for college_id, yname, yen, yorder, courses_data in all_units:
            year = StudyYear.query.filter_by(college_id=college_id, name=yname).first()
            if not year:
                year = StudyYear(college_id=college_id, name=yname, name_en=yen, sort_order=yorder)
                db.session.add(year)
                db.session.commit()

            for sname, sen, stype, sorder in semesters_data:
                sem = Semester.query.filter_by(year_id=year.id, semester_type=stype).first()
                if not sem:
                    sem = Semester(year_id=year.id, name=sname, name_en=sen, semester_type=stype, sort_order=sorder)
                    db.session.add(sem)
                    db.session.commit()

                for cname, cen, ccode in courses_data:
                    if not Course.query.filter_by(semester_id=sem.id, code=ccode).first():
                        t = teachers[len(courses_data) % len(teachers)] if teachers else None
                        c = Course(semester_id=sem.id, name=cname, name_en=cen, code=ccode, teacher_id=t.id if t else None)
                        db.session.add(c)

        db.session.commit()
        print("تم إنشاء قاعدة البيانات بنجاح!")
        print("الكليات والأقسام مع سنواتها الدراسية:")
        for college in College.query.filter_by(parent_id=None).order_by(College.sort_order).all():
            print(f"  - {college.name}")
            for child in college.children.all():
                years = StudyYear.query.filter_by(college_id=child.id).count()
                print(f"    -> {child.name} ({years} سنوات دراسية)")
            years = StudyYear.query.filter_by(college_id=college.id).count()
            if years > 0:
                print(f"    -> ({years} سنوات دراسية)")

if __name__ == "__main__":
    init_database()

