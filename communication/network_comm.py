import socket
import threading
import json
import time
from typing import Optional, Callable, Dict, Any
from utils.logger import ROVLogger

class NetworkCommunication:
    """فئة الاتصال الشبكي مع ROV (TCP/UDP)"""
    
    def __init__(self, host: str = "192.168.1.100", port: int = 8080, protocol: str = "TCP"):
        self.host = host
        self.port = port
        self.protocol = protocol.upper()
        self.socket_connection: Optional[socket.socket] = None
        self.is_connected = False
        self.logger = ROVLogger('NetworkComm')
        
        # معالج البيانات الواردة
        self.data_handler: Optional[Callable] = None
        
        # خيط قراءة البيانات
        self.read_thread: Optional[threading.Thread] = None
        self.is_reading = False
        
        # خيط خادم UDP (للاستماع)
        self.server_thread: Optional[threading.Thread] = None
        self.is_server_running = False
    
    def connect(self) -> bool:
        """الاتصال بـ ROV عبر الشبكة"""
        try:
            if self.protocol == "TCP":
                return self._connect_tcp()
            elif self.protocol == "UDP":
                return self._connect_udp()
            else:
                self.logger.error(f"بروتوكول غير مدعوم: {self.protocol}")
                return False
                
        except Exception as e:
            self.logger.error(f"خطأ في الاتصال الشبكي: {e}")
            return False
    
    def _connect_tcp(self) -> bool:
        """اتصال TCP"""
        try:
            self.socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_connection.settimeout(10)  # مهلة زمنية للاتصال
            
            self.socket_connection.connect((self.host, self.port))
            self.is_connected = True
            
            self.logger.info(f"تم الاتصال TCP بنجاح إلى {self.host}:{self.port}")
            
            # بدء خيط قراءة البيانات
            self._start_reading()
            return True
            
        except socket.timeout:
            self.logger.error("انتهت المهلة الزمنية للاتصال")
            return False
        except ConnectionRefusedError:
            self.logger.error("تم رفض الاتصال")
            return False
        except Exception as e:
            self.logger.error(f"خطأ في اتصال TCP: {e}")
            return False
    
    def _connect_udp(self) -> bool:
        """اتصال UDP"""
        try:
            self.socket_connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.is_connected = True
            
            self.logger.info(f"تم إعداد اتصال UDP إلى {self.host}:{self.port}")
            
            # بدء خادم UDP للاستماع
            self._start_udp_server()
            return True
            
        except Exception as e:
            self.logger.error(f"خطأ في اتصال UDP: {e}")
            return False
    
    def disconnect(self):
        """قطع الاتصال"""
        self.is_connected = False
        self.is_reading = False
        self.is_server_running = False
        
        # انتظار انتهاء الخيوط
        if self.read_thread and self.read_thread.is_alive():
            self.read_thread.join(timeout=2)
        
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(timeout=2)
        
        if self.socket_connection:
            self.socket_connection.close()
            self.logger.info("تم قطع الاتصال الشبكي")
    
    def send_data(self, data: Dict[str, Any]) -> bool:
        """إرسال البيانات إلى ROV"""
        if not self.is_connected or not self.socket_connection:
            self.logger.warning("لا يوجد اتصال - لا يمكن إرسال البيانات")
            return False
        
        try:
            # تحويل البيانات إلى JSON
            json_data = json.dumps(data)
            
            if self.protocol == "TCP":
                # إرسال البيانات مع طول الرسالة
                message = json_data.encode('utf-8')
                length = len(message)
                self.socket_connection.sendall(length.to_bytes(4, byteorder='big') + message)
            
            elif self.protocol == "UDP":
                # إرسال البيانات UDP
                message = json_data.encode('utf-8')
                self.socket_connection.sendto(message, (self.host, self.port))
            
            self.logger.debug(f"تم إرسال البيانات: {data}")
            return True
            
        except Exception as e:
            self.logger.error(f"خطأ في إرسال البيانات: {e}")
            return False
    
    def send_motor_commands(self, motors: Dict[str, int]) -> bool:
        """إرسال أوامر المحركات"""
        command_data = {
            "type": "motor_command",
            "motors": motors,
            "timestamp": time.time()
        }
        return self.send_data(command_data)
    
    def request_telemetry(self) -> bool:
        """طلب بيانات التيليمتري"""
        request_data = {
            "type": "telemetry_request",
            "timestamp": time.time()
        }
        return self.send_data(request_data)
    
    def emergency_stop(self) -> bool:
        """إيقاف طارئ"""
        self.logger.warning("تم تنفيذ إيقاف طارئ!")
        emergency_data = {
            "type": "emergency_stop",
            "timestamp": time.time()
        }
        return self.send_data(emergency_data)
    
    def _start_reading(self):
        """بدء خيط قراءة البيانات TCP"""
        if self.protocol == "TCP" and not self.is_reading:
            self.is_reading = True
            self.read_thread = threading.Thread(target=self._read_tcp_data, daemon=True)
            self.read_thread.start()
    
    def _start_udp_server(self):
        """بدء خادم UDP للاستماع"""
        if self.protocol == "UDP" and not self.is_server_running:
            self.is_server_running = True
            self.server_thread = threading.Thread(target=self._udp_server, daemon=True)
            self.server_thread.start()
    
    def _read_tcp_data(self):
        """قراءة البيانات TCP"""
        while self.is_reading and self.is_connected:
            try:
                # قراءة طول الرسالة (4 بايت)
                length_bytes = self.socket_connection.recv(4)
                if not length_bytes:
                    break
                
                message_length = int.from_bytes(length_bytes, byteorder='big')
                
                # قراءة الرسالة كاملة
                message = b''
                while len(message) < message_length:
                    chunk = self.socket_connection.recv(message_length - len(message))
                    if not chunk:
                        break
                    message += chunk
                
                if message:
                    data_str = message.decode('utf-8')
                    self.logger.debug(f"بيانات TCP واردة: {data_str}")
                    
                    # معالجة البيانات
                    if self.data_handler:
                        try:
                            data = json.loads(data_str)
                            self.data_handler(data)
                        except json.JSONDecodeError:
                            self.data_handler(data_str)
                
            except Exception as e:
                self.logger.error(f"خطأ في قراءة بيانات TCP: {e}")
                break
    
    def _udp_server(self):
        """خادم UDP للاستماع للبيانات الواردة"""
        listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        listen_socket.bind(('', self.port + 1))  # استخدام منفذ مختلف للاستماع
        listen_socket.settimeout(1)
        
        self.logger.info(f"بدء خادم UDP على المنفذ {self.port + 1}")
        
        while self.is_server_running:
            try:
                data, addr = listen_socket.recvfrom(4096)
                data_str = data.decode('utf-8')
                
                self.logger.debug(f"بيانات UDP واردة من {addr}: {data_str}")
                
                # معالجة البيانات
                if self.data_handler:
                    try:
                        data_obj = json.loads(data_str)
                        self.data_handler(data_obj)
                    except json.JSONDecodeError:
                        self.data_handler(data_str)
                        
            except socket.timeout:
                continue
            except Exception as e:
                self.logger.error(f"خطأ في خادم UDP: {e}")
                break
        
        listen_socket.close()
    
    def set_data_handler(self, handler: Callable):
        """تعيين معالج البيانات الواردة"""
        self.data_handler = handler
    
    def ping(self) -> bool:
        """اختبار الاتصال"""
        ping_data = {
            "type": "ping",
            "timestamp": time.time()
        }
        return self.send_data(ping_data)
