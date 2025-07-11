import numpy as np
import time
import threading
from typing import Dict, Optional, Callable, List, Tuple
from utils.logger import ROVLogger
from utils.calibration import CalibrationManager

class IMUSensor:
    """فئة حساس IMU (Inertial Measurement Unit)"""
    
    def __init__(self):
        self.logger = ROVLogger('IMU')
        self.calibration_manager = CalibrationManager()
        
        # بيانات IMU
        self.acceleration = {'x': 0.0, 'y': 0.0, 'z': 0.0}  # m/s²
        self.gyroscope = {'x': 0.0, 'y': 0.0, 'z': 0.0}    # deg/s
        self.magnetometer = {'x': 0.0, 'y': 0.0, 'z': 0.0} # µT
        self.orientation = {'roll': 0.0, 'pitch': 0.0, 'yaw': 0.0}  # degrees
        
        # إعدادات المرشح
        self.filter_alpha = 0.98  # معامل المرشح التكميلي
        self.sample_rate = 100    # Hz
        
        # معايرة
        self.is_calibrated = False
        self.calibration_data = {}
        
        # خيط قراءة البيانات
        self.reading_thread: Optional[threading.Thread] = None
        self.is_reading = False
        
        # معالج البيانات
        self.data_handler: Optional[Callable] = None
        
        # متغيرات المرشح
        self.last_update_time = time.time()
        
        self.logger.info("تم تهيئة حساس IMU")
    
    def start_reading(self):
        """بدء قراءة بيانات IMU"""
        if not self.is_reading:
            self.is_reading = True
            self.reading_thread = threading.Thread(target=self._reading_loop, daemon=True)
            self.reading_thread.start()
            self.logger.info("تم بدء قراءة بيانات IMU")
    
    def stop_reading(self):
        """إيقاف قراءة بيانات IMU"""
        self.is_reading = False
        if self.reading_thread and self.reading_thread.is_alive():
            self.reading_thread.join(timeout=2)
        self.logger.info("تم إيقاف قراءة بيانات IMU")
    
    def _reading_loop(self):
        """حلقة قراءة بيانات IMU"""
        while self.is_reading:
            try:
                # قراءة البيانات الخام
                raw_accel = self._read_accelerometer()
                raw_gyro = self._read_gyroscope()
                raw_mag = self._read_magnetometer()
                
                # تطبيق المعايرة
                if self.is_calibrated:
                    accel = self._apply_calibration(raw_accel, 'accelerometer')
                    gyro = self._apply_calibration(raw_gyro, 'gyroscope')
                    mag = self._apply_calibration(raw_mag, 'magnetometer')
                else:
                    accel = raw_accel
                    gyro = raw_gyro
                    mag = raw_mag
                
                # تحديث البيانات
                self.acceleration = accel
                self.gyroscope = gyro
                self.magnetometer = mag
                
                # حساب الاتجاه
                self._calculate_orientation()
                
                # إرسال البيانات للمعالج
                if self.data_handler:
                    self.data_handler(self.get_all_data())
                
                time.sleep(1.0 / self.sample_rate)
                
            except Exception as e:
                self.logger.error(f"خطأ في قراءة بيانات IMU: {e}")
                time.sleep(0.1)
    
    def _read_accelerometer(self) -> Dict[str, float]:
        """قراءة مقياس التسارع (محاكاة)"""
        # محاكاة بيانات مع ضوضاء
        return {
            'x': np.random.normal(0, 0.1),
            'y': np.random.normal(0, 0.1),
            'z': np.random.normal(9.81, 0.1)  # الجاذبية
        }
    
    def _read_gyroscope(self) -> Dict[str, float]:
        """قراءة الجايروسكوب (محاكاة)"""
        return {
            'x': np.random.normal(0, 0.5),
            'y': np.random.normal(0, 0.5),
            'z': np.random.normal(0, 0.5)
        }
    
    def _read_magnetometer(self) -> Dict[str, float]:
        """قراءة المغناطيسية (محاكاة)"""
        return {
            'x': np.random.normal(25, 2),
            'y': np.random.normal(0, 2),
            'z': np.random.normal(-40, 2)
        }
    
    def _apply_calibration(self, data: Dict[str, float], sensor_type: str) -> Dict[str, float]:
        """تطبيق معايرة الحساس"""
        if sensor_type not in self.calibration_data:
            return data
        
        calibration = self.calibration_data[sensor_type]
        calibrated_data = {}
        
        for axis in ['x', 'y', 'z']:
            offset = calibration.get('offset', {}).get(axis, 0)
            scale = calibration.get('scale', {}).get(axis, 1)
            calibrated_data[axis] = (data[axis] - offset) * scale
        
        return calibrated_data
    
    def _calculate_orientation(self):
        """حساب الاتجاه باستخدام المرشح التكميلي"""
        current_time = time.time()
        dt = current_time - self.last_update_time
        self.last_update_time = current_time
        
        if dt <= 0:
            return
        
        # حساب الاتجاه من التسارع
        accel_roll = np.arctan2(self.acceleration['y'], 
                               np.sqrt(self.acceleration['x']**2 + self.acceleration['z']**2))
        accel_pitch = np.arctan2(-self.acceleration['x'], 
                                np.sqrt(self.acceleration['y']**2 + self.acceleration['z']**2))
        
        # تحويل إلى درجات
        accel_roll = np.degrees(accel_roll)
        accel_pitch = np.degrees(accel_pitch)
        
        # تكامل الجايروسكوب
        gyro_roll = self.orientation['roll'] + self.gyroscope['x'] * dt
        gyro_pitch = self.orientation['pitch'] + self.gyroscope['y'] * dt
        gyro_yaw = self.orientation['yaw'] + self.gyroscope['z'] * dt
        
        # تطبيق المرشح التكميلي
        self.orientation['roll'] = self.filter_alpha * gyro_roll + (1 - self.filter_alpha) * accel_roll
        self.orientation['pitch'] = self.filter_alpha * gyro_pitch + (1 - self.filter_alpha) * accel_pitch
        self.orientation['yaw'] = gyro_yaw  # الـ yaw يعتمد على الجايروسكوب فقط (أو المغناطيسية)
        
        # تطبيق حدود الزوايا
        self.orientation['roll'] = self._normalize_angle(self.orientation['roll'])
        self.orientation['pitch'] = self._normalize_angle(self.orientation['pitch'])
        self.orientation['yaw'] = self._normalize_angle(self.orientation['yaw'])
    
    def _normalize_angle(self, angle: float) -> float:
        """تطبيع الزاوية إلى المدى [-180, 180]"""
        while angle > 180:
            angle -= 360
        while angle < -180:
            angle += 360
        return angle
    
    def calibrate(self, samples: int = 1000) -> bool:
        """معايرة IMU"""
        try:
            self.logger.info("بدء معايرة IMU...")
            
            # جمع عينات للمعايرة
            accel_samples = []
            gyro_samples = []
            
            for i in range(samples):
                accel_data = self._read_accelerometer()
                gyro_data = self._read_gyroscope()
                
                accel_samples.append(accel_data)
                gyro_samples.append(gyro_data)
                
                if i % 100 == 0:
                    progress = (i / samples) * 100
                    self.logger.info(f"تقدم المعايرة: {progress:.1f}%")
                
                time.sleep(0.01)
            
            # حساب الإزاحات
            accel_offsets = {}
            gyro_offsets = {}
            
            for axis in ['x', 'y', 'z']:
                accel_values = [sample[axis] for sample in accel_samples]
                gyro_values = [sample[axis] for sample in gyro_samples]
                
                accel_offsets[axis] = np.mean(accel_values)
                gyro_offsets[axis] = np.mean(gyro_values)
            
            # تعديل إزاحة Z للتسارع (إزالة الجاذبية)
            accel_offsets['z'] -= 9.81
            
            # حفظ بيانات المعايرة
            self.calibration_data = {
                'accelerometer': {
                    'offset': accel_offsets,
                    'scale': {'x': 1.0, 'y': 1.0, 'z': 1.0}
                },
                'gyroscope': {
                    'offset': gyro_offsets,
                    'scale': {'x': 1.0, 'y': 1.0, 'z': 1.0}
                },
                'timestamp': time.time()
            }
            
            self.is_calibrated = True
            self.logger.info("تمت معايرة IMU بنجاح")
            return True
            
        except Exception as e:
            self.logger.error(f"خطأ في معايرة IMU: {e}")
            return False
    
    def reset_orientation(self):
        """إعادة تعيين الاتجاه"""
        self.orientation = {'roll': 0.0, 'pitch': 0.0, 'yaw': 0.0}
        self.last_update_time = time.time()
        self.logger.info("تم إعادة تعيين الاتجاه")
    
    def set_filter_alpha(self, alpha: float):
        """تعديل معامل المرشح التكميلي"""
        self.filter_alpha = max(0.0, min(1.0, alpha))
        self.logger.info(f"تم تعديل معامل المرشح: {self.filter_alpha}")
    
    def set_data_handler(self, handler: Callable[[Dict], None]):
        """تعيين معالج البيانات"""
        self.data_handler = handler
    
    def get_acceleration(self) -> Dict[str, float]:
        """الحصول على بيانات التسارع"""
        return self.acceleration.copy()
    
    def get_gyroscope(self) -> Dict[str, float]:
        """الحصول على بيانات الجايروسكوب"""
        return self.gyroscope.copy()
    
    def get_orientation(self) -> Dict[str, float]:
        """الحصول على بيانات الاتجاه"""
        return self.orientation.copy()
    
    def get_all_data(self) -> Dict[str, any]:
        """الحصول على جميع بيانات IMU"""
        return {
            'acceleration': self.acceleration.copy(),
            'gyroscope': self.gyroscope.copy(),
            'magnetometer': self.magnetometer.copy(),
            'orientation': self.orientation.copy(),
            'timestamp': time.time(),
            'calibrated': self.is_calibrated
        }
    
    def get_tilt_angle(self) -> float:
        """حساب زاوية الميل الإجمالية"""
        roll = np.radians(self.orientation['roll'])
        pitch = np.radians(self.orientation['pitch'])
        
        tilt = np.degrees(np.arccos(np.cos(roll) * np.cos(pitch)))
        return tilt
    
    def is_level(self, tolerance: float = 5.0) -> bool:
        """فحص ما إذا كان ROV مستوٍ"""
        tilt = self.get_tilt_angle()
        return tilt < tolerance
    
    def save_calibration(self, filename: str = "imu_calibration.yaml"):
        """حفظ بيانات المعايرة"""
        import yaml
        
        try:
            with open(filename, 'w', encoding='utf-8') as file:
                yaml.dump(self.calibration_data, file, default_flow_style=False)
            self.logger.info(f"تم حفظ معايرة IMU في: {filename}")
        except Exception as e:
            self.logger.error(f"خطأ في حفظ معايرة IMU: {e}")
    
    def load_calibration(self, filename: str = "imu_calibration.yaml"):
        """تحميل بيانات المعايرة"""
        import yaml
        
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                self.calibration_data = yaml.safe_load(file)
            self.is_calibrated = True
            self.logger.info(f"تم تحميل معايرة IMU من: {filename}")
        except FileNotFoundError:
            self.logger.warning("ملف معايرة IMU غير موجود")
        except Exception as e:
            self.logger.error(f"خطأ في تحميل معايرة IMU: {e}")
