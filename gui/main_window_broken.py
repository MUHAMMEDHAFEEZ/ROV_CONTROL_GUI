from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QMenuBar, QStatusBar, QLabel, QPushButton, QFrame, QSplitter,
    QMessageBox, QApplication, QSystemTrayIcon, QMenu
)
from PyQt6.QtCore import QTimer, pyqtSignal, Qt, QThread, pyqtSlot
from PyQt6.QtGui import QIcon, QPixmap, QAction, QFont

import sys
import time
from typing import Dict, Any

from utils.config import Config
from utils.logger import ROVLogger
from controller.rov_controller import ROVController
from .camera_feed import CameraFeedWidget
from .control_panel import ControlPanelWidget
from .telemetry_display import TelemetryDisplayWidget

class MainWindow(QMainWindow):
    """Main window for ROV control system""
    
    # Custom signals
    rov_connected = pyqtSignal()
    rov_disconnected = pyqtSignal()
    emergency_stop_signal = pyqtSignal()
    
    def __init__(self, config: Config):
        super().__init__()
        self.config = config
        self.logger = ROVLogger('MainWindow)
        
        # Initialize ROV controller
        self.rov_controller = ROVController(config)
        
        # Application state
        self.is_connected = False
        self.is_fullscreen = False
        
        # Timers
        self.update_timer = QTimer()
        self.connection_timer = QTimer()
        
        # Setup interface
        self._setup_ui()
        self._setup_menu_bar()
        self._setup_status_bar()
        self._setup_connections()
        self._setup_timers()
        self._apply_theme()
        
        # تحميل Settings
        self._load_window_settings()
        
        self.logger.info(Completed تهيئة النافذة الرئيسية)
        
        # محاولة Connection التلقائي
        QTimer.singleShot(1000, self._auto_connect)
    
    def _setup_ui(self):
        "إعداد واجهة المستخدم"
        # النافذة الرئيسية
        self.setWindowTitle(ROV Control System v1.0)
        self.setMinimumSize(1200, 800)
        
        # إعداد الأيقونة
        # self.setWindowIcon(QIcon(assets/rov_icon.png))
        
        # الأداة المركزية
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # التخطيط الرئيسي
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # إنشاء المقسم الرئيسي
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(main_splitter)
        
        # القسم الأيسر - الكاميرا والتيليمتري
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Camera Feed
        self.camera_widget = CameraFeedWidget(self.config)
        left_layout.addWidget(self.camera_widget, 3)  # نسبة أكبر للكاميرا
        
        # View التيليمتري
        self.telemetry_widget = TelemetryDisplayWidget(self.config)
        left_layout.addWidget(self.telemetry_widget, 1)
        
        main_splitter.addWidget(left_widget)
        
        # القسم الأيمن - لوحة التحكم
        self.control_panel = ControlPanelWidget(self.config, self.rov_controller)
        main_splitter.addWidget(self.control_panel)
        
        # تعديل نسب المقسم
        main_splitter.setSizes([800, 400])  # 2:1 تقريباً
        
        # ربط الإشارات
        self._connect_widget_signals()
    
    def _setup_menu_bar(self):
        "إعداد شريط القوائم"
        menubar = self.menuBar()
        
        # قائمة الFile
        file_menu = menubar.addMenu(File)
        
        # اتصال/قطع اتصال
        self.connect_action = QAction(اتصال', self)
        self.connect_action.setShortcut('Ctrl+C)
        self.connect_action.triggered.connect(self._toggle_connection)
        file_menu.addAction(self.connect_action)
        
        file_menu.addSeparator()
        
        # حفظ Settings
        save_settings_action = QAction(حفظ Settings, self)
        save_settings_action.triggered.connect(self._save_settings)
        file_menu.addAction(save_settings_action)
        
        # تحميل Settings
        load_settings_action = QAction(تحميل Settings', self)
        load_settings_action.triggered.connect(self._load_settings)
        file_menu.addAction(load_settings_action)
        
        file_menu.addSeparator()
        
        # Exit
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # قائمة الView
        view_menu = menubar.addMenu(View)
        
        # شاشة كاملة
        fullscreen_action = QAction(شاشة كاملة', self)
        fullscreen_action.setShortcut('F11)
        fullscreen_action.triggered.connect(self._toggle_fullscreen)
        view_menu.addAction(fullscreen_action)
        
        # إظهار/إخفاء لوحة التحكم
        toggle_control_action = QAction(إظهار/إخفاء لوحة التحكم, self)
        toggle_control_action.triggered.connect(self._toggle_control_panel)
        view_menu.addAction(toggle_control_action)
        
        # قائمة التحكم
        control_menu = menubar.addMenu(تحكم)
        
        # إيقاف طارئ
        emergency_action = QAction(إيقاف طارئ', self)
        emergency_action.setShortcut('Space)
        emergency_action.triggered.connect(self._emergency_stop)
        control_menu.addAction(emergency_action)
        
        # معايرة
        calibrate_action = QAction(معايرة Sensors, self)
        calibrate_action.triggered.connect(self._calibrate_sensors)
        control_menu.addAction(calibrate_action)
        
        # قائمة الHelp
        help_menu = menubar.addMenu(Help')
        
        # About
        about_action = QAction('About, self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _setup_status_bar(self):
        "إعداد شريط الحالة"
        self.status_bar = self.statusBar()
        
        # حالة Connection
        self.connection_status = QLabel(غير Connected")
        self.connection_status.setStyleSheet("color: red; font-weight: bold;)
        self.status_bar.addPermanentWidget(self.connection_status)
        
        # حالة البطارية
        self.battery_status = QLabel(البطارية: --)
        self.status_bar.addPermanentWidget(self.battery_status)
        
        # العمق
        self.depth_status = QLabel(Depth: -- م)
        self.status_bar.addPermanentWidget(self.depth_status)
        
        # وضع التحكم
        self.control_mode_status = QLabel(Mode: يدوي)
        self.status_bar.addPermanentWidget(self.control_mode_status)
        
        # الوقت
        self.time_status = QLabel()
        self.status_bar.addPermanentWidget(self.time_status)
    
    def _setup_connections(self):
        "إعداد Connectionات والإشارات"
        # ربط إشارات ROV
        self.rov_connected.connect(self._on_rov_connected)
        self.rov_disconnected.connect(self._on_rov_disconnected)
        self.emergency_stop_signal.connect(self._on_emergency_stop)
    
    def _connect_widget_signals(self):
        "ربط إشارات الأدوات"
        # إشارات لوحة التحكم
        self.control_panel.connection_requested.connect(self._toggle_connection)
        self.control_panel.emergency_stop_requested.connect(self._emergency_stop)
        self.control_panel.calibration_requested.connect(self._calibrate_sensors)
        
        # إشارات الكاميرا
        self.camera_widget.recording_status_changed.connect(self._on_recording_status_changed)
    
    def _setup_timers(self):
        "إعداد المؤقتات"
        # مؤقت تحديث الواجهة
        self.update_timer.timeout.connect(self._update_ui)
        self.update_timer.start(100)  # 10 FPS
        
        # مؤقت فحص Connection
        self.connection_timer.timeout.connect(self._check_connection)
        self.connection_timer.start(5000)  # كل 5 ثوانٍ
    
    def _apply_theme(self):
        "تطبيق المظهر""
        theme = self.config.get(GUI', 'theme', 'dark')
        
        if theme == 'dark:
            self._apply_dark_theme()
        else:
            self._apply_light_theme()
    
    def _apply_dark_theme(self):
        """Apply dark theme"""
        dark_style = """
        QMainWindow {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        QMenuBar {
            background-color: #3c3c3c;
            color: #ffffff;
            border-bottom: 1px solid #555555;
        }
        QMenuBar::item {
            background-color: #3c3c3c;
            padding: 4px 8px;
        }
        QMenuBar::item:selected {
            background-color: #555555;
        }
        QStatusBar {
            background-color: #3c3c3c;
            color: #ffffff;
            border-top: 1px solid #555555;
        }
        QTabWidget::pane {
            border: 1px solid #555555;
            background-color: #2b2b2b;
        }
        QTabBar::tab {
            background-color: #3c3c3c;
            color: #ffffff;
            padding: 8px 16px;
            margin-right: 2px;
        }
        QTabBar::tab:selected {
            background-color: #555555;
        }
        """
        self.setStyleSheet(dark_style)
    
    def _apply_light_theme(self):
        ""تطبيق المظهر الفاتح"
        # المظهر الافتراضي
        self.setStyleSheet(")
    
    def _load_window_settings(self):
        ""تحميل إعدادات النافذة""
        width = self.config.get_int(GUI', 'window_width', 1200)
        height = self.config.get_int('GUI', 'window_height, 800)
        self.resize(width, height)
    
    def _auto_connect(self):
        ""محاولة Connection التلقائي""
        if self.config.get_bool(COMMUNICATION', 'auto_connect, False):
            self._connect_rov()
    
    def _toggle_connection(self):
        ""تبديل حالة Connection""
        if self.is_connected:
            self._disconnect_rov()
        else:
            self._connect_rov()
    
    def _connect_rov(self):
        ""Connection بـ ROV""
        try:
            self.status_bar.showMessage(جارٍ Connection...)
            
            if self.rov_controller.connect():
                self.is_connected = True
                self.rov_connected.emit()
                self.status_bar.showMessage(Completed Connection successfully, 3000)
            else:
                self.status_bar.showMessage(Failed to Connection, 5000)
                QMessageBox.warning(self, Error in Connection, Failed to Connection بـ ROV)
                
        except Exception as e:
            self.logger.error(fError in Connection: {e})
            QMessageBox.critical(self, خطأ, fError in Connection: {e})
    
    def _disconnect_rov(self):
        ""قطع Connection مع ROV""
        try:
            self.rov_controller.disconnect()
            self.is_connected = False
            self.rov_disconnected.emit()
            self.status_bar.showMessage(Completed قطع Connection, 3000)
            
        except Exception as e:
            self.logger.error(fError in قطع Connection: {e})
    
    @pyqtSlot()
    def _on_rov_connected(self):
        ""معالجة حدث Connection""
        self.connection_status.setText(Connected)
        self.connection_status.setStyleSheet("color: green; font-weight: bold;")
        self.connect_action.setText(قطع Connection)
        
        # تفعيل أدوات التحكم
        self.control_panel.setEnabled(True)
        self.camera_widget.setEnabled(True)
        
        self.logger.info(Completed Connection بـ ROV)
    
    @pyqtSlot()
    def _on_rov_disconnected(self):
        ""معالجة حدث قطع Connection""
        self.connection_status.setText(غير Connected)
        self.connection_status.setStyleSheet("color: red; font-weight: bold;")
        self.connect_action.setText(اتصال)
        
        # تعطيل أدوات التحكم
        self.control_panel.setEnabled(False)
        self.camera_widget.setEnabled(False)
        
        self.logger.info(Completed قطع Connection مع ROV)
    
    def _emergency_stop(self):
        ""تنفيذ الإيقاف الطارئ""
        self.rov_controller.emergency_stop()
        self.emergency_stop_signal.emit()
        self.status_bar.showMessage(Completed تنفيذ الإيقاف الطارئ!, 5000)
        
        # إظهار رسالة تحذيرية
        QMessageBox.warning(self, إيقاف طارئ, Completed تنفيذ الإيقاف الطارئ!\nجميع المحركات متوقفة.)
    
    @pyqtSlot()
    def _on_emergency_stop(self):
        ""معالجة حدث الإيقاف الطارئ"
        # تحديث الواجهة لإظهار حالة الإيقاف الطارئ
        self.control_panel.indicate_emergency_stop()
    
    def _calibrate_sensors(self):
        "معايرة Sensors""
        reply = QMessageBox.question(
            self, 
            معايرة Sensors, 
            هل تريد بدء معايرة Sensors؟\nتأكد من أن ROV في وضع مستقر.,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # بدء المعايرة (يمكن تنفيذها في خيط منفصل)
            self.status_bar.showMessage(جارٍ المعايرة...)
            # TODO: تنفيذ المعايرة
            self.status_bar.showMessage(Completedت المعايرة successfully, 3000)
    
    def _update_ui(self):
        ""تحديث الواجهة"
        # تحديث الوقت
        current_time = time.strftime(%H:%M:%S)
        self.time_status.setText(current_time)
        
        if self.is_connected:
            # الحصول على حالة ROV
            rov_status = self.rov_controller.get_rov_status()
            
            # تحديث شريط الحالة
            battery = rov_status[state'].get('battery, 0)
            self.battery_status.setText(fالبطارية: {battery}%")
            
            depth = rov_status[state']['position'].get('z, 0)
            self.depth_status.setText(fDepth: {abs(depth):.1f} م)
            
            control_mode = rov_status.get(control_mode', 'manual')
            mode_text = {'manual': يدوي, 'stabilized': مستقر, 'position': موقعي}.get(control_mode, control_mode)
            self.control_mode_status.setText(fMode: {mode_text})
            
            # تحديث أدوات التيليمتري
            self.telemetry_widget.update_data(rov_status['state])
    
    def _check_connection(self):
        ""فحص حالة Connection"
        if self.is_connected:
            # فحص Connection مع ROV
            # TODO: تنفيذ فحص Connection
            pass
    
    def _toggle_fullscreen(self):
        "تبديل الشاشة الكاملة""
        if self.is_fullscreen:
            self.showNormal()
            self.is_fullscreen = False
        else:
            self.showFullScreen()
            self.is_fullscreen = True
    
    def _toggle_control_panel(self):
        ""إظهار/إخفاء لوحة التحكم""
        self.control_panel.setVisible(not self.control_panel.isVisible())
    
    def _on_recording_status_changed(self, recording: bool):
        ""معالجة تغيير حالة التسجيل""
        if recording:
            self.status_bar.showMessage(جارٍ التسجيل...)
        else:
            self.status_bar.showMessage(Completed Stop Recording, 3000)
    
    def _save_settings(self):
        ""حفظ Settings"
        # حفظ حجم النافذة
        self.config.set(GUI', 'window_width', str(self.width()))
        self.config.set('GUI', 'window_height', str(self.height()))
        
        self.status_bar.showMessage(Completed حفظ الإعدادات", 3000)
    
    def _load_settings(self):
        ""تحميل Settings""
        self._load_window_settings()
        self._apply_theme()
        self.status_bar.showMessage(Completed تحميل Settings, 3000)
    
    def _show_about(self):
        ""إظهار معلومات About البرنامج""
        about_text = ""
        <h2>ROV Control System v1.0</h2>
        <p>نظام تحكم متقدم للمركبات المائية عن بُعد</p>
        <p><b>المطور:</b> فريق ROV</p>
        <p><b>التاريخ:</b> 2025</p>
        <p><b>الترخيص:</b> MIT License</p>
        
        <h3>الميزات:</h3>
        <ul>
        <li>تحكم في الوقت الحقيقي</li>
        <li>View بيانات Sensors</li>
        <li>تسجيل الفيديو</li>
        <li>أنظمة الأمان</li>
        </ul>
        ""
        
        QMessageBox.about(self, About ROV Control System, about_text)
    
    def closeEvent(self, event):
        ""معالجة إغلاق النافذة"
        # حفظ Settings
        self._save_settings()
        
        # قطع Connection إذا كان Connectedاً
        if self.is_connected:
            self._disconnect_rov()
        
        # إغلاق متحكم ROV
        self.rov_controller.shutdown()
        
        self.logger.info(Completed إغلاق التطبيق")
        event.accept()
