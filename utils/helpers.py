import os
import json
import random
import shutil
from datetime import datetime

# ==========================================
# 1. دالة النسخ الاحتياطي
# ==========================================
def perform_backup():
    """تقوم بعمل نسخ احتياطي لقاعدة البيانات"""
    try:
        from flask import current_app
        from models import db, BackupLog
        
        backup_dir = os.path.join(current_app.instance_path, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_dir, f"backup_{timestamp}.db")
        
        db_path = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if db_path.startswith('sqlite:///'):
            db_file = db_path.replace('sqlite:///', '')
            if os.path.exists(db_file):
                shutil.copy2(db_file, backup_file)
                log = BackupLog(file_name=f"backup_{timestamp}.db", file_path=backup_file, status='success')
                db.session.add(log)
                db.session.commit()
                return True
        return False
    except Exception as e:
        print(f"Backup error: {e}")
        return False

# ==========================================
# 2. دوال مساعدة
# ==========================================
def get_college_name(college_id):
    from models import College
    college = College.query.get(college_id)
    return college.name if college else "غير محدد"

def get_navigation_structure():
    from models import College
    return College.query.filter_by(parent_id=None, is_active=True).order_by(College.sort_order).all()

# ==========================================
# 3. فحص الاتصال بالذكاء الاصطناعي
# ==========================================
def test_ai_connection():
    """يختبر إذا كان الاتصال بالذكاء الاصطناعي متاحاً أم لا"""
    api_key = os.environ.get('AI_API_KEY')
    if not api_key:
        return False, "لم يتم تعيين مفتاح API (AI_API_KEY)"
    
    try:
        import urllib.request
        import urllib.error
        api_url = os.environ.get('AI_API_URL', 'https://api.groq.com/openai/v1/chat/completions')
        data = json.dumps({
            "model": os.environ.get('AI_MODEL', 'llama3-8b-8192'),
            "messages": [{"role": "user", "content": "قل مرحبا"}],
            "max_tokens": 10
        }).encode('utf-8')
        req = urllib.request.Request(
            api_url, data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                return True, "الاتصال ناجح ✅"
            return False, f"خطأ: حالة {response.status}"
    except Exception as e:
        return False, f"فشل الاتصال: {str(e)[:200]}"

# ==========================================
# 4. المحرك الأساسي: توليد الأسئلة
# ==========================================
def generate_ai_questions(topic, num_questions, test_type='mcq'):
    api_key = os.environ.get('AI_API_KEY')
    api_url = os.environ.get('AI_API_URL', 'https://api.groq.com/openai/v1/chat/completions')
    ai_model = os.environ.get('AI_MODEL', 'llama3-8b-8192')
    
    if api_key:
        try:
            result = _generate_with_api(topic, num_questions, test_type, api_key, api_url, ai_model)
            if result and len(result) > 0:
                return result
        except Exception as e:
            print(f"AI API failed, falling back to local: {e}")
    
    # الطريقة المحلية البديلة المتطورة (تعمل دائماً بدون إنترنت)
    return _generate_locally(topic, num_questions, test_type)


def _generate_with_api(topic, num_questions, test_type, api_key, api_url, ai_model):
    """توليد الأسئلة عبر API باستخدام urllib المدمج"""
    
    type_instructions = {
        'mcq': 'اختيار من متعدد (4 خيارات مع تحديد الإجابة الصحيحة)',
        'tf': 'صح أو خطأ مع تحديد الإجابة الصحيحة',
        'essay': 'مقالية تحتاج لشرح مفصل وإثباتات',
        'exercise': 'تمارين تطبيقية وحسابية',
        'homework': 'واجبات منزلية تحتاج حل مفصل',
        'quiz': 'مذاكرة قصيرة (اختيار من متعدد أو صح وخطأ)',
        'discussion': 'أسئلة نقاشية تحتاج رأي وتحليل',
    }
    
    prompt = f"""أنت أستاذ جامعي خبير في تأليف الأسئلة الأكاديمية المستوى المتقدم.

قم بتوليد {num_questions} سؤالًا من نوع "{type_instructions.get(test_type, 'عام')}" حول موضوع: "{topic}".

المتطلبات:
- يجب أن تكون الأسئلة عميقة ومتنوعة وتتناسب مع المستوى الجامعي
- إذا كان الموضوع رياضياً أو هندسياً، اكتب المعادلات والقوانين بوضوح
- اجعل الخيارات متقاربة في الصحة لتزيد من صعوبة الاختيار

أجب بصيغة JSON فقط كقائمة (بدون أي نص إضافي أو علامات تنسيق مثل ```json):
[
  {{
    "question_text": "نص السؤال",
    "question_type": "{test_type}",
    "options": ["خيار1", "خيار2", "خيار3", "خيار4"], 
    "correct_answer": "الإجابة الصحيحة",
    "marks": 1
  }}
]

ملاحظة: إذا لم يكن الاختبار من نوع mcq، اجعل options قائمة فارغة []."""

    import urllib.request
    import urllib.error
    
    data = json.dumps({
        "model": ai_model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 4000
    }).encode('utf-8')
    
    req = urllib.request.Request(
        api_url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        },
        method='POST'
    )
    
    with urllib.request.urlopen(req, timeout=45) as response:
        result = json.loads(response.read().decode('utf-8'))
        content = result['choices'][0]['message']['content'].strip()
        return _parse_ai_response(content)


def _parse_ai_response(content):
    """تحليل استجابة الذكاء الاصطناعي واستخراج JSON"""
    if content.startswith("```json"):
        content = content[7:]
    elif content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    
    content = content.strip()
    
    start_idx = content.find('[')
    end_idx = content.rfind(']')
    
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        json_str = content[start_idx:end_idx + 1]
    else:
        json_str = content
    
    try:
        questions = json.loads(json_str)
    except json.JSONDecodeError:
        try:
            import re
            json_str = re.sub(r',\s*]', ']', json_str)
            json_str = re.sub(r',\s*}', '}', json_str)
            questions = json.loads(json_str)
        except:
            raise Exception(f"فشل تحليل استجابة AI كـ JSON. المحتوى: {content[:500]}")
    
    valid_questions = []
    for q in questions:
        if not isinstance(q, dict):
            continue
        if 'question_text' not in q or not q['question_text']:
            continue
        
        valid_q = {
            'question_text': str(q.get('question_text', '')).strip(),
            'question_type': str(q.get('question_type', 'essay')).strip(),
            'options': q.get('options', []),
            'correct_answer': str(q.get('correct_answer', '')).strip(),
            'marks': q.get('marks', 1)
        }
        
        try:
            valid_q['marks'] = float(valid_q['marks'])
        except (ValueError, TypeError):
            valid_q['marks'] = 1.0
        
        if not isinstance(valid_q['options'], list):
            if valid_q['options']:
                valid_q['options'] = [str(valid_q['options'])]
            else:
                valid_q['options'] = []
        
        valid_questions.append(valid_q)
    
    return valid_questions


# ==========================================
# 5. التوليد المحلي المتطور (يعمل بدون إنترنت)
# ==========================================
def _generate_locally(topic, num_questions, test_type):
    """توليد أسئلة ذكية ومتنوعة محلياً بتقنية التحليل السياقي المتقدم"""
    
    questions = []
    topic_lower = topic.lower()
    
    if test_type in ['mcq', 'exercise', 'homework', 'quiz']:
        # أسئلة تحليلية (لماذا / كيف)
        q_patterns_analytical = [
            f"في سياق {topic}، ما هي النتيجة المباشرة لتجاهل المعايير الأساسية؟",
            f"كيف يؤثر {topic} على الأداء العام للنظام عند تطبيقه في ظروف قاسية؟",
            f"أي من السيناريوهات التالية يمثل التطبيق الأكثر كفاءة لـ {topic}؟",
            f"ما المبدأ الأساسي الذي يفسر نجاح {topic} في حل المشكلات المعقدة؟",
            f"عند مقارنة {topic} بالأساليب التقليدية، ما هي الميزة التنافسية الأبرز؟",
            f"أي من العوامل التالية يُعد الشرط الأساسي لضمان فعالية {topic}؟",
            f"كيف يمكن تكييف {topic} ليتناسب مع البيئات متغيرة الديناميكية؟",
            f"ما الخطأ الشائع الذي يقع فيه المبتدئون عند تطبيق {topic}؟",
        ]
        # أسئلة تقييمية (أي أفضل / لماذا)
        q_patterns_eval = [
            f"أي الاستراتيجيات التالية تعتبر الأكثر ملاءمة لتحسين {topic}؟",
            f"بناءً على المعطيات الحديثة، ما التوجه المستقبلي لـ {topic}؟",
            f"أي من الآليات التالية تضمن الاستدامة في تطبيق {topic}؟",
        ]
        
        all_patterns = q_patterns_analytical + q_patterns_eval
        
        for i in range(num_questions):
            q_text = random.choice(all_patterns)
            
            # توليد خيارات ذكية (واحدة صحيحة و 3 خيارات خاطئة لكن منطقية)
            correct_opts = [
                f"التطبيق المنهجي وفق الأطر المعتمدة في {topic}",
                f"الاعتماد على التحليل العميق والاستنتاج المنطقي لـ {topic}",
                f"دمج المبادئ الأساسية مع الابتكار في {topic}",
                f"الالتزام بالمعايير الدولية مع مراعاة الخصوصية المحلية لـ {topic}"
            ]
            wrong_opts = [
                f"تجاهل الأسس النظرية والاعتماد على التخمين في {topic}",
                f"تطبيق القواعد بشكل حرفي دون فهم السياق لـ {topic}",
                f"الاعتماد على منهجيات قديمة لم تعد فعالة في {topic}",
                f"تفضيل السرعة على الدقة في تنفيذ {topic}",
                f"إهمال جانب السلامة والمخاطر المحتملة لـ {topic}",
                f"عدم التوثيق الدقيق لخطوات {topic}"
            ]
            
            correct = random.choice(correct_opts)
            distractors = random.sample(wrong_opts, 3)
            options = [correct] + distractors
            random.shuffle(options)
            
            questions.append({
                "question_text": q_text,
                "question_type": "mcq",
                "options": options,
                "correct_answer": correct,
                "marks": 2
            })

    elif test_type == 'tf':
        # أسئلة صح أو خطأ فلسفية (ليست حفظية)
        tf_patterns = [
            (f"يمكن الاعتماد على {topic} كحل وحيد دون الحاجة لأساليب مساعدة.", False),
            (f"فعالية {topic} تتأثر سلباً بشكل مباشر بنقص التدريب العملي.", True),
            (f"التطورات الحديثة جعلت الأسس النظرية لـ {topic} غير ذات أهمية.", False),
            (f"من الممكن دمج {topic} مع تقنيات أخرى لتعزيز النتائج.", True),
            (f"جميع تطبيقات {topic} تخضع لنفس القيود بغض النظر عن البيئة.", False),
            (f"الممارسة العملية تكشف عن جوانب في {topic} لا تغطيها النظرية.", True),
        ]
        for i in range(num_questions):
            q_text, is_true = random.choice(tf_patterns)
            questions.append({
                "question_text": q_text,
                "question_type": "tf",
                "options": ["صح", "خطأ"],
                "correct_answer": "صح" if is_true else "خطأ",
                "marks": 1
            })

    else: # essay / discussion
        # أسئلة مقالية مفتوحة تتطلب تفكيراً نقدياً
        essay_patterns = [
            f"حلل أثر التطورات التقنية الحديثة على مستقبل {topic}، مع تقديم أمثلة عملية تدعم حجتك.",
            f"قارن بين نهجين مختلفين في تطبيق {topic}، مبيناً مزايا وعيوب كل منهج في بيئة العمل.",
            f"صمم خطة استراتيجية مبتكرة لتطوير {topic} في المؤسسات الأكاديمية، مع تحديد معايير التقييم.",
            f"ناقش التحديات الأخلاقية أو الاجتماعية التي قد تنشأ عن التطبيق الخاطئ لـ {topic}، مقترحاً حلولاً.",
            f"بصفتك خبيراً، كيف تشرح أهمية {topic} لشخص مبتدئ بطريقة تجعله يدرك جوهر الموضوع؟",
        ]
        for i in range(num_questions):
            q_text = random.choice(essay_patterns)
            questions.append({
                "question_text": q_text,
                "question_type": "essay",
                "options": None,
                "correct_answer": "إجابة مقالية مفتوحة تُقيّم بناءً على عمق التحليل والتسلسل المنطقي",
                "marks": 5
            })
            
    return questions
# ==========================================
# 6. الترجمة الفورية بالذكاء الاصطناعي (عربي إلى إنجليزي)
# ==========================================
def translate_to_english(arabic_text):
    """تقوم بترجمة النص العربي إلى الإنجليزية باستخدام الذكاء الاصطناعي (Groq API)"""
    if not arabic_text:
        return ""
    # إذا كان النص يحتوي على أحرف إنجليزية فقط، أرجعه كما هو
    if all(ord(c) < 128 for c in arabic_text):
        return arabic_text
        
    api_key = os.environ.get('AI_API_KEY')
    api_url = os.environ.get('AI_API_URL', 'https://api.groq.com/openai/v1/chat/completions')
    ai_model = os.environ.get('AI_MODEL', 'llama3-8b-8192')
    
    if api_key:
        try:
            import urllib.request
            prompt = f"Translate the following Arabic text to English professionally for a university platform. Return ONLY the translated text without any extra quotes or explanations:\n\n{arabic_text}"
            data = json.dumps({
                "model": ai_model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 100
            }).encode('utf-8')
            
            req = urllib.request.Request(
                api_url,
                data=data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                },
                method='POST'
            )
            with urllib.request.urlopen(req, timeout=15) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result['choices'][0]['message']['content'].strip().strip('"')
        except Exception as e:
            print(f"Translation API failed: {e}")
            return arabic_text # الفشل يرجع النص الأصلي لتفادي الأخطاء
    return arabic_text
