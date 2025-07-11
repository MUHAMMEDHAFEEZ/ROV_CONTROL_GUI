from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QGroupBox, QSlider, QCheckBox, QComboBox, 
    QSpinBox, QDoubleSpinBox, QGridLayout, QProgressBar,
    QDial, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import QTimer, pyqtSignal, Qt
from PyQt6.QtGui import QFont, QPalette, QColor
from typing import Dict, Any

class ControlPanelWidget(QWidget):
    ""لوحة التحكم الرئيسية لـ ROV"
    
    # إشارات مخصصة
    connection_requested = pyqtSignal()
    emergency_stop_requested = pyqtSignal()
    calibration_requested = pyqtSignal()
    movement_command = pyqtSignal(float, float, float, float)  # forward, strafe, vertical, yaw
    
    def __init__(self, config, rov_controller, parent=None):
        super().__init__(parent)
        self.config = config
        self.rov_controller = rov_controller
        self.emergency_stop_active = False
        
        self._setup_ui()
        
        # مؤقت تحديث أوامر الحركة
        self.movement_timer = QTimer()
        self.movement_timer.timeout.connect(self._send_movement_commands)
        self.movement_timer.start(50)  # 20 Hz
    
    def _setup_ui(self):
        "إعداد واجهة المستخدم"
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # Title
        title_label = QLabel(لوحة التحكم")
        title_label.setFont(QFont("Arial, 14, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # أدوات Connection والحالة
        connection_group = self._create_connection_controls()
        layout.addWidget(connection_group)
        
        # أدوات التحكم في الحركة
        movement_group = self._create_movement_controls()
        layout.addWidget(movement_group)
        
        # أدوات أوضاع التحكم
        modes_group = self._create_control_modes()
        layout.addWidget(modes_group)
        
        # أدوات الأمان
        safety_group = self._create_safety_controls()
        layout.addWidget(safety_group)
        
        # أدوات Settings
        settings_group = self._create_settings_controls()
        layout.addWidget(settings_group)
        
        # مساحة فارغة
        layout.addStretch()
    
    def _create_connection_controls(self) -> QGroupBox:
        "إنشاء أدوات Connection""
        group = QGroupBox(Connection والحالة)
        layout = QVBoxLayout(group)
        
        # زر الاتصال
        self.connect_button = QPushButton(اتصال)
        self.connect_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        "")
        self.connect_button.clicked.connect(self.connection_requested.emit)
        layout.addWidget(self.connect_button)
        
        # مؤشر حالة Connection
        connection_layout = QHBoxLayout()
        connection_layout.addWidget(QLabel(حالة الاتصال:"))
        
        self.connection_indicator = QLabel("●")
        self.connection_indicator.setStyleSheet("color: red; font-size: 20px;")
        connection_layout.addWidget(self.connection_indicator)
        
        self.connection_status = QLabel(غير Connected)
        connection_layout.addWidget(self.connection_status)
        connection_layout.addStretch()
        
        layout.addLayout(connection_layout)
        
        # حالة البطارية
        battery_layout = QHBoxLayout()
        battery_layout.addWidget(QLabel(البطارية:))
        
        self.battery_bar = QProgressBar()
        self.battery_bar.setRange(0, 100)
        self.battery_bar.setValue(100)
        self.battery_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        battery_layout.addWidget(self.battery_bar)
        
        layout.addLayout(battery_layout)
        
        return group
    
    def _create_movement_controls(self) -> QGroupBox:
        ""إنشاء أدوات التحكم في الحركة""
        group = QGroupBox(التحكم في الحركة)
        layout = QGridLayout(group)
        
        # التحكم الأمامي/الخلفي
        layout.addWidget(QLabel(Forwardي/Backwardي:), 0, 0)
        self.forward_slider = QSlider(Qt.Orientation.Horizontal)
        self.forward_slider.setRange(-100, 100)
        self.forward_slider.setValue(0)
        self.forward_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.forward_slider.setTickInterval(25)
        layout.addWidget(self.forward_slider, 0, 1)
        
        self.forward_value = QLabel("0)
        layout.addWidget(self.forward_value, 0, 2)
        
        # التحكم الجانبي
        layout.addWidget(QLabel(جانبي:"), 1, 0)
        self.strafe_slider = QSlider(Qt.Orientation.Horizontal)
        self.strafe_slider.setRange(-100, 100)
        self.strafe_slider.setValue(0)
        self.strafe_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.strafe_slider.setTickInterval(25)
        layout.addWidget(self.strafe_slider, 1, 1)
        
        self.strafe_value = QLabel("0)
        layout.addWidget(self.strafe_value, 1, 2)
        
        # التحكم العمودي
        layout.addWidget(QLabel(عمودي:"), 2, 0)
        self.vertical_slider = QSlider(Qt.Orientation.Horizontal)
        self.vertical_slider.setRange(-100, 100)
        self.vertical_slider.setValue(0)
        self.vertical_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.vertical_slider.setTickInterval(25)
        layout.addWidget(self.vertical_slider, 2, 1)
        
        self.vertical_value = QLabel("0)
        layout.addWidget(self.vertical_value, 2, 2)
        
        # التحكم في الدوران
        layout.addWidget(QLabel(دوران:"), 3, 0)
        self.yaw_slider = QSlider(Qt.Orientation.Horizontal)
        self.yaw_slider.setRange(-100, 100)
        self.yaw_slider.setValue(0)
        self.yaw_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.yaw_slider.setTickInterval(25)
        layout.addWidget(self.yaw_slider, 3, 1)
        
        self.yaw_value = QLabel("0)
        layout.addWidget(self.yaw_value, 3, 2)
        
        # ربط الأحداث
        self.forward_slider.valueChanged.connect(lambda v: self.forward_value.setText(str(v)))
        self.strafe_slider.valueChanged.connect(lambda v: self.strafe_value.setText(str(v)))
        self.vertical_slider.valueChanged.connect(lambda v: self.vertical_value.setText(str(v)))
        self.yaw_slider.valueChanged.connect(lambda v: self.yaw_value.setText(str(v)))
        
        # زر إعادة تعيين
        reset_button = QPushButton(إعادة تعيين")
        reset_button.clicked.connect(self._reset_movement_controls)
        layout.addWidget(reset_button, 4, 0, 1, 3)
        
        return group
    
    def _create_control_modes(self) -> QGroupBox:
        ""إنشاء أدوات أوضاع التحكم""
        group = QGroupBox(أوضاع التحكم)
        layout = QVBoxLayout(group)
        
        # وضع التحكم
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel(Mode:))
        
        self.control_mode_combo = QComboBox()
        self.control_mode_combo.addItems([يدوي, مستقر, تلقائي])
        self.control_mode_combo.currentTextChanged.connect(self._change_control_mode)
        mode_layout.addWidget(self.control_mode_combo)
        
        layout.addLayout(mode_layout)
        
        # وضع السرعة
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel(Speed:))
        
        self.speed_mode_combo = QComboBox()
        self.speed_mode_combo.addItems([بطيء, متوسط, سريع])
        self.speed_mode_combo.setCurrentIndex(1)  # متوسط
        self.speed_mode_combo.currentTextChanged.connect(self._change_speed_mode)
        speed_layout.addWidget(self.speed_mode_combo)
        
        layout.addLayout(speed_layout)
        
        # تفعيل الاستقرار
        self.stabilization_checkbox = QCheckBox(تفعيل الاستقرار)
        self.stabilization_checkbox.toggled.connect(self._toggle_stabilization)
        layout.addWidget(self.stabilization_checkbox)
        
        return group
    
    def _create_safety_controls(self) -> QGroupBox:
        ""إنشاء أدوات الأمان""
        group = QGroupBox(الأمان)
        layout = QVBoxLayout(group)
        
        # زر الإيقاف الطارئ
        self.emergency_button = QPushButton(إيقاف طارئ)
        self.emergency_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 15px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #bd2130;
            }
        "")
        self.emergency_button.clicked.connect(self.emergency_stop_requested.emit)
        layout.addWidget(self.emergency_button)
        
        # العمق الأقصى
        depth_layout = QHBoxLayout()
        depth_layout.addWidget(QLabel(العمق الأقصى:"))
        
        self.max_depth_spin = QDoubleSpinBox()
        self.max_depth_spin.setRange(0, 100)
        self.max_depth_spin.setValue(50)
        self.max_depth_spin.setSuffix( م)
        depth_layout.addWidget(self.max_depth_spin)
        
        layout.addLayout(depth_layout)
        
        # تفعيل الصعود التلقائي
        self.auto_surface_checkbox = QCheckBox(الصعود التلقائي عند انقطاع الإشارة)
        self.auto_surface_checkbox.setChecked(True)
        layout.addWidget(self.auto_surface_checkbox)
        
        return group
    
    def _create_settings_controls(self) -> QGroupBox:
        ""إنشاء أدوات Settings""
        group = QGroupBox(Settings)
        layout = QVBoxLayout(group)
        
        # زر المعايرة
        calibrate_button = QPushButton(معايرة Sensors)
        calibrate_button.clicked.connect(self.calibration_requested.emit)
        layout.addWidget(calibrate_button)
        
        # حفظ الإعدادات
        save_button = QPushButton(حفظ Settings)
        save_button.clicked.connect(self._save_settings)
        layout.addWidget(save_button)
        
        # إعادة Load configuration
        reload_button = QPushButton(إعادة تحميل Settings)
        reload_button.clicked.connect(self._reload_settings)
        layout.addWidget(reload_button)
        
        return group
    
    def _reset_movement_controls(self):
        ""إعادة تعيين أدوات التحكم في الحركة""
        self.forward_slider.setValue(0)
        self.strafe_slider.setValue(0)
        self.vertical_slider.setValue(0)
        self.yaw_slider.setValue(0)
    
    def _send_movement_commands(self):
        ""إرسال أوامر الحركة"
        if not self.emergency_stop_active and self.isEnabled():
            forward = self.forward_slider.value()
            strafe = self.strafe_slider.value()
            vertical = self.vertical_slider.value()
            yaw = self.yaw_slider.value()
            
            # إرسال الأوامر إلى متحكم ROV
            self.rov_controller.motor_controller.set_manual_control(forward, strafe, vertical, yaw)
            
            # إرسال إشارة للواجهة
            self.movement_command.emit(forward, strafe, vertical, yaw)
    
    def _change_control_mode(self, mode: str):
        "تغيير وضع التحكم""
        mode_mapping = {
            يدوي: "manual",
            مستقر: "stabilized",
            تلقائي: "auto"
        }
        
        if mode in mode_mapping:
            self.rov_controller.set_control_mode(mode_mapping[mode])
    
    def _change_speed_mode(self, mode: str):
        ""تغيير وضع السرعة""
        mode_mapping = {
            بطيء: "slow",
            متوسط: "medium",
            سريع: "fast"
        }
        
        if mode in mode_mapping:
            self.rov_controller.set_speed_mode(mode_mapping[mode])
    
    def _toggle_stabilization(self, checked: bool):
        ""تبديل الاستقرار""
        if checked:
            self.rov_controller.set_control_mode("stabilized")
        else:
            self.rov_controller.set_control_mode("manual")
    
    def _save_settings(self):
        ""حفظ Settings"
        # حفظ إعدادات لوحة التحكم
        self.config.set('CONTROL', 'max_depth', str(self.max_depth_spin.value()))
        self.config.set('SAFETY', 'auto_surface, str(self.auto_surface_checkbox.isChecked()))
        print(Completed حفظ Settings")
    
    def _reload_settings(self):
        ""إعادة تحميل Settings"
        # تحميل Settings من الFile
        max_depth = self.config.get_float(CONTROL', 'max_depth', 50.0)
        auto_surface = self.config.get_bool('SAFETY', 'auto_surface', True)
        
        self.max_depth_spin.setValue(max_depth)
        self.auto_surface_checkbox.setChecked(auto_surface)
        print(Completed إعادة تحميل الإعدادات")
    
    def update_connection_status(self, connected: bool):
        ""تحديث حالة Connection""
        if connected:
            self.connection_indicator.setStyleSheet("color: green; font-size: 20px;")
            self.connection_status.setText(Connected)
            self.connect_button.setText(قطع Connection)
            self.connect_button.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border: none;
                    padding: 10px;
                    border-radius: 5px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
            """)
        else:
            self.connection_indicator.setStyleSheet("color: red; font-size: 20px;")
            self.connection_status.setText(غير Connected)
            self.connect_button.setText(اتصال)
            self.connect_button.setStyleSheet("""
                QPushButton {
                    background-color: #007bff;
                    color: white;
                    border: none;
                    padding: 10px;
                    border-radius: 5px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #0056b3;
                }
            """)
    
    def update_battery_level(self, level: int):
        ""تحديث مستوى البطارية"
        self.battery_bar.setValue(level)
        
        # تغيير اللون حسب المستوى
        if level > 50:
            color = #4CAF50  # أخضر
        elif level > 20:
            color = #FF9800  # برتقالي
        else:
            color = #F44336  # أحمر
        
        self.battery_bar.setStyleSheet(f""
            QProgressBar {{
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 3px;
            }}
        """)
    
    def indicate_emergency_stop(self):
        ""إظهار حالة الإيقاف الطارئ"
        self.emergency_stop_active = True
        self._reset_movement_controls()
        
        # تغيير لون زر الإيقاف الطارئ
        self.emergency_button.setStyleSheet(""
            QPushButton {
                background-color: #bd2130;
                color: white;
                border: 3px solid #ffc107;
                padding: 15px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 16px;
            }
        "")
        
        # إعادة تعيين بعد 3 ثوانٍ
        QTimer.singleShot(3000, self._reset_emergency_stop)
    
    def _reset_emergency_stop(self):
        "إعادة تعيين حالة الإيقاف الطارئ""
        self.emergency_stop_active = False
        self.emergency_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 15px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #bd2130;
            }
        """)
    
    def setEnabled(self, enabled: bool):
        ""تفعيل/تعطيل لوحة التحكم""
        super().setEnabled(enabled)
        if not enabled:
            self._reset_movement_controls()
            self.emergency_stop_active = False
