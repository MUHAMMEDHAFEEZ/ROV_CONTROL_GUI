import serial
import time
import threading
from typing import Optional, Callable, Dict, Any
from utils.logger import ROVLogger

class SerialCommunication:
    """فئة الاتصال التسلسلي مع ROV"""
    
    def __init__(self, port: str = "COM3", baud_rate: int = 9600, timeout: float = 5.0):
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.serial_connection: Optional[serial.Serial] = None
        self.is_connected = False
        self.logger = ROVLogger('SerialComm')
        
        # معالج البيانات الواردة
        self.data_handler: Optional[Callable] = None
        
        # خيط قراءة البيانات
        self.read_thread: Optional[threading.Thread] = None
        self.is_reading = False
        
    def connect(self) -> bool:
        """الاتصال بـ ROV عبر المنفذ التسلسلي"""
        try:
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                timeout=self.timeout,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS
            )
            
            if self.serial_connection.is_open:
                self.is_connected = True
                self.logger.info(f"تم الاتصال بنجاح عبر {self.port} بسرعة {self.baud_rate}")
                
                # بدء خيط قراءة البيانات
                self._start_reading()
                return True
            else:
                self.logger.error("فشل في فتح المنفذ التسلسلي")
                return False
                
        except serial.SerialException as e:
            self.logger.error(f"خطأ في الاتصال التسلسلي: {e}")
            self.is_connected = False
            return False
        except Exception as e:
            self.logger.error(f"خطأ غير متوقع: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """قطع الاتصال"""
        self.is_connected = False
        self.is_reading = False
        
        if self.read_thread and self.read_thread.is_alive():
            self.read_thread.join(timeout=2)
        
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            self.logger.info("تم قطع الاتصال التسلسلي")
    
    def send_command(self, command: str) -> bool:
        """إرسال أمر إلى ROV"""
        if not self.is_connected or not self.serial_connection:
            self.logger.warning("لا يوجد اتصال - لا يمكن إرسال الأمر")
            return False
        
        try:
            # إضافة خط جديد في نهاية الأمر
            command_bytes = (command + '\n').encode('utf-8')
            self.serial_connection.write(command_bytes)
            self.serial_connection.flush()
            
            self.logger.debug(f"تم إرسال الأمر: {command}")
            return True
            
        except Exception as e:
            self.logger.error(f"خطأ في إرسال الأمر: {e}")
            return False
    
    def send_motor_commands(self, motors: Dict[str, int]) -> bool:
        """إرسال أوامر المحركات"""
        try:
            # تكوين أمر المحركات
            # صيغة: MOTOR,front_left,front_right,back_left,back_right,vertical_1,vertical_2
            command = "MOTOR"
            motor_order = ['front_left', 'front_right', 'back_left', 'back_right', 'vertical_1', 'vertical_2']
            
            for motor in motor_order:
                speed = motors.get(motor, 1500)  # القيمة الافتراضية (محايد)
                command += f",{speed}"
            
            return self.send_command(command)
            
        except Exception as e:
            self.logger.error(f"خطأ في إرسال أوامر المحركات: {e}")
            return False
    
    def request_telemetry(self) -> bool:
        """طلب بيانات التيليمتري"""
        return self.send_command("GET_TELEMETRY")
    
    def emergency_stop(self) -> bool:
        """إيقاف طارئ"""
        self.logger.warning("تم تنفيذ إيقاف طارئ!")
        return self.send_command("EMERGENCY_STOP")
    
    def _start_reading(self):
        """بدء خيط قراءة البيانات"""
        if not self.is_reading:
            self.is_reading = True
            self.read_thread = threading.Thread(target=self._read_data, daemon=True)
            self.read_thread.start()
    
    def _read_data(self):
        """قراءة البيانات الواردة من ROV"""
        while self.is_reading and self.is_connected:
            try:
                if self.serial_connection and self.serial_connection.in_waiting > 0:
                    # قراءة خط كامل
                    line = self.serial_connection.readline().decode('utf-8').strip()
                    
                    if line:
                        self.logger.debug(f"بيانات واردة: {line}")
                        
                        # معالجة البيانات
                        if self.data_handler:
                            self.data_handler(line)
                
                time.sleep(0.01)  # تجنب استهلاك المعالج بشكل مفرط
                
            except Exception as e:
                self.logger.error(f"خطأ في قراءة البيانات: {e}")
                break
    
    def set_data_handler(self, handler: Callable[[str], None]):
        """تعيين معالج البيانات الواردة"""
        self.data_handler = handler
    
    def get_available_ports(self) -> list:
        """الحصول على قائمة المنافذ المتاحة"""
        import serial.tools.list_ports
        
        ports = []
        for port in serial.tools.list_ports.comports():
            ports.append({
                'device': port.device,
                'description': port.description,
                'hwid': port.hwid
            })
        
        return ports
    
    def test_connection(self) -> bool:
        """اختبار الاتصال"""
        if not self.is_connected:
            return False
        
        try:
            # إرسال أمر اختبار
            self.send_command("PING")
            
            # انتظار الرد (يجب تنفيذ آلية انتظار الرد)
            time.sleep(0.5)
            
            return True
            
        except Exception as e:
            self.logger.error(f"فشل في اختبار الاتصال: {e}")
            return False
