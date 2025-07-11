import time
import threading
from typing import Dict, List, Optional, Callable, Any
from utils.logger import ROVLogger
from utils.config import Config

class PIDController:
    """متحكم PID للتحكم في الحركة"""
    
    def __init__(self, kp: float = 1.0, ki: float = 0.1, kd: float = 0.05):
        self.kp = kp  # معامل التناسب
        self.ki = ki  # معامل التكامل
        self.kd = kd  # معامل المشتق
        
        self.previous_error = 0.0
        self.integral = 0.0
        self.last_time = time.time()
    
    def update(self, setpoint: float, current_value: float) -> float:
        """تحديث المتحكم PID وإرجاع القيمة المطلوبة"""
        current_time = time.time()
        dt = current_time - self.last_time
        
        if dt <= 0.0:
            return 0.0
        
        # حساب الخطأ
        error = setpoint - current_value
        
        # تحديث التكامل
        self.integral += error * dt
        
        # حساب المشتق
        derivative = (error - self.previous_error) / dt
        
        # حساب الإخراج
        output = (self.kp * error) + (self.ki * self.integral) + (self.kd * derivative)
        
        # تحديث القيم للدورة القادمة
        self.previous_error = error
        self.last_time = current_time
        
        return output
    
    def reset(self):
        """إعادة تعيين المتحكم"""
        self.previous_error = 0.0
        self.integral = 0.0
        self.last_time = time.time()
    
    def set_parameters(self, kp: float, ki: float, kd: float):
        """تعديل معاملات PID"""
        self.kp = kp
        self.ki = ki
        self.kd = kd

class MotorController:
    """فئة التحكم في المحركات"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = ROVLogger('MotorController')
        
        # حالة المحركات
        self.motor_speeds = {
            'front_left': 1500,    # PWM value (1000-2000, 1500=neutral)
            'front_right': 1500,
            'back_left': 1500,
            'back_right': 1500,
            'vertical_1': 1500,
            'vertical_2': 1500
        }
        
        # حدود السرعة
        self.min_pwm = 1000
        self.max_pwm = 2000
        self.neutral_pwm = 1500
        
        # إعدادات الأمان
        self.emergency_stop = False
        self.max_speed = self.config.get_int('CONTROL', 'max_speed', 100)
        self.acceleration_limit = self.config.get_int('CONTROL', 'acceleration', 10)
        
        # متحكمات PID للمحاور
        if self.config.get_bool('CONTROL', 'use_pid', True):
            kp = self.config.get_float('CONTROL', 'pid_kp', 1.0)
            ki = self.config.get_float('CONTROL', 'pid_ki', 0.1)
            kd = self.config.get_float('CONTROL', 'pid_kd', 0.05)
            
            self.pid_controllers = {
                'x': PIDController(kp, ki, kd),
                'y': PIDController(kp, ki, kd),
                'z': PIDController(kp, ki, kd),
                'yaw': PIDController(kp, ki, kd)
            }
        else:
            self.pid_controllers = None
        
        # معايرة المحركات
        self.motor_calibration = {}
        
        # معالج إرسال الأوامر
        self.command_sender: Optional[Callable] = None
        
        # خيط التحكم المستمر
        self.control_thread: Optional[threading.Thread] = None
        self.is_controlling = False
        
        self.logger.info("تم تهيئة متحكم المحركات")
    
    def set_command_sender(self, sender: Callable[[Dict[str, int]], bool]):
        """تعيين دالة إرسال أوامر المحركات"""
        self.command_sender = sender
    
    def start_control_loop(self):
        """بدء حلقة التحكم المستمرة"""
        if not self.is_controlling:
            self.is_controlling = True
            self.control_thread = threading.Thread(target=self._control_loop, daemon=True)
            self.control_thread.start()
            self.logger.info("تم بدء حلقة التحكم")
    
    def stop_control_loop(self):
        """إيقاف حلقة التحكم"""
        self.is_controlling = False
        if self.control_thread and self.control_thread.is_alive():
            self.control_thread.join(timeout=2)
        self.logger.info("تم إيقاف حلقة التحكم")
    
    def _control_loop(self):
        """حلقة التحكم الرئيسية"""
        while self.is_controlling:
            try:
                if not self.emergency_stop and self.command_sender:
                    # إرسال أوامر المحركات الحالية
                    self.command_sender(self.motor_speeds.copy())
                
                time.sleep(0.1)  # 10Hz control loop
                
            except Exception as e:
                self.logger.error(f"خطأ في حلقة التحكم: {e}")
    
    def set_manual_control(self, forward: float, strafe: float, vertical: float, yaw: float):
        """التحكم اليدوي المباشر
        
        Args:
            forward: حركة أمامي/خلفي (-100 إلى 100)
            strafe: حركة جانبية (-100 إلى 100)  
            vertical: حركة عمودية (-100 إلى 100)
            yaw: دوران (-100 إلى 100)
        """
        if self.emergency_stop:
            return
        
        # تطبيق حدود السرعة
        forward = max(-self.max_speed, min(self.max_speed, forward))
        strafe = max(-self.max_speed, min(self.max_speed, strafe))
        vertical = max(-self.max_speed, min(self.max_speed, vertical))
        yaw = max(-self.max_speed, min(self.max_speed, yaw))
        
        # حساب سرعات المحركات الأفقية (6DOF mixing)
        front_left = forward - strafe + yaw
        front_right = forward + strafe - yaw
        back_left = forward + strafe + yaw
        back_right = forward - strafe - yaw
        
        # تحويل إلى قيم PWM
        self.motor_speeds['front_left'] = self._scale_to_pwm(front_left)
        self.motor_speeds['front_right'] = self._scale_to_pwm(front_right)
        self.motor_speeds['back_left'] = self._scale_to_pwm(back_left)
        self.motor_speeds['back_right'] = self._scale_to_pwm(back_right)
        
        # المحركات العمودية
        self.motor_speeds['vertical_1'] = self._scale_to_pwm(vertical)
        self.motor_speeds['vertical_2'] = self._scale_to_pwm(vertical)
        
        self.logger.debug(f"تحكم يدوي: F={forward}, S={strafe}, V={vertical}, Y={yaw}")
    
    def set_position_control(self, target_x: float, target_y: float, target_z: float, target_yaw: float,
                           current_x: float, current_y: float, current_z: float, current_yaw: float):
        """التحكم في الموقع باستخدام PID"""
        if self.emergency_stop or not self.pid_controllers:
            return
        
        # حساب أوامر التحكم باستخدام PID
        x_command = self.pid_controllers['x'].update(target_x, current_x)
        y_command = self.pid_controllers['y'].update(target_y, current_y)
        z_command = self.pid_controllers['z'].update(target_z, current_z)
        yaw_command = self.pid_controllers['yaw'].update(target_yaw, current_yaw)
        
        # تطبيق أوامر التحكم
        self.set_manual_control(x_command, y_command, z_command, yaw_command)
        
        self.logger.debug(f"تحكم موقعي: X={x_command:.2f}, Y={y_command:.2f}, Z={z_command:.2f}, Yaw={yaw_command:.2f}")
    
    def set_motor_speed(self, motor_name: str, speed: float):
        """تعيين سرعة محرك محدد (-100 إلى 100)"""
        if motor_name in self.motor_speeds and not self.emergency_stop:
            speed = max(-100, min(100, speed))
            self.motor_speeds[motor_name] = self._scale_to_pwm(speed)
            self.logger.debug(f"تم تعديل سرعة {motor_name}: {speed}")
    
    def _scale_to_pwm(self, speed: float) -> int:
        """تحويل سرعة (-100 إلى 100) إلى قيمة PWM (1000 إلى 2000)"""
        if speed == 0:
            return self.neutral_pwm
        
        # تطبيق منحنى التسارع إذا لزم الأمر
        scaled_speed = speed * (self.max_pwm - self.neutral_pwm) / 100
        
        if speed > 0:
            pwm_value = self.neutral_pwm + scaled_speed
        else:
            pwm_value = self.neutral_pwm + scaled_speed
        
        # تطبيق الحدود
        return int(max(self.min_pwm, min(self.max_pwm, pwm_value)))
    
    def emergency_stop_all(self):
        """إيقاف طارئ لجميع المحركات"""
        self.emergency_stop = True
        
        # إعادة تعيين جميع المحركات للمحايد
        for motor in self.motor_speeds:
            self.motor_speeds[motor] = self.neutral_pwm
        
        # إرسال الأمر فوراً
        if self.command_sender:
            self.command_sender(self.motor_speeds.copy())
        
        self.logger.warning("تم تنفيذ الإيقاف الطارئ")
    
    def reset_emergency_stop(self):
        """إلغاء الإيقاف الطارئ"""
        self.emergency_stop = False
        self.logger.info("تم إلغاء الإيقاف الطارئ")
    
    def stop_all_motors(self):
        """إيقاف جميع المحركات (بدون إيقاف طارئ)"""
        for motor in self.motor_speeds:
            self.motor_speeds[motor] = self.neutral_pwm
        self.logger.info("تم إيقاف جميع المحركات")
    
    def apply_motor_calibration(self, calibration_data: Dict[str, Dict]):
        """تطبيق بيانات معايرة المحركات"""
        self.motor_calibration = calibration_data
        self.logger.info("تم تطبيق معايرة المحركات")
    
    def get_motor_status(self) -> Dict[str, Any]:
        """الحصول على حالة المحركات"""
        return {
            'speeds': self.motor_speeds.copy(),
            'emergency_stop': self.emergency_stop,
            'is_controlling': self.is_controlling,
            'max_speed': self.max_speed
        }
    
    def set_pid_parameters(self, axis: str, kp: float, ki: float, kd: float):
        """تعديل معاملات PID لمحور معين"""
        if self.pid_controllers and axis in self.pid_controllers:
            self.pid_controllers[axis].set_parameters(kp, ki, kd)
            self.logger.info(f"تم تحديث معاملات PID للمحور {axis}")
    
    def reset_pid_controllers(self):
        """إعادة تعيين جميع متحكمات PID"""
        if self.pid_controllers:
            for controller in self.pid_controllers.values():
                controller.reset()
            self.logger.info("تم إعادة تعيين متحكمات PID")
