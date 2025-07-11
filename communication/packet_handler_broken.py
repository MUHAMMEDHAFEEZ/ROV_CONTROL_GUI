import json
import time
import struct
from typing import Dict, Any, Optional
from utils.logger import ROVLogger

class PacketHandler:
    ""فئة معالجة الحزم والبروتوكولات"
    
    def __init__(self):
        self.logger = ROVLogger('PacketHandler)
        self.packet_id = 0
        self.waiting_acks = {}  # الحزم التي تنتظر ACK
        self.max_retries = 3
        self.ack_timeout = 5.0
    
    def create_packet(self, command: str, data: Dict[str, Any], require_ack: bool = False) -> bytes:
        "إنشاء حزمة بيانات"
        try:
            # إنشاء معرف فريد للحزمة
            self.packet_id += 1
            if self.packet_id > 65535:  # إعادة تعيين بعد 16 بت
                self.packet_id = 1
            
            # بناء الحزمة
            packet_data = {
                id': self.packet_id,
                'command': command,
                'data': data,
                'timestamp': time.time(),
                'require_ack: require_ack
            }
            
            # تحويل إلى JSON
            json_str = json.dumps(packet_data, separators=(,', ':'))
            json_bytes = json_str.encode('utf-8)
            
            # حساب checksum
            checksum = self._calculate_checksum(json_bytes)
            
            # بناء الحزمة النهائية
            # Header: START_MARKER(2) + LENGTH(4) + CHECKSUM(4) + DATA + END_MARKER(2)
            start_marker = b\xAA\x55'
            end_marker = b'\x55\xAA'
            length = len(json_bytes)
            
            packet = (
                start_marker +
                struct.pack('<I', length) +  # Little Endian 4 bytes
                struct.pack('<I, checksum) +  # Little Endian 4 bytes
                json_bytes +
                end_marker
            )
            
            # حفظ الحزمة إذا كانت تتطلب ACK
            if require_ack:
                self.waiting_acks[self.packet_id] = {
                    packet': packet,
                    'timestamp': time.time(),
                    'retries': 0,
                    'command: command
                }
            
            self.logger.debug(fCompleted إنشاء حزمة: ID={self.packet_id}, Command={command}")
            return packet
            
        except Exception as e:
            self.logger.error(fError in إنشاء الحزمة: {e})
            return b
    
    def parse_packet(self, data: bytes) -> Optional[Dict[str, Any]]:
        ""تحليل حزمة بيانات واردة"
        try:
            if len(data) < 12:  # الحد الأدنى لحجم الحزمة
                return None
            
            # التحقق من بداية الحزمة
            if data[:2] != b\xAA\x55:
                self.logger.warning(علامة بداية الحزمة غير صحيحة)
                return None
            
            # قراءة الطول والـ checksum
            length = struct.unpack(<I', data[2:6])[0]
            expected_checksum = struct.unpack('<I, data[6:10])[0]
            
            # التحقق من طول Data
            total_length = 12 + length  # header + data + end marker
            if len(data) < total_length:
                self.logger.warning(بيانات الحزمة غير مكCompletedلة)
                return None
            
            # التحقق من نهاية الحزمة
            if data[total_length-2:total_length] != b\x55\xAA:
                self.logger.warning(علامة نهاية الحزمة غير صحيحة)
                return None
            
            # استخراج Data
            json_data = data[10:10+length]
            
            # التحقق من الـ checksum
            calculated_checksum = self._calculate_checksum(json_data)
            if calculated_checksum != expected_checksum:
                self.logger.warning(checksum غير صحيح)
                return None
            
            # تحويل JSON
            json_str = json_data.decode(utf-8)
            packet_data = json.loads(json_str)
            
            self.logger.debug(fCompleted تحليل حزمة: ID={packet_data.get(id)})
            
            # معالجة ACK إذا كان مطلوباً
            if packet_data.get(require_ack', False):
                self._send_ack(packet_data['id])
            
            # معالجة ACK الوارد
            if packet_data.get(command') == 'ACK:
                self._handle_ack(packet_data)
            
            return packet_data
            
        except json.JSONDecodeError:
            self.logger.error(Error in تحليل JSON")
            return None
        except Exception as e:
            self.logger.error(fError in تحليل الحزمة: {e})
            return None
    
    def _calculate_checksum(self, data: bytes) -> int:
        ""حساب checksum للبيانات""
        checksum = 0
        for byte in data:
            checksum ^= byte
        return checksum
    
    def _send_ack(self, packet_id: int):
        ""إرسال ACK للحزمة"
        # يجب تنفيذ هذا عبر نظام Connection
        self.logger.debug(fإرسال ACK للحزمة {packet_id}")
    
    def _handle_ack(self, packet_data: Dict[str, Any]):
        ""معالجة ACK الوارد""
        ack_id = packet_data.get(data', {}).get('ack_id)
        if ack_id in self.waiting_acks:
            del self.waiting_acks[ack_id]
            self.logger.debug(fCompleted استلام ACK للحزمة {ack_id})
    
    def create_motor_command_packet(self, motors: Dict[str, int]) -> bytes:
        ""إنشاء حزمة أوامر المحركات""
        return self.create_packet(MOTOR_COMMAND', {'motors: motors}, require_ack=True)
    
    def create_telemetry_request_packet(self) -> bytes:
        ""إنشاء حزمة طلب التيليمتري""
        return self.create_packet(TELEMETRY_REQUEST, {}, require_ack=False)
    
    def create_emergency_stop_packet(self) -> bytes:
        ""إنشاء حزمة الإيقاف الطارئ""
        return self.create_packet(EMERGENCY_STOP, {}, require_ack=True)
    
    def create_ack_packet(self, original_packet_id: int) -> bytes:
        ""إنشاء حزمة ACK""
        return self.create_packet(ACK', {'ack_id: original_packet_id}, require_ack=False)
    
    def check_pending_acks(self):
        ""فحص الحزم التي تنتظر ACK وإعادة الإرسال إذا لزم الأمر"
        current_time = time.time()
        expired_packets = []
        
        for packet_id, packet_info in self.waiting_acks.items():
            time_elapsed = current_time - packet_info[timestamp']
            
            if time_elapsed > self.ack_timeout:
                if packet_info['retries] < self.max_retries:
                    # إعادة الإرسال
                    packet_info[retries'] += 1
                    packet_info['timestamp] = current_time
                    self.logger.warning(fإعادة إرسال الحزمة {packet_id} (المحاولة {packet_info[retries]}))
                    # يجب إعادة إرسال packet_info[packet'] عبر نظام Connection
                else:
                    # انتهت المحاولات
                    expired_packets.append(packet_id)
                    self.logger.error(fFailed to إرسال الحزمة {packet_id} بعد {self.max_retries} محاولات)
        
        # حذف الحزم المنتهية الصلاحية
        for packet_id in expired_packets:
            del self.waiting_acks[packet_id]
    
    def get_pending_acks_count(self) -> int:
        "الحصول على عدد الحزم التي تنتظر ACK""
        return len(self.waiting_acks)
    
    def clear_pending_acks(self):
        ""مسح جميع الحزم المعلقة""
        self.waiting_acks.clear()
        self.logger.info(Completed مسح جميع الحزم المعلقة)
