import pygame
import threading
import time
from typing import Dict, Optional, Callable, List, Any
from utils.logger import ROVLogger

class JoystickInput:
    """فئة التحكم بالجويستيك/الغمباد"""
    
    def __init__(self):
        self.logger = ROVLogger('JoystickInput')
        self.joystick: Optional[pygame.joystick.Joystick] = None
        self.is_connected = False
        self.is_active = False
        
        # إعدادات الحساسية
        self.deadzone = 0.1  # المنطقة الميتة
        self.sensitivity = 1.0
        
        # مفاتيح التحكم
        self.button_mapping = {
            0: 'emergency_stop',    # A button
            1: 'lights_toggle',     # B button  
            2: 'camera_record',     # X button
            3: 'stabilize',         # Y button
            4: 'slow_mode',         # LB
            5: 'fast_mode',         # RB
            6: 'reset_heading',     # Back
            7: 'menu',              # Start
        }
        
        # معالجات الأحداث
        self.movement_handler: Optional[Callable] = None
        self.button_handler: Optional[Callable] = None
        
        # خيط قراءة الجويستيك
        self.input_thread: Optional[threading.Thread] = None
        
        # حالة الأزرار والمحاور
        self.button_states = {}
        self.axis_values = {}
        
        # تهيئة pygame
        try:
            pygame.init()
            pygame.joystick.init()
            self.logger.info("تم تهيئة نظام الجويستيك")
        except Exception as e:
            self.logger.error(f"خطأ في تهيئة pygame: {e}")
    
    def scan_joysticks(self) -> List[str]:
        """البحث عن الجويستيك المتاح"""
        joysticks = []
        try:
            pygame.joystick.quit()
            pygame.joystick.init()
            
            joystick_count = pygame.joystick.get_count()
            
            for i in range(joystick_count):
                joystick = pygame.joystick.Joystick(i)
                joysticks.append({
                    'id': i,
                    'name': joystick.get_name(),
                    'axes': joystick.get_numaxes(),
                    'buttons': joystick.get_numbuttons(),
                    'hats': joystick.get_numhats()
                })
            
            self.logger.info(f"تم العثور على {len(joysticks)} جويستيك")
            return joysticks
            
        except Exception as e:
            self.logger.error(f"خطأ في البحث عن الجويستيك: {e}")
            return []
    
    def connect_joystick(self, joystick_id: int = 0) -> bool:
        """الاتصال بجويستيك محدد"""
        try:
            if pygame.joystick.get_count() <= joystick_id:
                self.logger.error("الجويستيك المطلوب غير متاح")
                return False
            
            self.joystick = pygame.joystick.Joystick(joystick_id)
            self.joystick.init()
            
            self.is_connected = True
            
            self.logger.info(f"تم الاتصال بالجويستيك: {self.joystick.get_name()}")
            self.logger.info(f"المحاور: {self.joystick.get_numaxes()}, الأزرار: {self.joystick.get_numbuttons()}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"خطأ في الاتصال بالجويستيك: {e}")
            return False
    
    def disconnect_joystick(self):
        """قطع الاتصال بالجويستيك"""
        self.is_connected = False
        self.stop_input()
        
        if self.joystick:
            self.joystick.quit()
            self.joystick = None
        
        self.logger.info("تم قطع الاتصال بالجويستيك")
    
    def start_input(self):
        """بدء قراءة إدخال الجويستيك"""
        if not self.is_connected or self.is_active:
            return
        
        self.is_active = True
        self.input_thread = threading.Thread(target=self._input_loop, daemon=True)
        self.input_thread.start()
        
        self.logger.info("تم بدء قراءة إدخال الجويستيك")
    
    def stop_input(self):
        """إيقاف قراءة إدخال الجويستيك"""
        self.is_active = False
        
        if self.input_thread and self.input_thread.is_alive():
            self.input_thread.join(timeout=1)
        
        self.logger.info("تم إيقاف قراءة إدخال الجويستيك")
    
    def _input_loop(self):
        """حلقة قراءة إدخال الجويستيك"""
        clock = pygame.time.Clock()
        
        while self.is_active and self.is_connected:
            try:
                # معالجة أحداث pygame
                pygame.event.pump()
                
                # قراءة المحاور
                if self.joystick:
                    self._read_axes()
                    self._read_buttons()
                    self._process_input()
                
                clock.tick(60)  # 60 FPS
                
            except Exception as e:
                self.logger.error(f"خطأ في حلقة الإدخال: {e}")
                break
    
    def _read_axes(self):
        """قراءة قيم المحاور"""
        if not self.joystick:
            return
        
        try:
            # محاور التحكم الأساسية (Xbox Controller)
            axes = {
                'left_x': self._apply_deadzone(self.joystick.get_axis(0)),      # Left stick X
                'left_y': self._apply_deadzone(self.joystick.get_axis(1)),      # Left stick Y
                'right_x': self._apply_deadzone(self.joystick.get_axis(2)),     # Right stick X
                'right_y': self._apply_deadzone(self.joystick.get_axis(3)),     # Right stick Y
                'left_trigger': (self.joystick.get_axis(4) + 1) / 2,           # Left trigger (0-1)
                'right_trigger': (self.joystick.get_axis(5) + 1) / 2,          # Right trigger (0-1)
            }
            
            self.axis_values = axes
            
        except Exception as e:
            self.logger.error(f"خطأ في قراءة المحاور: {e}")
    
    def _read_buttons(self):
        """قراءة حالة الأزرار"""
        if not self.joystick:
            return
        
        try:
            for button_id in range(self.joystick.get_numbuttons()):
                button_state = self.joystick.get_button(button_id)
                
                # التحقق من تغيير الحالة
                if button_id not in self.button_states:
                    self.button_states[button_id] = False
                
                # إرسال حدث الضغط
                if button_state and not self.button_states[button_id]:
                    self._handle_button_press(button_id)
                
                # إرسال حدث الإفلات
                elif not button_state and self.button_states[button_id]:
                    self._handle_button_release(button_id)
                
                self.button_states[button_id] = button_state
                
        except Exception as e:
            self.logger.error(f"خطأ في قراءة الأزرار: {e}")
    
    def _apply_deadzone(self, value: float) -> float:
        """تطبيق المنطقة الميتة على قيمة المحور"""
        if abs(value) < self.deadzone:
            return 0.0
        
        # تطبيق منحنى الحساسية
        sign = 1 if value > 0 else -1
        normalized = (abs(value) - self.deadzone) / (1 - self.deadzone)
        
        return sign * normalized * self.sensitivity
    
    def _process_input(self):
        """معالجة الإدخال وإرسال أوامر الحركة"""
        if not self.movement_handler or not self.axis_values:
            return
        
        try:
            # تحويل إدخال الجويستيك إلى أوامر حركة
            # Left stick: forward/strafe
            forward = -self.axis_values.get('left_y', 0) * 100  # عكس Y
            strafe = self.axis_values.get('left_x', 0) * 100
            
            # Right stick: vertical/yaw
            vertical = -(self.axis_values.get('right_y', 0) * 100)  # عكس Y
            yaw = self.axis_values.get('right_x', 0) * 100
            
            # Triggers: تحكم إضافي في العمق
            left_trigger = self.axis_values.get('left_trigger', 0) * 100
            right_trigger = self.axis_values.get('right_trigger', 0) * 100
            
            # استخدام الـ triggers للتحكم في العمق إذا لم يستخدم اللاعب العصا اليمنى
            if abs(vertical) < 10:  # إذا لم تستخدم العصا اليمنى للعمق
                vertical = right_trigger - left_trigger
            
            # إرسال أوامر الحركة
            self.movement_handler(forward, strafe, vertical, yaw)
            
        except Exception as e:
            self.logger.error(f"خطأ في معالجة الإدخال: {e}")
    
    def _handle_button_press(self, button_id: int):
        """معالجة ضغط الزر"""
        button_name = self.button_mapping.get(button_id, f"button_{button_id}")
        
        self.logger.debug(f"تم ضغط الزر: {button_name}")
        
        if self.button_handler:
            self.button_handler(button_name, True)
    
    def _handle_button_release(self, button_id: int):
        """معالجة إفلات الزر"""
        button_name = self.button_mapping.get(button_id, f"button_{button_id}")
        
        if self.button_handler:
            self.button_handler(button_name, False)
    
    def set_movement_handler(self, handler: Callable[[float, float, float, float], None]):
        """تعيين معالج أوامر الحركة"""
        self.movement_handler = handler
    
    def set_button_handler(self, handler: Callable[[str, bool], None]):
        """تعيين معالج أحداث الأزرار"""
        self.button_handler = handler
    
    def set_deadzone(self, deadzone: float):
        """تعيين المنطقة الميتة"""
        self.deadzone = max(0.0, min(1.0, deadzone))
        self.logger.info(f"تم تعديل المنطقة الميتة: {self.deadzone}")
    
    def set_sensitivity(self, sensitivity: float):
        """تعيين الحساسية"""
        self.sensitivity = max(0.1, min(2.0, sensitivity))
        self.logger.info(f"تم تعديل الحساسية: {self.sensitivity}")
    
    def get_joystick_info(self) -> Dict[str, Any]:
        """الحصول على معلومات الجويستيك"""
        if not self.joystick:
            return {}
        
        return {
            'name': self.joystick.get_name(),
            'axes': self.joystick.get_numaxes(),
            'buttons': self.joystick.get_numbuttons(),
            'hats': self.joystick.get_numhats(),
            'connected': self.is_connected,
            'active': self.is_active,
            'deadzone': self.deadzone,
            'sensitivity': self.sensitivity
        }
    
    def calibrate(self):
        """معايرة الجويستيك"""
        self.logger.info("بدء معايرة الجويستيك...")
        
        # معايرة بسيطة - يمكن توسيعها
        if self.joystick:
            # قراءة القيم الحالية كنقطة مرجعية
            center_values = {}
            for i in range(self.joystick.get_numaxes()):
                center_values[i] = self.joystick.get_axis(i)
            
            self.logger.info(f"تم حفظ القيم المرجعية: {center_values}")
        
        self.logger.info("تمت معايرة الجويستيك")
