from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QGroupBox, QProgressBar, QSlider, QCheckBox,
    QComboBox, QSpinBox, QDoubleSpinBox, QGridLayout
)
from PyQt6.QtCore import QTimer, pyqtSignal, Qt
from PyQt6.QtGui import QPixmap, QFont, QImage
import cv2
import numpy as np
from typing import Optional

class CameraFeedWidget(QWidget):
    """أداة عرض الكاميرا والفيديو"""
    
    # إشارات مخصصة
    recording_status_changed = pyqtSignal(bool)
    snapshot_taken = pyqtSignal(str)
    
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.is_recording = False
        self.video_writer = None
        self.frame_count = 0
        
        # إعدادات الكاميرا
        self.camera_resolution = self.config.get('GUI', 'camera_resolution', '640x480')
        self.fps = self.config.get_int('GUI', 'fps', 30)
        
        self._setup_ui()
        self._setup_camera()
        
        # مؤقت تحديث الإطارات
        self.frame_timer = QTimer()
        self.frame_timer.timeout.connect(self._update_frame)
        self.frame_timer.start(1000 // self.fps)  # تحديث بناءً على FPS
    
    def _setup_ui(self):
        """إعداد واجهة المستخدم"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # عنوان
        title_label = QLabel("عرض الكاميرا")
        title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # إطار الفيديو
        self.video_frame = QLabel()
        self.video_frame.setMinimumSize(640, 480)
        self.video_frame.setStyleSheet("""
            QLabel {
                border: 2px solid #555555;
                background-color: #000000;
                color: #ffffff;
            }
        """)
        self.video_frame.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_frame.setText("لا يوجد إشارة فيديو")
        layout.addWidget(self.video_frame)
        
        # أدوات التحكم في الكاميرا
        controls_layout = self._create_camera_controls()
        layout.addLayout(controls_layout)
        
        # معلومات الكاميرا
        info_layout = self._create_camera_info()
        layout.addLayout(info_layout)
    
    def _create_camera_controls(self) -> QHBoxLayout:
        """إنشاء أدوات التحكم في الكاميرا"""
        layout = QHBoxLayout()
        
        # زر التسجيل
        self.record_button = QPushButton("بدء التسجيل")
        self.record_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        self.record_button.clicked.connect(self._toggle_recording)
        layout.addWidget(self.record_button)
        
        # زر لقطة
        snapshot_button = QPushButton("لقطة")
        snapshot_button.clicked.connect(self._take_snapshot)
        layout.addWidget(snapshot_button)
        
        # إعدادات الجودة
        quality_label = QLabel("الجودة:")
        layout.addWidget(quality_label)
        
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["منخفضة", "متوسطة", "عالية", "فائقة"])
        self.quality_combo.setCurrentIndex(2)  # عالية
        self.quality_combo.currentTextChanged.connect(self._change_quality)
        layout.addWidget(self.quality_combo)
        
        # تبديل الإضاءة
        self.lights_checkbox = QCheckBox("الإضاءة")
        self.lights_checkbox.toggled.connect(self._toggle_lights)
        layout.addWidget(self.lights_checkbox)
        
        layout.addStretch()
        return layout
    
    def _create_camera_info(self) -> QHBoxLayout:
        """إنشاء معلومات الكاميرا"""
        layout = QHBoxLayout()
        
        # FPS
        self.fps_label = QLabel("FPS: --")
        layout.addWidget(self.fps_label)
        
        # الدقة
        self.resolution_label = QLabel(f"الدقة: {self.camera_resolution}")
        layout.addWidget(self.resolution_label)
        
        # عداد الإطارات
        self.frame_count_label = QLabel("الإطارات: 0")
        layout.addWidget(self.frame_count_label)
        
        # حالة التسجيل
        self.recording_status = QLabel("غير مسجل")
        self.recording_status.setStyleSheet("color: #6c757d;")
        layout.addWidget(self.recording_status)
        
        layout.addStretch()
        return layout
    
    def _setup_camera(self):
        """إعداد الكاميرا"""
        try:
            # محاولة فتح الكاميرا (0 للكاميرا الافتراضية)
            self.camera = cv2.VideoCapture(0)
            
            if self.camera.isOpened():
                # تعيين دقة الكاميرا
                width, height = map(int, self.camera_resolution.split('x'))
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
                self.camera.set(cv2.CAP_PROP_FPS, self.fps)
                
                self.camera_available = True
            else:
                self.camera_available = False
                self._show_no_camera_message()
                
        except Exception as e:
            print(f"خطأ في إعداد الكاميرا: {e}")
            self.camera_available = False
            self._show_no_camera_message()
    
    def _show_no_camera_message(self):
        """إظهار رسالة عدم توفر الكاميرا"""
        self.video_frame.setText("الكاميرا غير متاحة\\nسيتم عرض محاكاة")
        self.camera_available = False
    
    def _update_frame(self):
        """تحديث إطار الفيديو"""
        if self.camera_available and self.camera.isOpened():
            ret, frame = self.camera.read()
            if ret:
                self._display_frame(frame)
            else:
                self._show_no_camera_message()
        else:
            # محاكاة إطار فيديو
            frame = self._generate_demo_frame()
            self._display_frame(frame)
        
        # تحديث عداد الإطارات
        self.frame_count += 1
        self.frame_count_label.setText(f"الإطارات: {self.frame_count}")
        
        # حفظ الإطار إذا كان التسجيل مفعلاً
        if self.is_recording and self.video_writer:
            self.video_writer.write(frame)
    
    def _generate_demo_frame(self) -> np.ndarray:
        """إنشاء إطار تجريبي للمحاكاة"""
        width, height = map(int, self.camera_resolution.split('x'))
        
        # إنشاء إطار أزرق مع نص
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        frame[:, :, 0] = 100  # أزرق
        
        # إضافة نص
        text = f"ROV Camera Simulation"
        time_text = f"Frame: {self.frame_count}"
        
        cv2.putText(frame, text, (50, height//2-20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(frame, time_text, (50, height//2+20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1)
        
        # إضافة شبكة
        for i in range(0, width, 50):
            cv2.line(frame, (i, 0), (i, height), (50, 50, 50), 1)
        for i in range(0, height, 50):
            cv2.line(frame, (0, i), (width, i), (50, 50, 50), 1)
        
        return frame
    
    def _display_frame(self, frame: np.ndarray):
        """عرض الإطار في الواجهة"""
        try:
            # تحويل إطار OpenCV إلى Qt
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            
            # إنشاء QImage أولاً
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            
            # تحويل QImage إلى QPixmap
            qt_pixmap = QPixmap.fromImage(qt_image)
            
            # تغيير حجم الصورة لتناسب الأداة
            scaled_pixmap = qt_pixmap.scaled(
                self.video_frame.size(), 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            
            self.video_frame.setPixmap(scaled_pixmap)
            
            # حفظ الإطار الحالي للقطات
            self.current_frame = frame
            
        except Exception as e:
            print(f"خطأ في عرض الإطار: {e}")
    
    def _toggle_recording(self):
        """تبديل التسجيل"""
        if not self.is_recording:
            self._start_recording()
        else:
            self._stop_recording()
    
    def _start_recording(self):
        """بدء التسجيل"""
        try:
            # إنشاء اسم ملف فريد
            import time
            filename = f"rov_recording_{int(time.time())}.mp4"
            
            # إعداد كاتب الفيديو
            width, height = map(int, self.camera_resolution.split('x'))
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.video_writer = cv2.VideoWriter(filename, fourcc, self.fps, (width, height))
            
            if self.video_writer.isOpened():
                self.is_recording = True
                self.record_button.setText("إيقاف التسجيل")
                self.record_button.setStyleSheet("""
                    QPushButton {
                        background-color: #dc3545;
                        color: white;
                        border: none;
                        padding: 8px 16px;
                        border-radius: 4px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #c82333;
                    }
                """)
                self.recording_status.setText(f"مسجل: {filename}")
                self.recording_status.setStyleSheet("color: #dc3545; font-weight: bold;")
                
                self.recording_status_changed.emit(True)
            else:
                print("فشل في إنشاء كاتب الفيديو")
                
        except Exception as e:
            print(f"خطأ في بدء التسجيل: {e}")
    
    def _stop_recording(self):
        """إيقاف التسجيل"""
        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None
        
        self.is_recording = False
        self.record_button.setText("بدء التسجيل")
        self.record_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.recording_status.setText("غير مسجل")
        self.recording_status.setStyleSheet("color: #6c757d;")
        
        self.recording_status_changed.emit(False)
    
    def _take_snapshot(self):
        """أخذ لقطة"""
        if hasattr(self, 'current_frame'):
            import time
            filename = f"rov_snapshot_{int(time.time())}.jpg"
            cv2.imwrite(filename, self.current_frame)
            self.snapshot_taken.emit(filename)
            print(f"تم حفظ اللقطة: {filename}")
    
    def _change_quality(self, quality: str):
        """تغيير جودة الفيديو"""
        quality_settings = {
            "منخفضة": "320x240",
            "متوسطة": "640x480", 
            "عالية": "1280x720",
            "فائقة": "1920x1080"
        }
        
        if quality in quality_settings:
            self.camera_resolution = quality_settings[quality]
            self.resolution_label.setText(f"الدقة: {self.camera_resolution}")
            
            # إعادة تكوين الكاميرا
            if self.camera_available:
                width, height = map(int, self.camera_resolution.split('x'))
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    
    def _toggle_lights(self, checked: bool):
        """تبديل الإضاءة"""
        # إرسال أمر تشغيل/إطفاء الإضاءة إلى ROV
        print(f"الإضاءة: {'تشغيل' if checked else 'إطفاء'}")
        # TODO: إرسال الأمر إلى ROV
    
    def setEnabled(self, enabled: bool):
        """تفعيل/تعطيل الأداة"""
        super().setEnabled(enabled)
        if not enabled and self.is_recording:
            self._stop_recording()
    
    def closeEvent(self, event):
        """تنظيف الموارد عند الإغلاق"""
        if self.is_recording:
            self._stop_recording()
        
        if hasattr(self, 'camera') and self.camera.isOpened():
            self.camera.release()
        
        event.accept()
