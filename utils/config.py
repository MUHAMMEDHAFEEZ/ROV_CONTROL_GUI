import configparser
import os
import yaml
from typing import Dict, Any

class Config:
    """فئة إدارة إعدادات المشروع"""
    
    def __init__(self, config_file="config.ini"):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.settings = {}
        self._load_default_config()
        self._load_config()
    
    def _load_default_config(self):
        """تحميل الإعدادات الافتراضية"""
        self.default_settings = {
            'COMMUNICATION': {
                'serial_port': 'COM3',
                'baud_rate': '9600',
                'timeout': '5',
                'use_network': 'False',
                'network_ip': '192.168.1.100',
                'network_port': '8080'
            },
            'GUI': {
                'window_width': '1200',
                'window_height': '800',
                'fps': '30',
                'camera_resolution': '640x480',
                'theme': 'dark'
            },
            'CONTROL': {
                'max_speed': '100',
                'acceleration': '10',
                'use_pid': 'True',
                'pid_kp': '1.0',
                'pid_ki': '0.1',
                'pid_kd': '0.05'
            },
            'SENSORS': {
                'imu_enabled': 'True',
                'pressure_enabled': 'True',
                'temperature_enabled': 'True',
                'data_logging': 'True'
            },
            'SAFETY': {
                'emergency_stop': 'True',
                'max_depth': '50',
                'auto_surface': 'True',
                'battery_warning': '20'
            }
        }
    
    def _load_config(self):
        """تحميل الإعدادات من الملف"""
        if os.path.exists(self.config_file):
            self.config.read(self.config_file, encoding='utf-8')
            # تحويل الإعدادات إلى قاموس
            for section in self.config.sections():
                self.settings[section] = dict(self.config[section])
        else:
            # إنشاء ملف إعدادات افتراضي
            self._create_default_config()
    
    def _create_default_config(self):
        """إنشاء ملف إعدادات افتراضي"""
        for section, options in self.default_settings.items():
            self.config[section] = options
        
        self._save_config()
        self.settings = self.default_settings.copy()
    
    def _save_config(self):
        """حفظ الإعدادات في الملف"""
        with open(self.config_file, 'w', encoding='utf-8') as configfile:
            self.config.write(configfile)
    
    def get(self, section: str, key: str, default=None):
        """الحصول على قيمة إعداد"""
        try:
            return self.settings.get(section, {}).get(key, default)
        except:
            return default
    
    def set(self, section: str, key: str, value: str):
        """تعديل قيمة إعداد"""
        if section not in self.settings:
            self.settings[section] = {}
        
        self.settings[section][key] = value
        
        if section not in self.config:
            self.config[section] = {}
        
        self.config[section][key] = value
        self._save_config()
    
    def get_int(self, section: str, key: str, default: int = 0) -> int:
        """الحصول على قيمة عددية صحيحة"""
        try:
            return int(self.get(section, key, default))
        except:
            return default
    
    def get_float(self, section: str, key: str, default: float = 0.0) -> float:
        """الحصول على قيمة عددية عشرية"""
        try:
            return float(self.get(section, key, default))
        except:
            return default
    
    def get_bool(self, section: str, key: str, default: bool = False) -> bool:
        """الحصول على قيمة منطقية"""
        try:
            value = self.get(section, key, str(default)).lower()
            return value in ['true', '1', 'yes', 'on']
        except:
            return default
