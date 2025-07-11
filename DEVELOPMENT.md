# دليل التطوير - ROV Control System

## 🛠️ إعداد بيئة التطوير

### متطلبات النظام
- Python 3.8 أو أحدث
- Git
- محرر النصوص (VS Code مُوصى به)

### خطوات الإعداد

1. **استنساخ المشروع**
```bash
git clone <repository-url>
cd ROV_CONTROL_GUI
```

2. **إنشاء بيئة افتراضية**
```bash
python -m venv rov_env
# Windows
rov_env\Scripts\activate
# Linux/Mac
source rov_env/bin/activate
```

3. **تثبيت المتطلبات**
```bash
pip install -r requirements.txt
```

4. **تشغيل setup**
```bash
python setup.py
```

## 🏗️ هيكل الكود

### المبادئ الأساسية
- **فصل الاهتمامات**: كل وحدة لها غرض محدد
- **التغليف**: البيانات والوظائف مجمعة في فئات
- **إعادة الاستخدام**: الكود قابل للإعادة والتوسيع
- **التعليقات**: تعليقات باللغة العربية للوضوح

### أنماط التصميم المستخدمة

#### 1. Model-View-Controller (MVC)
- **Model**: `sensors/`, `communication/`
- **View**: `gui/`
- **Controller**: `controller/`

#### 2. Observer Pattern
- استخدام Qt Signals and Slots
- معالجة الأحداث بطريقة منفصلة

#### 3. Factory Pattern
- إنشاء كائنات الاتصال حسب النوع
- إنشاء الحساسات حسب النوع

### قواعد الترميز

#### تسمية المتغيرات
```python
# متغيرات - snake_case
rov_controller = ROVController()
sensor_data = {}

# فئات - PascalCase
class ROVController:
    pass

# ثوابت - UPPER_CASE
MAX_DEPTH = 100
DEFAULT_PORT = 'COM3'

# دوال - snake_case
def connect_rov():
    pass
```

#### التعليقات
```python
class MotorController:
    """فئة التحكم في المحركات"""
    
    def set_manual_control(self, forward: float, strafe: float, vertical: float, yaw: float):
        """التحكم اليدوي المباشر
        
        Args:
            forward: حركة أمامي/خلفي (-100 إلى 100)
            strafe: حركة جانبية (-100 إلى 100)  
            vertical: حركة عمودية (-100 إلى 100)
            yaw: دوران (-100 إلى 100)
        """
        pass
```

## 🧪 الاختبار

### أنواع الاختبارات

#### 1. اختبارات الوحدة (Unit Tests)
```python
import unittest
from controller.motors import MotorController

class TestMotorController(unittest.TestCase):
    def setUp(self):
        self.motor_controller = MotorController()
    
    def test_manual_control(self):
        # اختبار التحكم اليدوي
        self.motor_controller.set_manual_control(50, 0, 0, 0)
        self.assertEqual(self.motor_controller.motor_speeds['front_left'], 1750)
```

#### 2. اختبارات التكامل
- اختبار الاتصال بين الوحدات
- اختبار تدفق البيانات
- اختبار واجهة المستخدم

#### 3. اختبارات الأداء
- اختبار سرعة الاستجابة
- اختبار استهلاك الذاكرة
- اختبار الثبات في التشغيل الطويل

### تشغيل الاختبارات
```bash
# جميع الاختبارات
python -m pytest

# اختبارات محددة
python -m pytest tests/test_motors.py

# مع تقرير التغطية
python -m pytest --cov=controller
```

## 🐛 استكشاف الأخطاء

### أدوات التشخيص

#### 1. نظام السجلات
```python
from utils.logger import ROVLogger

logger = ROVLogger('ModuleName')
logger.info("معلومة عامة")
logger.warning("تحذير")
logger.error("خطأ")
logger.debug("تفاصيل للتطوير")
```

#### 2. مراقب الأداء
```python
import cProfile
import pstats

# قياس الأداء
profiler = cProfile.Profile()
profiler.enable()
# كود يُراد قياسه
profiler.disable()

# عرض النتائج
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats()
```

### الأخطاء الشائعة وحلولها

#### 1. خطأ في الاتصال
```
ConnectionError: [Errno 2] No such file or directory
```
**الحل**: تحقق من المنفذ المحدد وتأكد من توصيل ROV

#### 2. خطأ في استيراد PyQt6
```
ModuleNotFoundError: No module named 'PyQt6'
```
**الحل**: 
```bash
pip install PyQt6
```

#### 3. خطأ في الكاميرا
```
cv2.error: OpenCV(4.x.x) error
```
**الحل**: تحقق من توصيل الكاميرا وصلاحيات الوصول

## 🚀 إضافة ميزات جديدة

### خطوات إضافة ميزة

#### 1. التخطيط
- حدد الغرض من الميزة
- ارسم مخطط التدفق
- حدد التأثير على الوحدات الأخرى

#### 2. التطوير
```python
# مثال: إضافة حساس جديد
class NewSensor:
    """حساس جديد"""
    
    def __init__(self):
        self.logger = ROVLogger('NewSensor')
        # تهيئة الحساس
    
    def start_reading(self):
        """بدء قراءة البيانات"""
        pass
    
    def get_data(self):
        """الحصول على البيانات"""
        pass
```

#### 3. الاختبار
- اكتب اختبارات للميزة الجديدة
- اختبر التكامل مع الوحدات الأخرى
- اختبر واجهة المستخدم

#### 4. التوثيق
- حدّث README.md
- أضف تعليقات للكود
- أضف أمثلة الاستخدام

### إرشادات المساهمة

#### 1. Git Workflow
```bash
# إنشاء فرع جديد
git checkout -b feature/new-sensor

# إضافة التغييرات
git add .
git commit -m "إضافة حساس جديد للكشف عن العوائق"

# دفع التغييرات
git push origin feature/new-sensor

# إنشاء Pull Request
```

#### 2. معايير الكود
- اتبع قواعد الترميز المحددة
- اكتب تعليقات واضحة
- اختبر الكود قبل الإرسال

#### 3. مراجعة الكود
- كل مساهمة تحتاج مراجعة
- تأكد من مرور جميع الاختبارات
- حافظ على جودة الكود

## 📚 موارد إضافية

### مكتبات مفيدة
- **PyQt6**: [الوثائق الرسمية](https://doc.qt.io/qtforpython/)
- **OpenCV**: [دروس OpenCV](https://opencv-python-tutroals.readthedocs.io/)
- **NumPy**: [دليل NumPy](https://numpy.org/doc/)
- **PySerial**: [وثائق PySerial](https://pythonhosted.org/pyserial/)

### أدوات التطوير
- **VS Code**: محرر مُوصى به مع ملحقات Python
- **Qt Designer**: لتصميم واجهات المستخدم
- **Git**: للتحكم في الإصدارات
- **pytest**: لتشغيل الاختبارات

### مجتمعات المطورين
- **Python.org**: المجتمع الرسمي لـ Python
- **Qt Community**: مجتمع مطوري Qt
- **ROV Forums**: منتديات المركبات المائية

## 🔧 الصيانة

### النسخ الاحتياطية
- احتفظ بنسخ احتياطية من الإعدادات
- احتفظ بسجلات التشغيل المهمة
- احتفظ بنسخ من بيانات المعايرة

### التحديثات
- راقب تحديثات المكتبات
- اختبر التحديثات في بيئة منفصلة
- حدّث الوثائق حسب الحاجة

### الأمان
- لا تشارك معلومات الاتصال الحساسة
- استخدم اتصالات آمنة عند الإمكان
- احتفظ بسجلات الأمان

---

**ملاحظة**: هذا الدليل في تطوير مستمر. ساهم في تحسينه عبر إضافة تجاربك ومقترحاتك.
