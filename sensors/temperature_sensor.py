import time
import threading
from typing import Optional, Callable, Dict, List
from utils.logger import ROVLogger

class TemperatureSensor:
    """فئة حساس درجة الحرارة"""
    
    def __init__(self):
        self.logger = ROVLogger('TemperatureSensor')
        
        # بيانات الحساس
        self.temperature = 20.0  # °C
        self.humidity = 50.0     # % (للحساسات التي تقيس الرطوبة أيضاً)
        
        # إعدادات المعايرة
        self.temperature_offset = 0.0
        self.temperature_scale = 1.0
        
        # دقة القراءة
        self.temperature_resolution = 0.1  # °C
        self.sample_rate = 5  # Hz
        
        # خيط قراءة البيانات
        self.reading_thread: Optional[threading.Thread] = None
        self.is_reading = False
        
        # معالج البيانات
        self.data_handler: Optional[Callable] = None
        
        # فلترة البيانات
        self.filter_samples = 10
        self.temperature_history = []
        
        # إنذارات
        self.min_temp_alarm = -5.0   # °C
        self.max_temp_alarm = 50.0   # °C
        self.alarm_handler: Optional[Callable] = None
        
        self.logger.info("تم تهيئة حساس درجة الحرارة")
    
    def start_reading(self):
        """بدء قراءة بيانات درجة الحرارة"""
        if not self.is_reading:
            self.is_reading = True
            self.reading_thread = threading.Thread(target=self._reading_loop, daemon=True)
            self.reading_thread.start()
            self.logger.info("تم بدء قراءة بيانات درجة الحرارة")
    
    def stop_reading(self):
        """إيقاف قراءة بيانات درجة الحرارة"""
        self.is_reading = False
        if self.reading_thread and self.reading_thread.is_alive():
            self.reading_thread.join(timeout=2)
        self.logger.info("تم إيقاف قراءة بيانات درجة الحرارة")
    
    def _reading_loop(self):
        """حلقة قراءة بيانات درجة الحرارة"""
        while self.is_reading:
            try:
                # قراءة البيانات الخام
                raw_temperature = self._read_raw_temperature()
                raw_humidity = self._read_raw_humidity()
                
                # تطبيق الفلترة
                filtered_temperature = self._apply_filter(raw_temperature)
                
                # تطبيق المعايرة
                calibrated_temperature = (filtered_temperature + self.temperature_offset) * self.temperature_scale
                
                # تحديث البيانات
                self.temperature = calibrated_temperature
                self.humidity = raw_humidity
                
                # فحص الإنذارات
                self._check_alarms()
                
                # إرسال البيانات للمعالج
                if self.data_handler:
                    self.data_handler(self.get_all_data())
                
                time.sleep(1.0 / self.sample_rate)
                
            except Exception as e:
                self.logger.error(f"خطأ في قراءة بيانات درجة الحرارة: {e}")
                time.sleep(0.1)
    
    def _read_raw_temperature(self) -> float:
        """قراءة درجة الحرارة الخام (محاكاة)"""
        import numpy as np
        
        # محاكاة درجة حرارة الماء مع تغييرات طبيعية
        base_temp = 22.0  # درجة الحرارة الأساسية
        
        # تغيير مع الوقت (محاكاة التيارات)
        time_factor = np.sin(time.time() * 0.01) * 2
        
        # ضوضاء القراءة
        noise = np.random.normal(0, 0.1)
        
        return base_temp + time_factor + noise
    
    def _read_raw_humidity(self) -> float:
        """قراءة الرطوبة الخام (محاكاة)"""
        import numpy as np
        
        # محاكاة رطوبة (مفيدة للحساسات في علبة مقاومة للماء)
        base_humidity = 45.0
        variation = np.sin(time.time() * 0.005) * 10
        noise = np.random.normal(0, 1)
        
        return max(0, min(100, base_humidity + variation + noise))
    
    def _apply_filter(self, temperature: float) -> float:
        """تطبيق فلتر متوسط متحرك"""
        self.temperature_history.append(temperature)
        
        # الاحتفاظ بعدد محدد من العينات
        if len(self.temperature_history) > self.filter_samples:
            self.temperature_history.pop(0)
        
        # حساب المتوسط
        return sum(self.temperature_history) / len(self.temperature_history)
    
    def _check_alarms(self):
        """فحص إنذارات درجة الحرارة"""
        if self.temperature < self.min_temp_alarm:
            alarm_msg = f"إنذار: درجة الحرارة منخفضة جداً: {self.temperature:.1f}°C"
            self.logger.warning(alarm_msg)
            if self.alarm_handler:
                self.alarm_handler("LOW_TEMPERATURE", self.temperature)
        
        elif self.temperature > self.max_temp_alarm:
            alarm_msg = f"إنذار: درجة الحرارة مرتفعة جداً: {self.temperature:.1f}°C"
            self.logger.warning(alarm_msg)
            if self.alarm_handler:
                self.alarm_handler("HIGH_TEMPERATURE", self.temperature)
    
    def calibrate_temperature(self, reference_temp: float, samples: int = 50) -> bool:
        """معايرة درجة الحرارة مقارنة بمرجع معروف"""
        try:
            self.logger.info(f"بدء معايرة درجة الحرارة مع المرجع: {reference_temp}°C")
            
            temp_samples = []
            
            for i in range(samples):
                temp = self._read_raw_temperature()
                temp_samples.append(temp)
                
                if i % 10 == 0:
                    progress = (i / samples) * 100
                    self.logger.info(f"تقدم المعايرة: {progress:.1f}%")
                
                time.sleep(0.2)
            
            # حساب متوسط القراءات
            avg_temp = sum(temp_samples) / len(temp_samples)
            
            # حساب الإزاحة
            self.temperature_offset = reference_temp - avg_temp
            
            self.logger.info(f"تم تعديل إزاحة درجة الحرارة: {self.temperature_offset:.2f}°C")
            return True
            
        except Exception as e:
            self.logger.error(f"خطأ في معايرة درجة الحرارة: {e}")
            return False
    
    def set_temperature_offset(self, offset: float):
        """تعيين إزاحة درجة الحرارة يدوياً"""
        self.temperature_offset = offset
        self.logger.info(f"تم تعديل إزاحة درجة الحرارة: {offset}°C")
    
    def set_temperature_scale(self, scale: float):
        """تعيين مقياس درجة الحرارة"""
        self.temperature_scale = scale
        self.logger.info(f"تم تعديل مقياس درجة الحرارة: {scale}")
    
    def set_alarm_limits(self, min_temp: float, max_temp: float):
        """تعيين حدود إنذار درجة الحرارة"""
        self.min_temp_alarm = min_temp
        self.max_temp_alarm = max_temp
        self.logger.info(f"تم تعديل حدود الإنذار: {min_temp}°C إلى {max_temp}°C")
    
    def set_filter_samples(self, samples: int):
        """تعديل عدد عينات الفلتر"""
        self.filter_samples = max(1, min(50, samples))
        self.temperature_history.clear()
        self.logger.info(f"تم تعديل عينات الفلتر: {self.filter_samples}")
    
    def set_data_handler(self, handler: Callable[[Dict], None]):
        """تعيين معالج البيانات"""
        self.data_handler = handler
    
    def set_alarm_handler(self, handler: Callable[[str, float], None]):
        """تعيين معالج الإنذارات"""
        self.alarm_handler = handler
    
    def get_temperature(self) -> float:
        """الحصول على درجة الحرارة الحالية"""
        return self.temperature
    
    def get_temperature_fahrenheit(self) -> float:
        """الحصول على درجة الحرارة بالفهرنهايت"""
        return (self.temperature * 9/5) + 32
    
    def get_humidity(self) -> float:
        """الحصول على الرطوبة الحالية"""
        return self.humidity
    
    def get_all_data(self) -> Dict:
        """الحصول على جميع بيانات الحساس"""
        return {
            'temperature_celsius': self.temperature,
            'temperature_fahrenheit': self.get_temperature_fahrenheit(),
            'humidity': self.humidity,
            'timestamp': time.time()
        }
    
    def get_temperature_statistics(self, window_minutes: int = 5) -> Dict:
        """الحصول على إحصائيات درجة الحرارة خلال فترة معينة"""
        if len(self.temperature_history) < 2:
            return {'min': 0, 'max': 0, 'avg': 0, 'std': 0}
        
        # أخذ العينات المناسبة للفترة المطلوبة
        samples_needed = min(len(self.temperature_history), window_minutes * 60 * self.sample_rate)
        recent_temps = self.temperature_history[-samples_needed:]
        
        import numpy as np
        return {
            'min': min(recent_temps),
            'max': max(recent_temps),
            'avg': np.mean(recent_temps),
            'std': np.std(recent_temps),
            'samples': len(recent_temps)
        }
    
    def get_temperature_trend(self) -> str:
        """تحديد اتجاه تغيير درجة الحرارة"""
        if len(self.temperature_history) < 5:
            return "غير محدد"
        
        recent_temps = self.temperature_history[-5:]
        
        # حساب الاتجاه
        if recent_temps[-1] > recent_temps[0] + 0.5:
            return "ارتفاع"
        elif recent_temps[-1] < recent_temps[0] - 0.5:
            return "انخفاض"
        else:
            return "مستقر"
    
    def is_temperature_stable(self, tolerance: float = 0.5, window_size: int = 10) -> bool:
        """فحص ما إذا كانت درجة الحرارة مستقرة"""
        if len(self.temperature_history) < window_size:
            return False
        
        recent_temps = self.temperature_history[-window_size:]
        temp_range = max(recent_temps) - min(recent_temps)
        
        return temp_range <= tolerance
    
    def save_calibration(self, filename: str = "temperature_calibration.yaml"):
        """حفظ بيانات المعايرة"""
        import yaml
        
        calibration_data = {
            'temperature_offset': self.temperature_offset,
            'temperature_scale': self.temperature_scale,
            'min_temp_alarm': self.min_temp_alarm,
            'max_temp_alarm': self.max_temp_alarm,
            'timestamp': time.time()
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as file:
                yaml.dump(calibration_data, file, default_flow_style=False)
            self.logger.info(f"تم حفظ معايرة درجة الحرارة في: {filename}")
        except Exception as e:
            self.logger.error(f"خطأ في حفظ معايرة درجة الحرارة: {e}")
    
    def load_calibration(self, filename: str = "temperature_calibration.yaml"):
        """تحميل بيانات المعايرة"""
        import yaml
        
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                calibration_data = yaml.safe_load(file)
            
            self.temperature_offset = calibration_data.get('temperature_offset', 0.0)
            self.temperature_scale = calibration_data.get('temperature_scale', 1.0)
            self.min_temp_alarm = calibration_data.get('min_temp_alarm', -5.0)
            self.max_temp_alarm = calibration_data.get('max_temp_alarm', 50.0)
            
            self.logger.info(f"تم تحميل معايرة درجة الحرارة من: {filename}")
        except FileNotFoundError:
            self.logger.warning("ملف معايرة درجة الحرارة غير موجود")
        except Exception as e:
            self.logger.error(f"خطأ في تحميل معايرة درجة الحرارة: {e}")
