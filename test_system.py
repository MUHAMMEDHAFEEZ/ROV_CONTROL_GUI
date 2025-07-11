#!/usr/bin/env python3
"""
اختبار سريع لنظام ROV Control System
يقوم بإنشاء محاكاة بسيطة للنظام
"""

import sys
import os

# إضافة المسار الحالي لـ Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """اختبار استيراد جميع الوحدات"""
    print("🔍 اختبار استيراد الوحدات...")
    
    try:
        # اختبار Utils
        from utils.config import Config
        from utils.logger import ROVLogger
        from utils.calibration import CalibrationManager
        print("✅ utils - تم بنجاح")
        
        # اختبار Communication
        from communication.serial_comm import SerialCommunication
        from communication.network_comm import NetworkCommunication
        from communication.packet_handler import PacketHandler
        print("✅ communication - تم بنجاح")
        
        # اختبار Controller
        from controller.motors import MotorController
        from controller.joystick_input import JoystickInput
        from controller.rov_controller import ROVController
        print("✅ controller - تم بنجاح")
        
        # اختبار Sensors
        from sensors.imu import IMUSensor
        from sensors.pressure_sensor import PressureSensor
        from sensors.temperature_sensor import TemperatureSensor
        print("✅ sensors - تم بنجاح")
        
        return True
        
    except ImportError as e:
        print(f"❌ خطأ في الاستيراد: {e}")
        return False

def test_basic_functionality():
    """اختبار الوظائف الأساسية"""
    print("\n🧪 اختبار الوظائف الأساسية...")
    
    try:
        # اختبار الإعدادات
        from utils.config import Config
        config = Config()
        print("✅ إنشاء كائن الإعدادات")
        
        # اختبار السجلات
        from utils.logger import setup_logger, ROVLogger
        setup_logger()
        logger = ROVLogger('Test')
        logger.info("اختبار نظام السجلات")
        print("✅ نظام السجلات يعمل")
        
        # اختبار متحكم المحركات
        from controller.motors import MotorController
        motor_controller = MotorController(config)
        motor_controller.set_manual_control(50, 0, 0, 0)
        print("✅ متحكم المحركات يعمل")
        
        # اختبار الحساسات
        from sensors.imu import IMUSensor
        imu = IMUSensor()
        imu_data = imu.get_all_data()
        print("✅ حساس IMU يعمل")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {e}")
        return False

def test_gui_components():
    """اختبار مكونات واجهة المستخدم"""
    print("\n🖥️  اختبار واجهة المستخدم...")
    
    try:
        # محاولة استيراد PyQt6
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import QTimer
        print("✅ PyQt6 متاح")
        
        # إنشاء تطبيق وهمي
        app = QApplication([])
        
        # اختبار مكونات GUI
        from gui.camera_feed import CameraFeedWidget
        from gui.control_panel import ControlPanelWidget
        from gui.telemetry_display import TelemetryDisplayWidget
        
        # إنشاء كائنات الاختبار
        from utils.config import Config
        config = Config()
        
        camera_widget = CameraFeedWidget(config)
        print("✅ أداة الكاميرا")
        
        telemetry_widget = TelemetryDisplayWidget(config)
        print("✅ أداة التيليمتري")
        
        app.quit()
        return True
        
    except ImportError as e:
        print(f"⚠️  PyQt6 غير متاح: {e}")
        print("   تشغيل: pip install PyQt6")
        return False
    except Exception as e:
        print(f"❌ خطأ في اختبار GUI: {e}")
        return False

def show_system_info():
    """عرض معلومات النظام"""
    print("\n📊 معلومات النظام:")
    print(f"🐍 Python: {sys.version}")
    print(f"💻 المنصة: {sys.platform}")
    
    # فحص المكتبات المتاحة
    libraries = [
        ("PyQt6", "واجهة المستخدم"),
        ("cv2", "معالجة الفيديو"),
        ("serial", "الاتصال التسلسلي"),
        ("pygame", "دعم الجويستيك"),
        ("numpy", "العمليات الرياضية"),
        ("yaml", "ملفات YAML")
    ]
    
    print("\n📚 المكتبات:")
    for lib_name, description in libraries:
        try:
            __import__(lib_name)
            print(f"  ✅ {lib_name} - {description}")
        except ImportError:
            print(f"  ❌ {lib_name} - {description} (غير متاح)")

def main():
    """الدالة الرئيسية للاختبار"""
    print("🚀 اختبار سريع لنظام ROV Control System")
    print("=" * 50)
    
    # عرض معلومات النظام
    show_system_info()
    
    # اختبار الاستيراد
    if not test_imports():
        print("\n❌ فشل في اختبار الاستيراد")
        return False
    
    # اختبار الوظائف الأساسية
    if not test_basic_functionality():
        print("\n❌ فشل في اختبار الوظائف الأساسية")
        return False
    
    # اختبار واجهة المستخدم
    gui_ok = test_gui_components()
    
    print("\n" + "=" * 50)
    if gui_ok:
        print("✅ جميع الاختبارات نجحت!")
        print("\n🎉 النظام جاهز للتشغيل!")
        print("استخدم: python main.py")
    else:
        print("⚠️  بعض مكونات واجهة المستخدم غير متاحة")
        print("لكن النظام الأساسي يعمل")
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  تم إيقاف الاختبار بواسطة المستخدم")
    except Exception as e:
        print(f"\n❌ خطأ غير متوقع: {e}")
        sys.exit(1)
