import logging
import os
from datetime import datetime

def setup_logger():
    """إعداد نظام التسجيل للمشروع"""
    
    # إنشاء مجلد السجلات إذا لم يكن موجوداً
    if not os.path.exists("logs"):
        os.makedirs("logs")
    
    # تحديد اسم ملف السجل بالتاريخ والوقت
    log_filename = f"logs/rov_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    # إعداد التنسيق
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # إعداد المسجل الرئيسي
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler()  # لعرض السجلات في الكونسول أيضاً
        ]
    )
    
    # إنشاء مسجل مخصص للمشروع
    logger = logging.getLogger('ROV_System')
    logger.info(f"تم بدء نظام التسجيل - ملف السجل: {log_filename}")
    
    return logger

class ROVLogger:
    """فئة مخصصة لتسجيل أحداث ROV"""
    
    def __init__(self, name):
        self.logger = logging.getLogger(f'ROV.{name}')
    
    def info(self, message):
        self.logger.info(message)
    
    def warning(self, message):
        self.logger.warning(message)
    
    def error(self, message):
        self.logger.error(message)
    
    def debug(self, message):
        self.logger.debug(message)
    
    def critical(self, message):
        self.logger.critical(message)
