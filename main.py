from gui.main_window import MainWindow
from PyQt6.QtWidgets import QApplication
import sys
import logging
from utils.logger import setup_logger
from utils.config import Config

def main():
    # إعداد نظام التسجيل
    setup_logger()
    logger = logging.getLogger(__name__)
    logger.info("بدء تشغيل ROV Control System")
    
    # تحميل الإعدادات
    config = Config()
    
    # إنشاء تطبيق Qt
    app = QApplication(sys.argv)
    app.setApplicationName("ROV Control System")
    app.setApplicationVersion("1.0.0")
    
    try:
        # إنشاء النافذة الرئيسية
        window = MainWindow(config)
        window.show()
        
        logger.info("تم تشغيل التطبيق بنجاح")
        
        # تشغيل التطبيق
        sys.exit(app.exec())
        
    except Exception as e:
        logger.error(f"خطأ في تشغيل التطبيق: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
