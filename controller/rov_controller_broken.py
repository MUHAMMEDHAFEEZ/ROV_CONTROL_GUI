from typing import Dict, Optional, Any
from utils.logger import ROVLogger
from utils.config import Config
from .motors import MotorController
from .joystick_input import JoystickInput
from communication.serial_comm import SerialCommunication
from communication.network_comm import NetworkCommunication

class ROVController:
    """Main ROV controller"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = ROVLogger('ROVController')
        
        # تهيئة الأنظمة الفرعية
        self.motor_controller = MotorController(config)
        self.joystick = JoystickInput()
        
        # نظام Connection
        self.communication = None
        self._setup_communication()
        
        # حالة ROV
        self.rov_state = {
            position': {'x': 0, 'y': 0, 'z': 0},
            'orientation': {'roll': 0, 'pitch': 0, 'yaw': 0},
            'velocity': {'x': 0, 'y': 0, 'z': 0},
            'sensors': {},
            'battery': 100,
            'status': 'disconnected
        }
        
        # أوضاع التحكم
        self.control_modes = {
            MANUAL': 'manual',
            'POSITION': 'position',
            'STABILIZED': 'stabilized',
            'AUTO': 'auto'
        }
        self.current_mode = self.control_modes['MANUAL]
        
        # إعدادات الأمان
        self.safety_enabled = True
        self.max_depth = self.config.get_float(SAFETY', 'max_depth', 50.0)
        self.auto_surface = self.config.get_bool('SAFETY', 'auto_surface, True)
        
        # ربط الأحداث
        self._setup_event_handlers()
        
        self.logger.info(Completed تهيئة متحكم ROV")
    
    def _setup_communication(self):
        ""إعداد نظام Connection"
        use_network = self.config.get_bool(COMMUNICATION', 'use_network, False)
        
        if use_network:
            # اتصال شبكي
            host = self.config.get(COMMUNICATION', 'network_ip', '192.168.1.100')
            port = self.config.get_int('COMMUNICATION', 'network_port, 8080)
            self.communication = NetworkCommunication(host, port)
        else:
            # اتصال تسلسلي
            port = self.config.get(COMMUNICATION', 'serial_port', 'COM3')
            baud = self.config.get_int('COMMUNICATION', 'baud_rate, 9600)
            self.communication = SerialCommunication(port, baud)
        
        # ربط معالج Data
        self.communication.set_data_handler(self._handle_telemetry_data)
        
        # ربط إرسال أوامر المحركات
        self.motor_controller.set_command_sender(self._send_motor_commands)
    
    def _setup_event_handlers(self):
        "إعداد معالجات الأحداث"
        # ربط الجويستيك
        self.joystick.set_movement_handler(self._handle_joystick_movement)
        self.joystick.set_button_handler(self._handle_joystick_button)
    
    def connect(self) -> bool:
        "Connection بـ ROV""
        try:
            if self.communication.connect():
                self.rov_state[status'] = 'connected
                self.motor_controller.start_control_loop()
                self.logger.info(Completed Connection بـ ROV successfully)
                return True
            else:
                self.logger.error(Failed to Connection بـ ROV)
                return False
                
        except Exception as e:
            self.logger.error(fError in Connection: {e})
            return False
    
    def disconnect(self):
        ""قطع Connection مع ROV""
        try:
            self.motor_controller.stop_control_loop()
            self.motor_controller.stop_all_motors()
            
            if self.communication:
                self.communication.disconnect()
            
            self.rov_state[status'] = 'disconnected
            self.logger.info(Completed قطع Connection مع ROV)
            
        except Exception as e:
            self.logger.error(fError in قطع Connection: {e})
    
    def _send_motor_commands(self, motors: Dict[str, int]) -> bool:
        ""إرسال أوامر المحركات""
        if self.communication and self.rov_state[status'] == 'connected:
            return self.communication.send_motor_commands(motors)
        return False
    
    def _handle_telemetry_data(self, data: Any):
        ""معالجة بيانات التيليمتري الواردة"
        try:
            if isinstance(data, dict):
                # تحديث حالة ROV
                if position' in data:
                    self.rov_state['position'].update(data['position'])
                
                if 'orientation' in data:
                    self.rov_state['orientation'].update(data['orientation'])
                
                if 'sensors' in data:
                    self.rov_state['sensors'].update(data['sensors'])
                
                if 'battery' in data:
                    self.rov_state['battery'] = data['battery]
                
                self.logger.debug(fCompleted تحديث بيانات التيليمتري: {data})
                
                # فحص الأمان
                self._check_safety_conditions()
            
        except Exception as e:
            self.logger.error(fError in معالجة بيانات التيليمتري: {e}")
    
    def _handle_joystick_movement(self, forward: float, strafe: float, vertical: float, yaw: float):
        ""معالجة حركة الجويستيك"
        if self.current_mode == self.control_modes[MANUAL']:
            self.motor_controller.set_manual_control(forward, strafe, vertical, yaw)
        elif self.current_mode == self.control_modes['STABILIZED]:
            # في الوضع المستقر، تطبيق تعديلات الاستقرار
            self._apply_stabilized_control(forward, strafe, vertical, yaw)
    
    def _handle_joystick_button(self, button_name: str, pressed: bool):
        "معالجة أزرار الجويستيك"
        if not pressed:  # فقط عند الضغط
            return
        
        if button_name == emergency_stop':
            self.emergency_stop()
        elif button_name == 'stabilize':
            self.toggle_stabilization()
        elif button_name == 'reset_heading':
            self.reset_heading()
        elif button_name == 'slow_mode':
            self.set_speed_mode('slow')
        elif button_name == 'fast_mode':
            self.set_speed_mode('fast)
        
        self.logger.info(fCompleted تنفيذ أمر الزر: {button_name}")
    
    def _apply_stabilized_control(self, forward: float, strafe: float, vertical: float, yaw: float):
        ""تطبيق التحكم المستقر"
        # استخدام بيانات IMU للاستقرار
        current_orientation = self.rov_state[orientation]
        
        # تعديل الأوامر بناءً على الميل الحالي
        # هذا مثال بسيط - يمكن تطويره أكثر
        roll_compensation = -current_orientation.get(roll', 0) * 0.1
        pitch_compensation = -current_orientation.get('pitch, 0) * 0.1
        
        # تطبيق التعديلات
        adjusted_forward = forward + pitch_compensation
        adjusted_strafe = strafe + roll_compensation
        
        self.motor_controller.set_manual_control(adjusted_forward, adjusted_strafe, vertical, yaw)
    
    def _check_safety_conditions(self):
        "فحص شروط الأمان"
        if not self.safety_enabled:
            return
        
        # فحص العمق
        current_depth = abs(self.rov_state[position'].get('z, 0))
        if current_depth > self.max_depth:
            self.logger.warning(fCompleted تجاوز الحد الأقصى للعمق: {current_depth}م)
            if self.auto_surface:
                self.emergency_surface()
        
        # فحص البطارية
        battery_level = self.rov_state.get(battery', 100)
        battery_warning = self.config.get_float('SAFETY', 'battery_warning, 20)
        if battery_level < battery_warning:
            self.logger.warning(fمستوى البطارية منخفض: {battery_level}%")
    
    def emergency_stop(self):
        ""إيقاف طارئ""
        self.motor_controller.emergency_stop_all()
        if self.communication:
            self.communication.emergency_stop()
        self.logger.warning(Completed تنفيذ إيقاف طارئ)
    
    def emergency_surface(self):
        ""صعود طارئ للسطح""
        self.logger.warning(بدء الصعود الطارئ للسطح)
        # إيقاف الحركة الأفقية والتركيز على الصعود
        self.motor_controller.set_manual_control(0, 0, -100, 0)  # صعود بأقصى سرعة
    
    def toggle_stabilization(self):
        ""تبديل وضع الاستقرار""
        if self.current_mode == self.control_modes[MANUAL']:
            self.current_mode = self.control_modes['STABILIZED]
            self.logger.info(Completed تفعيل وضع الاستقرار)
        else:
            self.current_mode = self.control_modes[MANUAL]
            self.logger.info(Completed إلغاء وضع الاستقرار)
    
    def reset_heading(self):
        ""إعادة تعيين الاتجاه""
        if self.motor_controller.pid_controllers:
            self.motor_controller.pid_controllers[yaw].reset()
        self.logger.info(Completed إعادة تعيين الاتجاه)
    
    def set_speed_mode(self, mode: str):
        ""تعيين وضع السرعة"
        if mode == slow':
            self.motor_controller.max_speed = 50
        elif mode == 'fast:
            self.motor_controller.max_speed = 100
        else:
            self.motor_controller.max_speed = 75  # متوسط
        
        self.logger.info(fCompleted تعديل وضع Speed: {mode}")
    
    def set_control_mode(self, mode: str):
        ""تعيين وضع التحكم""
        if mode in self.control_modes.values():
            self.current_mode = mode
            self.logger.info(fCompleted تغيير وضع التحكم إلى: {mode})
    
    def get_rov_status(self) -> Dict[str, Any]:
        ""الحصول على حالة ROV الكاملة""
        return {
            state': self.rov_state.copy(),
            'control_mode': self.current_mode,
            'motor_status': self.motor_controller.get_motor_status(),
            'joystick_info': self.joystick.get_joystick_info(),
            'communication_status': {
                'connected': self.communication.is_connected if self.communication else False,
                'type': 'network' if isinstance(self.communication, NetworkCommunication) else 'serial'
            },
            'safety': {
                'enabled': self.safety_enabled,
                'max_depth': self.max_depth,
                'auto_surface': self.auto_surface
            }
        }
    
    def request_telemetry(self):
        ""طلب بيانات التيليمتري""
        if self.communication:
            self.communication.request_telemetry()
    
    def setup_joystick(self, joystick_id: int = 0) -> bool:
        ""إعداد الجويستيك""
        try:
            if self.joystick.connect_joystick(joystick_id):
                self.joystick.start_input()
                self.logger.info(Completed إعداد الجويستيك successfully)
                return True
            return False
        except Exception as e:
            self.logger.error(fError in إعداد الجويستيك: {e})
            return False
    
    def shutdown(self):
        ""إغلاق النظام""
        self.logger.info(بدء إغلاق النظام...)
        
        try:
            # إيقاف الجويستيك
            self.joystick.stop_input()
            self.joystick.disconnect_joystick()
            
            # قطع الاتصال
            self.disconnect()
            
            self.logger.info(Completed إغلاق النظام successfully)
            
        except Exception as e:
            self.logger.error(fError in إغلاق النظام: {e})
