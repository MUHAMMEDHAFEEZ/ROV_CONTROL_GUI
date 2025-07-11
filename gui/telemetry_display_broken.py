from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QGroupBox, QProgressBar, QTableWidget, QTableWidgetItem,
    QTabWidget, QTextEdit, QScrollArea, QGridLayout
)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont, QColor, QPalette
import pyqtgraph as pg
import time
from typing import Dict, Any, List
from collections import deque

class TelemetryDisplayWidget(QWidget):
    ""أداة View بيانات التيليمتري وSensors"
    
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        
        # بيانات التيليمتري
        self.telemetry_data = {}
        self.data_history = {
            'depth': deque(maxlen=100),
            'temperature': deque(maxlen=100),
            'pressure': deque(maxlen=100),
            'roll': deque(maxlen=100),
            'pitch': deque(maxlen=100),
            'yaw': deque(maxlen=100),
            'timestamps: deque(maxlen=100)
        }
        
        self._setup_ui()
        
        # مؤقت تحديث Data
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_displays)
        self.update_timer.start(100)  # تحديث كل 100ms
    
    def _setup_ui(self):
        "إعداد واجهة المستخدم"
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Title
        title_label = QLabel(بيانات التيليمتري")
        title_label.setFont(QFont("Arial, 12, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # علامات التبويب
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # تبويب المؤشرات الرئيسية
        indicators_tab = self._create_indicators_tab()
        self.tab_widget.addTab(indicators_tab, المؤشرات)
        
        # تبويب الرسوم البيانية
        charts_tab = self._create_charts_tab()
        self.tab_widget.addTab(charts_tab, الرسوم البيانية)
        
        # تبويب Data التفصيلية
        details_tab = self._create_details_tab()
        self.tab_widget.addTab(details_tab, التفاصيل)
        
        # تبويب السجل
        log_tab = self._create_log_tab()
        self.tab_widget.addTab(log_tab, السجل")
    
    def _create_indicators_tab(self) -> QWidget:
        ""إنشاء تبويب المؤشرات الرئيسية"
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # مجموعة الموقع والاتجاه
        position_group = QGroupBox(الموقع والاتجاه)
        position_layout = QGridLayout(position_group)
        
        # العمق
        position_layout.addWidget(QLabel(Depth:"), 0, 0)
        self.depth_label = QLabel(0.0 م)
        self.depth_label.setStyleSheet("font-weight: bold; font-size: 14px;)
        position_layout.addWidget(self.depth_label, 0, 1)
        
        self.depth_bar = QProgressBar()
        self.depth_bar.setRange(0, 100)
        self.depth_bar.setOrientation(Qt.Orientation.Horizontal)
        position_layout.addWidget(self.depth_bar, 0, 2)
        
        # الاتجاهات
        position_layout.addWidget(QLabel(الميل (Roll):"), 1, 0)
        self.roll_label = QLabel("0.0°")
        position_layout.addWidget(self.roll_label, 1, 1)
        
        position_layout.addWidget(QLabel(الانحدار (Pitch):), 2, 0)
        self.pitch_label = QLabel("0.0°")
        position_layout.addWidget(self.pitch_label, 2, 1)
        
        position_layout.addWidget(QLabel(الدوران (Yaw):), 3, 0)
        self.yaw_label = QLabel("0.0°)
        position_layout.addWidget(self.yaw_label, 3, 1)
        
        layout.addWidget(position_group)
        
        # مجموعة Sensors البيئية
        env_group = QGroupBox(Sensors البيئية)
        env_layout = QGridLayout(env_group)
        
        # درجة الحرارة
        env_layout.addWidget(QLabel(Temperature:"), 0, 0)
        self.temperature_label = QLabel("--°C")
        self.temperature_label.setStyleSheet("font-weight: bold; color: #FF5722;)
        env_layout.addWidget(self.temperature_label, 0, 1)
        
        # الضغط
        env_layout.addWidget(QLabel(Pressure:"), 1, 0)
        self.pressure_label = QLabel("-- hPa")
        self.pressure_label.setStyleSheet("font-weight: bold; color: #2196F3;)
        env_layout.addWidget(self.pressure_label, 1, 1)
        
        # الرطوبة
        env_layout.addWidget(QLabel(الرطوبة:"), 2, 0)
        self.humidity_label = QLabel("--%)
        env_layout.addWidget(self.humidity_label, 2, 1)
        
        layout.addWidget(env_group)
        
        # مجموعة حالة النظام
        system_group = QGroupBox(حالة النظام)
        system_layout = QGridLayout(system_group)
        
        # البطارية
        system_layout.addWidget(QLabel(البطارية:"), 0, 0)
        self.battery_label = QLabel("100%)
        system_layout.addWidget(self.battery_label, 0, 1)
        
        self.battery_progress = QProgressBar()
        self.battery_progress.setRange(0, 100)
        self.battery_progress.setValue(100)
        system_layout.addWidget(self.battery_progress, 0, 2)
        
        # الإشارة
        system_layout.addWidget(QLabel(قوة الإشارة:"), 1, 0)
        self.signal_label = QLabel(ممتاز)
        system_layout.addWidget(self.signal_label, 1, 1)
        
        self.signal_progress = QProgressBar()
        self.signal_progress.setRange(0, 100)
        self.signal_progress.setValue(100)
        system_layout.addWidget(self.signal_progress, 1, 2)
        
        layout.addWidget(system_group)
        
        layout.addStretch()
        return widget
    
    def _create_charts_tab(self) -> QWidget:
        ""إنشاء تبويب الرسوم البيانية"
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # رسم العمق
        depth_group = QGroupBox(رسم العمق)
        depth_layout = QVBoxLayout(depth_group)
        
        self.depth_plot = pg.PlotWidget()
        self.depth_plot.setLabel(left', العمق (م))
        self.depth_plot.setLabel('bottom', الوقت (ث))
        self.depth_plot.setTitle(تغيير العمق مع الوقت)
        self.depth_plot.showGrid(True, True)
        self.depth_curve = self.depth_plot.plot(pen='b)
        depth_layout.addWidget(self.depth_plot)
        
        layout.addWidget(depth_group)
        
        # رسم درجة الحرارة
        temp_group = QGroupBox(رسم درجة الحرارة)
        temp_layout = QVBoxLayout(temp_group)
        
        self.temp_plot = pg.PlotWidget()
        self.temp_plot.setLabel(left', درجة الحرارة (°C))
        self.temp_plot.setLabel('bottom', الوقت (ث))
        self.temp_plot.setTitle(تغيير درجة الحرارة مع الوقت)
        self.temp_plot.showGrid(True, True)
        self.temp_curve = self.temp_plot.plot(pen='r)
        temp_layout.addWidget(self.temp_plot)
        
        layout.addWidget(temp_group)
        
        # رسم الاتجاه
        orientation_group = QGroupBox(رسم الاتجاه)
        orientation_layout = QVBoxLayout(orientation_group)
        
        self.orientation_plot = pg.PlotWidget()
        self.orientation_plot.setLabel(left', الزاوية (°))
        self.orientation_plot.setLabel('bottom', الوقت (ث))
        self.orientation_plot.setTitle(الاتجاه مع الوقت)
        self.orientation_plot.showGrid(True, True)
        self.roll_curve = self.orientation_plot.plot(pen='g', name='Roll')
        self.pitch_curve = self.orientation_plot.plot(pen='b', name='Pitch')
        self.yaw_curve = self.orientation_plot.plot(pen='r', name='Yaw)
        orientation_layout.addWidget(self.orientation_plot)
        
        layout.addWidget(orientation_group)
        
        return widget
    
    def _create_details_tab(self) -> QWidget:
        "إنشاء تبويب Data التفصيلية"
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # جدول Data
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(2)
        self.data_table.setHorizontalHeaderLabels([المعطى", القيمة])
        
        # تعبئة الجدول بData الأولية
        self._populate_data_table()
        
        layout.addWidget(self.data_table)
        
        return widget
    
    def _create_log_tab(self) -> QWidget:
        ""إنشاء تبويب السجل"
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # منطقة نص السجل
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet(""
            QTextEdit {
                background-color: #000000;
                color: #00FF00;
                font-family: Courier New, monospace;
                font-size: 10px;
            }
        "")
        
        layout.addWidget(self.log_text)
        
        # إضافة بعض السجلات الأولية
        self._add_log_entry(Completed بدء نظام التيليمتري")
        
        return widget
    
    def _populate_data_table(self):
        ""تعبئة جدول Data""
        data_items = [
            (الموقع X, 0.0 م),
            (الموقع Y, 0.0 م),
            (الموقع Z (العمق), 0.0 م),
            (السرعة X, 0.0 م/ث),
            (السرعة Y, 0.0 م/ث),
            (السرعة Z, 0.0 م/ث),
            (تسارع X, 0.0 م/ث²),
            (تسارع Y, 0.0 م/ث²),
            (تسارع Z, 9.81 م/ث²),
            (دوران X, 0.0 °/ث),
            (دوران Y, 0.0 °/ث),
            (دوران Z, 0.0 °/ث),
            (درجة الحرارة, "-- °C"),
            (الضغط, "-- hPa"),
            (الرطوبة, "-- %"),
            (البطارية, "-- %"),
            (وقت الON, "00:00:00),
        ]
        
        self.data_table.setRowCount(len(data_items))
        
        for i, (name, value) in enumerate(data_items):
            self.data_table.setItem(i, 0, QTableWidgetItem(name))
            self.data_table.setItem(i, 1, QTableWidgetItem(value))
        
        # تعديل View الأعمدة
        self.data_table.resizeColumnsToContents()
    
    def _add_log_entry(self, message: str):
        "إضافة دخل جديد للسجل""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}
        self.log_text.append(log_entry)
        
        # الCompletedرير إلى النهاية
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)
    
    def update_data(self, data: Dict[str, Any]):
        "تحديث Data المعروضة"
        self.telemetry_data = data
        
        # إضافة Data إلى التاريخ
        current_time = time.time()
        self.data_history[timestamps].append(current_time)
        
        # تحديث بيانات الموقع
        position = data.get(position', {})
        depth = abs(position.get('z', 0))
        self.data_history['depth].append(depth)
        
        # تحديث بيانات الاتجاه
        orientation = data.get(orientation', {})
        roll = orientation.get('roll', 0)
        pitch = orientation.get('pitch', 0)
        yaw = orientation.get('yaw', 0)
        
        self.data_history['roll'].append(roll)
        self.data_history['pitch'].append(pitch)
        self.data_history['yaw].append(yaw)
        
        # تحديث بيانات Sensors
        sensors = data.get(sensors', {})
        temp = sensors.get('temperature', 0)
        pressure = sensors.get('pressure', 0)
        
        self.data_history['temperature'].append(temp)
        self.data_history['pressure].append(pressure)
        
        # إضافة سجل للتغييرات المهمة
        if depth > 10:  # عمق أكبر من 10 متر
            self._add_log_entry(fتحذير: العمق الحالي {depth:.1f} متر)
        
        if abs(roll) > 30 or abs(pitch) > 30:  # ميل كبير
            self._add_log_entry(fتحذير: ميل كبير - Roll: {roll:.1f}°, Pitch: {pitch:.1f}°")
    
    def _update_displays(self):
        ""تحديث العروض المرئية"
        if not self.telemetry_data:
            return
        
        # تحديث المؤشرات
        self._update_indicators()
        
        # تحديث الرسوم البيانية
        self._update_charts()
        
        # تحديث جدول Data
        self._update_data_table()
    
    def _update_indicators(self):
        "تحديث المؤشرات الرئيسية"
        # الموقع والاتجاه
        position = self.telemetry_data.get(position', {})
        orientation = self.telemetry_data.get('orientation', {})
        
        depth = abs(position.get('z, 0))
        self.depth_label.setText(f{depth:.1f} م")
        self.depth_bar.setValue(min(int(depth), 100))
        
        roll = orientation.get(roll', 0)
        pitch = orientation.get('pitch', 0)
        yaw = orientation.get('yaw, 0)
        
        self.roll_label.setText(f"{roll:.1f}°")
        self.pitch_label.setText(f"{pitch:.1f}°")
        self.yaw_label.setText(f"{yaw:.1f}°)
        
        # Sensors البيئية
        sensors = self.telemetry_data.get(sensors', {})
        
        temp = sensors.get('temperature', 0)
        self.temperature_label.setText(f{temp:.1f}°C")
        
        pressure = sensors.get('pressure', 0)
        self.pressure_label.setText(f"{pressure:.1f} hPa")
        
        humidity = sensors.get('humidity, 0)
        self.humidity_label.setText(f"{humidity:.1f}%)
        
        # حالة النظام
        battery = self.telemetry_data.get(battery, 100)
        self.battery_label.setText(f{battery}%)
        self.battery_progress.setValue(battery)
        
        # تغيير لون البطارية حسب المستوى
        if battery > 50:
            color = #4CAF50"
        elif battery > 20:
            color = "#FF9800"
        else:
            color = "#F44336"
        
        self.battery_progress.setStyleSheet(f"""
            QProgressBar::chunk {{
                background-color: {color};
            }}
        """)
    
    def _update_charts(self):
        ""تحديث الرسوم البيانية"
        if len(self.data_history[timestamps]) < 2:
            return
        
        # تحويل الأوقات إلى أوقات نسبية
        base_time = self.data_history[timestamps'][0]
        times = [t - base_time for t in self.data_history['timestamps]]
        
        # رسم العمق
        self.depth_curve.setData(times, list(self.data_history[depth]))
        
        # رسم درجة الحرارة
        self.temp_curve.setData(times, list(self.data_history[temperature]))
        
        # رسم الاتجاه
        self.roll_curve.setData(times, list(self.data_history[roll']))
        self.pitch_curve.setData(times, list(self.data_history['pitch']))
        self.yaw_curve.setData(times, list(self.data_history['yaw]))
    
    def _update_data_table(self):
        "تحديث جدول Data التفصيلية"
        position = self.telemetry_data.get(position', {})
        velocity = self.telemetry_data.get('velocity', {})
        orientation = self.telemetry_data.get('orientation', {})
        sensors = self.telemetry_data.get('sensors, {})
        
        # تحديث قيم الجدول
        updates = [
            (0, f{position.get(x, 0):.2f} م),      # الموقع X
            (1, f{position.get(y, 0):.2f} م),      # الموقع Y
            (2, f{abs(position.get(z, 0)):.2f} م),  # العمق
            (3, f{velocity.get(x, 0):.2f} م/ث),    # السرعة X
            (4, f{velocity.get(y, 0):.2f} م/ث),    # السرعة Y
            (5, f{velocity.get(z, 0):.2f} م/ث),    # السرعة Z
            (9, f{orientation.get(roll, 0):.1f}°),  # دوران X
            (10, f{orientation.get(pitch, 0):.1f}°), # دوران Y
            (11, f{orientation.get(yaw, 0):.1f}°),   # دوران Z
            (12, f{sensors.get(temperature, 0):.1f} °C), # درجة الحرارة
            (13, f{sensors.get(pressure, 0):.1f} hPa),   # الضغط
            (14, f{sensors.get(humidity, 0):.1f} %),     # الرطوبة
            (15, f{self.telemetry_data.get(battery, 100)} %), # البطارية
        ]
        
        for row, value in updates:
            if row < self.data_table.rowCount():
                self.data_table.setItem(row, 1, QTableWidgetItem(value))
    
    def clear_data(self):
        "مسح جميع Data""
        for key in self.data_history:
            self.data_history[key].clear()
        
        self.telemetry_data.clear()
        self._add_log_entry(Completed مسح جميع Data)
    
    def export_data(self, filename: str):
        ""تصدير Data إلى File"
        try:
            import csv
            
            with open(filename, w', newline='', encoding='utf-8) as file:
                writer = csv.writer(file)
                
                # كتابة رؤوس الأعمدة
                headers = [timestamp', 'depth', 'temperature', 'pressure', 'roll', 'pitch', 'yaw]
                writer.writerow(headers)
                
                # كتابة Data
                for i in range(len(self.data_history[timestamps'])):
                    row = [
                        self.data_history['timestamps'][i],
                        self.data_history['depth'][i],
                        self.data_history['temperature'][i],
                        self.data_history['pressure'][i],
                        self.data_history['roll'][i],
                        self.data_history['pitch'][i],
                        self.data_history['yaw'][i]
                    ]
                    writer.writerow(row)
            
            self._add_log_entry(fCompleted تصدير البيانات إلى {filename}")
            
        except Exception as e:
            self._add_log_entry(fError in تصدير Data: {e})
