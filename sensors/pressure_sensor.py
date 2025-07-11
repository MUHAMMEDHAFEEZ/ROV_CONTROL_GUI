import time
import threading
from typing import Optional, Callable, Dict
from utils.logger import ROVLogger

class PressureSensor:
    """فئة حساس الضغط لقياس العمق"""
    
    def __init__(self):
        self.logger = ROVLogger('PressureSensor')
        
        # بيانات الحساس
        self.pressure = 1013.25  # hPa (ضغط جوي عند مستوى البحر)
        self.temperature = 20.0  # °C
        self.depth = 0.0         # متر
        self.altitude = 0.0      # متر
        
        # إعدادات المعايرة
        self.sea_level_pressure = 1013.25  # hPa
        self.pressure_offset = 0.0
        self.depth_factor = 0.01  # عامل تحويل الضغط إلى عمق
        
        # دقة القراءة
        self.pressure_resolution = 0.01  # hPa
        self.sample_rate = 10  # Hz
        
        # خيط قراءة البيانات
        self.reading_thread: Optional[threading.Thread] = None
        self.is_reading = False
        
        # معالج البيانات
        self.data_handler: Optional[Callable] = None
        
        # فلترة البيانات
        self.filter_samples = 5
        self.pressure_history = []
        
        self.logger.info("تم تهيئة حساس الضغط")
    
    def start_reading(self):
        """بدء قراءة بيانات الضغط"""
        if not self.is_reading:
            self.is_reading = True
            self.reading_thread = threading.Thread(target=self._reading_loop, daemon=True)
            self.reading_thread.start()
            self.logger.info("تم بدء قراءة بيانات الضغط")
    
    def stop_reading(self):
        """إيقاف قراءة بيانات الضغط"""
        self.is_reading = False
        if self.reading_thread and self.reading_thread.is_alive():
            self.reading_thread.join(timeout=2)
        self.logger.info("تم إيقاف قراءة بيانات الضغط")
    
    def _reading_loop(self):
        """حلقة قراءة بيانات الضغط"""
        while self.is_reading:
            try:
                # قراءة البيانات الخام
                raw_pressure = self._read_raw_pressure()
                raw_temperature = self._read_raw_temperature()
                
                # تطبيق الفلترة
                filtered_pressure = self._apply_filter(raw_pressure)
                
                # تطبيق المعايرة
                calibrated_pressure = filtered_pressure - self.pressure_offset
                
                # تحديث البيانات
                self.pressure = calibrated_pressure
                self.temperature = raw_temperature
                
                # حساب العمق والارتفاع
                self._calculate_depth_altitude()
                
                # إرسال البيانات للمعالج
                if self.data_handler:
                    self.data_handler(self.get_all_data())
                
                time.sleep(1.0 / self.sample_rate)
                
            except Exception as e:
                self.logger.error(f"خطأ في قراءة بيانات الضغط: {e}")
                time.sleep(0.1)
    
    def _read_raw_pressure(self) -> float:
        """قراءة الضغط الخام (محاكاة)"""
        import numpy as np
        
        # محاكاة ضغط متغير مع العمق
        base_pressure = 1013.25  # ضغط جوي
        depth_pressure = abs(self.depth) * 100  # كل متر = 100 hPa تقريباً
        noise = np.random.normal(0, 0.1)  # ضوضاء
        
        return base_pressure + depth_pressure + noise
    
    def _read_raw_temperature(self) -> float:
        """قراءة درجة الحرارة الخام (محاكاة)"""
        import numpy as np
        
        # محاكاة درجة حرارة الماء مع العمق
        surface_temp = 25.0  # درجة حرارة السطح
        temp_drop = abs(self.depth) * 0.1  # انخفاض مع العمق
        noise = np.random.normal(0, 0.2)
        
        return surface_temp - temp_drop + noise
    
    def _apply_filter(self, pressure: float) -> float:
        """تطبيق فلتر متوسط متحرك"""
        self.pressure_history.append(pressure)
        
        # الاحتفاظ بعدد محدد من العينات
        if len(self.pressure_history) > self.filter_samples:
            self.pressure_history.pop(0)
        
        # حساب المتوسط
        return sum(self.pressure_history) / len(self.pressure_history)
    
    def _calculate_depth_altitude(self):
        """حساب العمق والارتفاع من الضغط"""
        # حساب الارتفاع باستخدام المعادلة الجوية
        self.altitude = 44330 * (1 - (self.pressure / self.sea_level_pressure) ** 0.1903)
        
        # حساب العمق في الماء
        # كل 10.33 متر من الماء = 1 atm = 1013.25 hPa
        pressure_diff = self.pressure - self.sea_level_pressure
        self.depth = (pressure_diff / 1013.25) * 10.33
        
        # التأكد من أن العمق موجب تحت الماء
        if self.depth < 0:
            self.depth = 0
    
    def calibrate_sea_level(self, samples: int = 100) -> bool:
        """معايرة ضغط مستوى سطح البحر"""
        try:
            self.logger.info("بدء معايرة ضغط مستوى البحر...")
            
            pressure_samples = []
            
            for i in range(samples):
                pressure = self._read_raw_pressure()
                pressure_samples.append(pressure)
                
                if i % 10 == 0:
                    progress = (i / samples) * 100
                    self.logger.info(f"تقدم المعايرة: {progress:.1f}%")
                
                time.sleep(0.1)
            
            # حساب متوسط الضغط
            avg_pressure = sum(pressure_samples) / len(pressure_samples)
            self.sea_level_pressure = avg_pressure
            
            self.logger.info(f"تم تعديل ضغط مستوى البحر إلى: {self.sea_level_pressure:.2f} hPa")
            return True
            
        except Exception as e:
            self.logger.error(f"خطأ في معايرة ضغط مستوى البحر: {e}")
            return False
    
    def zero_depth(self):
        """تصفير العمق عند الموقع الحالي"""
        current_pressure = self._read_raw_pressure()
        self.pressure_offset = current_pressure - self.sea_level_pressure
        self.logger.info(f"تم تصفير العمق - إزاحة الضغط: {self.pressure_offset:.2f} hPa")
    
    def set_sea_level_pressure(self, pressure: float):
        """تعيين ضغط مستوى البحر يدوياً"""
        self.sea_level_pressure = pressure
        self.logger.info(f"تم تعديل ضغط مستوى البحر يدوياً: {pressure} hPa")
    
    def set_depth_factor(self, factor: float):
        """تعديل عامل تحويل العمق"""
        self.depth_factor = factor
        self.logger.info(f"تم تعديل عامل العمق: {factor}")
    
    def set_filter_samples(self, samples: int):
        """تعديل عدد عينات الفلتر"""
        self.filter_samples = max(1, min(20, samples))
        self.pressure_history.clear()
        self.logger.info(f"تم تعديل عينات الفلتر: {self.filter_samples}")
    
    def set_data_handler(self, handler: Callable[[Dict], None]):
        """تعيين معالج البيانات"""
        self.data_handler = handler
    
    def get_pressure(self) -> float:
        """الحصول على الضغط الحالي"""
        return self.pressure
    
    def get_depth(self) -> float:
        """الحصول على العمق الحالي"""
        return self.depth
    
    def get_altitude(self) -> float:
        """الحصول على الارتفاع الحالي"""
        return self.altitude
    
    def get_temperature(self) -> float:
        """الحصول على درجة الحرارة"""
        return self.temperature
    
    def get_all_data(self) -> Dict:
        """الحصول على جميع بيانات الحساس"""
        return {
            'pressure': self.pressure,
            'depth': self.depth,
            'altitude': self.altitude,
            'temperature': self.temperature,
            'sea_level_pressure': self.sea_level_pressure,
            'timestamp': time.time()
        }
    
    def is_underwater(self) -> bool:
        """فحص ما إذا كان ROV تحت الماء"""
        return self.depth > 0.1  # 10 سم
    
    def get_depth_rate(self, window_size: int = 5) -> float:
        """حساب معدل تغيير العمق (m/s)"""
        if len(self.pressure_history) < window_size:
            return 0.0
        
        # حساب معدل التغيير
        recent_pressures = self.pressure_history[-window_size:]
        if len(recent_pressures) < 2:
            return 0.0
        
        # تحويل الضغط إلى عمق
        depths = []
        for p in recent_pressures:
            pressure_diff = p - self.sea_level_pressure
            depth = (pressure_diff / 1013.25) * 10.33
            depths.append(max(0, depth))
        
        # حساب المعدل
        time_window = window_size / self.sample_rate
        depth_change = depths[-1] - depths[0]
        
        return depth_change / time_window
    
    def save_calibration(self, filename: str = "pressure_calibration.yaml"):
        """حفظ بيانات المعايرة"""
        import yaml
        
        calibration_data = {
            'sea_level_pressure': self.sea_level_pressure,
            'pressure_offset': self.pressure_offset,
            'depth_factor': self.depth_factor,
            'timestamp': time.time()
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as file:
                yaml.dump(calibration_data, file, default_flow_style=False)
            self.logger.info(f"تم حفظ معايرة الضغط في: {filename}")
        except Exception as e:
            self.logger.error(f"خطأ في حفظ معايرة الضغط: {e}")
    
    def load_calibration(self, filename: str = "pressure_calibration.yaml"):
        """تحميل بيانات المعايرة"""
        import yaml
        
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                calibration_data = yaml.safe_load(file)
            
            self.sea_level_pressure = calibration_data.get('sea_level_pressure', 1013.25)
            self.pressure_offset = calibration_data.get('pressure_offset', 0.0)
            self.depth_factor = calibration_data.get('depth_factor', 0.01)
            
            self.logger.info(f"تم تحميل معايرة الضغط من: {filename}")
        except FileNotFoundError:
            self.logger.warning("ملف معايرة الضغط غير موجود")
        except Exception as e:
            self.logger.error(f"خطأ في تحميل معايرة الضغط: {e}")
