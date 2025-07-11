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
    """Telemetry and sensor data display widget"""
    
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        
        # Telemetry data
        self.telemetry_data = {}
        self.data_history = {
            'depth': deque(maxlen=100),
            'temperature': deque(maxlen=100),
            'pressure': deque(maxlen=100),
            'roll': deque(maxlen=100),
            'pitch': deque(maxlen=100),
            'yaw': deque(maxlen=100),
            'timestamps': deque(maxlen=100)
        }
        
        self._setup_ui()
        
        # Data update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_displays)
        self.update_timer.start(100)  # Update every 100ms
    
    def _setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Title
        title_label = QLabel("Telemetry Data")
        title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Tabs
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Main indicators tab
        indicators_tab = self._create_indicators_tab()
        self.tab_widget.addTab(indicators_tab, "Indicators")
        
        # Charts tab
        charts_tab = self._create_charts_tab()
        self.tab_widget.addTab(charts_tab, "Charts")
        
        # Detailed data tab
        details_tab = self._create_details_tab()
        self.tab_widget.addTab(details_tab, "Details")
        
        # Log tab
        log_tab = self._create_log_tab()
        self.tab_widget.addTab(log_tab, "Log")
    
    def _create_indicators_tab(self) -> QWidget:
        """Create main indicators tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Position and orientation group
        position_group = QGroupBox("Position and Orientation")
        position_layout = QGridLayout(position_group)
        
        # Depth
        position_layout.addWidget(QLabel("Depth:"), 0, 0)
        self.depth_label = QLabel("0.0 m")
        self.depth_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        position_layout.addWidget(self.depth_label, 0, 1)
        
        self.depth_bar = QProgressBar()
        self.depth_bar.setRange(0, 100)
        self.depth_bar.setOrientation(Qt.Orientation.Horizontal)
        position_layout.addWidget(self.depth_bar, 0, 2)
        
        # Orientations
        position_layout.addWidget(QLabel("Roll:"), 1, 0)
        self.roll_label = QLabel("0.0°")
        position_layout.addWidget(self.roll_label, 1, 1)
        
        position_layout.addWidget(QLabel("Pitch:"), 2, 0)
        self.pitch_label = QLabel("0.0°")
        position_layout.addWidget(self.pitch_label, 2, 1)
        
        position_layout.addWidget(QLabel("Yaw:"), 3, 0)
        self.yaw_label = QLabel("0.0°")
        position_layout.addWidget(self.yaw_label, 3, 1)
        
        layout.addWidget(position_group)
        
        # Environmental sensors group
        env_group = QGroupBox("Environmental Sensors")
        env_layout = QGridLayout(env_group)
        
        # Temperature
        env_layout.addWidget(QLabel("Temperature:"), 0, 0)
        self.temperature_label = QLabel("--°C")
        self.temperature_label.setStyleSheet("font-weight: bold; color: #FF5722;")
        env_layout.addWidget(self.temperature_label, 0, 1)
        
        # Pressure
        env_layout.addWidget(QLabel("Pressure:"), 1, 0)
        self.pressure_label = QLabel("-- hPa")
        self.pressure_label.setStyleSheet("font-weight: bold; color: #2196F3;")
        env_layout.addWidget(self.pressure_label, 1, 1)
        
        # Humidity
        env_layout.addWidget(QLabel("Humidity:"), 2, 0)
        self.humidity_label = QLabel("--%")
        env_layout.addWidget(self.humidity_label, 2, 1)
        
        layout.addWidget(env_group)
        
        # System status group
        system_group = QGroupBox("System Status")
        system_layout = QGridLayout(system_group)
        
        # Battery
        system_layout.addWidget(QLabel("Battery:"), 0, 0)
        self.battery_label = QLabel("100%")
        system_layout.addWidget(self.battery_label, 0, 1)
        
        self.battery_progress = QProgressBar()
        self.battery_progress.setRange(0, 100)
        self.battery_progress.setValue(100)
        system_layout.addWidget(self.battery_progress, 0, 2)
        
        # Signal
        system_layout.addWidget(QLabel("Signal Strength:"), 1, 0)
        self.signal_label = QLabel("Excellent")
        system_layout.addWidget(self.signal_label, 1, 1)
        
        self.signal_progress = QProgressBar()
        self.signal_progress.setRange(0, 100)
        self.signal_progress.setValue(100)
        system_layout.addWidget(self.signal_progress, 1, 2)
        
        layout.addWidget(system_group)
        
        layout.addStretch()
        return widget
    
    def _create_charts_tab(self) -> QWidget:
        """Create charts tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Depth Chart
        depth_group = QGroupBox("Depth Chart")
        depth_layout = QVBoxLayout(depth_group)
        
        self.depth_plot = pg.PlotWidget()
        self.depth_plot.setLabel('left', 'Depth (m)')
        self.depth_plot.setLabel('bottom', 'Time (s)')
        self.depth_plot.setTitle('Depth Over Time')
        self.depth_plot.showGrid(True, True)
        self.depth_curve = self.depth_plot.plot(pen='b')
        depth_layout.addWidget(self.depth_plot)
        
        layout.addWidget(depth_group)
        
        # Temperature Chart
        temp_group = QGroupBox("Temperature Chart")
        temp_layout = QVBoxLayout(temp_group)
        
        self.temp_plot = pg.PlotWidget()
        self.temp_plot.setLabel('left', 'Temperature (°C)')
        self.temp_plot.setLabel('bottom', 'Time (s)')
        self.temp_plot.setTitle('Temperature Over Time')
        self.temp_plot.showGrid(True, True)
        self.temp_curve = self.temp_plot.plot(pen='r')
        temp_layout.addWidget(self.temp_plot)
        
        layout.addWidget(temp_group)
        
        # Orientation Chart
        orientation_group = QGroupBox("Orientation Chart")
        orientation_layout = QVBoxLayout(orientation_group)
        
        self.orientation_plot = pg.PlotWidget()
        self.orientation_plot.setLabel('left', 'Angle (°)')
        self.orientation_plot.setLabel('bottom', 'Time (s)')
        self.orientation_plot.setTitle('Orientation Over Time')
        self.orientation_plot.showGrid(True, True)
        self.roll_curve = self.orientation_plot.plot(pen='g', name='Roll')
        self.pitch_curve = self.orientation_plot.plot(pen='b', name='Pitch')
        self.yaw_curve = self.orientation_plot.plot(pen='r', name='Yaw')
        orientation_layout.addWidget(self.orientation_plot)
        
        layout.addWidget(orientation_group)
        
        return widget
    
    def _create_details_tab(self) -> QWidget:
        """Create detailed data tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Data table
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(2)
        self.data_table.setHorizontalHeaderLabels(["Parameter", "Value"])
        
        # Fill table with initial data
        self._populate_data_table()
        
        layout.addWidget(self.data_table)
        
        return widget
    
    def _create_log_tab(self) -> QWidget:
        """Create log tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Log text area
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #000000;
                color: #00FF00;
                font-family: 'Courier New', monospace;
                font-size: 10px;
            }
        """)
        
        layout.addWidget(self.log_text)
        
        # Add some initial log entries
        self._add_log_entry("Telemetry system started")
        
        return widget
    
    def _populate_data_table(self):
        """Populate data table"""
        data_items = [
            ("Position X", "0.0 m"),
            ("Position Y", "0.0 m"),
            ("Position Z (Depth)", "0.0 m"),
            ("Velocity X", "0.0 m/s"),
            ("Velocity Y", "0.0 m/s"),
            ("Velocity Z", "0.0 m/s"),
            ("Acceleration X", "0.0 m/s²"),
            ("Acceleration Y", "0.0 m/s²"),
            ("Acceleration Z", "9.81 m/s²"),
            ("Angular X", "0.0 °/s"),
            ("Angular Y", "0.0 °/s"),
            ("Angular Z", "0.0 °/s"),
            ("Temperature", "-- °C"),
            ("Pressure", "-- hPa"),
            ("Humidity", "-- %"),
            ("Battery", "-- %"),
            ("Uptime", "00:00:00"),
        ]
        
        self.data_table.setRowCount(len(data_items))
        
        for i, (name, value) in enumerate(data_items):
            self.data_table.setItem(i, 0, QTableWidgetItem(name))
            self.data_table.setItem(i, 1, QTableWidgetItem(value))
        
        # Adjust column widths
        self.data_table.resizeColumnsToContents()
    
    def _add_log_entry(self, message: str):
        """Add new log entry"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.log_text.append(log_entry)
        
        # Scroll to end
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)
    
    def update_data(self, data: Dict[str, Any]):
        """Update displayed data"""
        self.telemetry_data = data
        
        # Add data to history
        current_time = time.time()
        self.data_history['timestamps'].append(current_time)
        
        # Update position data
        position = data.get('position', {})
        depth = abs(position.get('z', 0))
        self.data_history['depth'].append(depth)
        
        # Update orientation data
        orientation = data.get('orientation', {})
        roll = orientation.get('roll', 0)
        pitch = orientation.get('pitch', 0)
        yaw = orientation.get('yaw', 0)
        
        self.data_history['roll'].append(roll)
        self.data_history['pitch'].append(pitch)
        self.data_history['yaw'].append(yaw)
        
        # Update sensor data
        sensors = data.get('sensors', {})
        temp = sensors.get('temperature', 0)
        pressure = sensors.get('pressure', 0)
        
        self.data_history['temperature'].append(temp)
        self.data_history['pressure'].append(pressure)
        
        # Add log for important changes
        if depth > 10:  # Depth greater than 10 meters
            self._add_log_entry(f"Warning: Current depth {depth:.1f} meters")
        
        if abs(roll) > 30 or abs(pitch) > 30:  # Large tilt
            self._add_log_entry(f"Warning: Large tilt - Roll: {roll:.1f}°, Pitch: {pitch:.1f}°")
    
    def _update_displays(self):
        """Update visual displays"""
        if not self.telemetry_data:
            return
        
        # Update indicators
        self._update_indicators()
        
        # Update charts
        self._update_charts()
        
        # Update data table
        self._update_data_table()
    
    def _update_indicators(self):
        """Update main indicators"""
        # Position and orientation
        position = self.telemetry_data.get('position', {})
        orientation = self.telemetry_data.get('orientation', {})
        
        depth = abs(position.get('z', 0))
        self.depth_label.setText(f"{depth:.1f} m")
        self.depth_bar.setValue(min(int(depth), 100))
        
        roll = orientation.get('roll', 0)
        pitch = orientation.get('pitch', 0)
        yaw = orientation.get('yaw', 0)
        
        self.roll_label.setText(f"{roll:.1f}°")
        self.pitch_label.setText(f"{pitch:.1f}°")
        self.yaw_label.setText(f"{yaw:.1f}°")
        
        # Environmental sensors
        sensors = self.telemetry_data.get('sensors', {})
        
        temp = sensors.get('temperature', 0)
        self.temperature_label.setText(f"{temp:.1f}°C")
        
        pressure = sensors.get('pressure', 0)
        self.pressure_label.setText(f"{pressure:.1f} hPa")
        
        humidity = sensors.get('humidity', 0)
        self.humidity_label.setText(f"{humidity:.1f}%")
        
        # System status
        battery = self.telemetry_data.get('battery', 100)
        self.battery_label.setText(f"{battery}%")
        self.battery_progress.setValue(battery)
        
        # Change battery color based on level
        if battery > 50:
            color = "#4CAF50"
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
        """Update charts"""
        if len(self.data_history['timestamps']) < 2:
            return
        
        # Convert times to relative times
        base_time = self.data_history['timestamps'][0]
        times = [t - base_time for t in self.data_history['timestamps']]
        
        # Plot depth
        self.depth_curve.setData(times, list(self.data_history['depth']))
        
        # Plot temperature
        self.temp_curve.setData(times, list(self.data_history['temperature']))
        
        # Plot orientation
        self.roll_curve.setData(times, list(self.data_history['roll']))
        self.pitch_curve.setData(times, list(self.data_history['pitch']))
        self.yaw_curve.setData(times, list(self.data_history['yaw']))
    
    def _update_data_table(self):
        """Update detailed data table"""
        position = self.telemetry_data.get('position', {})
        velocity = self.telemetry_data.get('velocity', {})
        orientation = self.telemetry_data.get('orientation', {})
        sensors = self.telemetry_data.get('sensors', {})
        
        # Update table values
        updates = [
            (0, f"{position.get('x', 0):.2f} m"),      # Position X
            (1, f"{position.get('y', 0):.2f} m"),      # Position Y
            (2, f"{abs(position.get('z', 0)):.2f} m"),  # Depth
            (3, f"{velocity.get('x', 0):.2f} m/s"),    # Velocity X
            (4, f"{velocity.get('y', 0):.2f} m/s"),    # Velocity Y
            (5, f"{velocity.get('z', 0):.2f} m/s"),    # Velocity Z
            (9, f"{orientation.get('roll', 0):.1f}°"),  # Angular X
            (10, f"{orientation.get('pitch', 0):.1f}°"), # Angular Y
            (11, f"{orientation.get('yaw', 0):.1f}°"),   # Angular Z
            (12, f"{sensors.get('temperature', 0):.1f} °C"), # Temperature
            (13, f"{sensors.get('pressure', 0):.1f} hPa"),   # Pressure
            (14, f"{sensors.get('humidity', 0):.1f} %"),     # Humidity
            (15, f"{self.telemetry_data.get('battery', 100)} %"), # Battery
        ]
        
        for row, value in updates:
            if row < self.data_table.rowCount():
                self.data_table.setItem(row, 1, QTableWidgetItem(value))
    
    def clear_data(self):
        """Clear all data"""
        for key in self.data_history:
            self.data_history[key].clear()
        
        self.telemetry_data.clear()
        self._add_log_entry("All data cleared")
    
    def export_data(self, filename: str):
        """Export data to file"""
        try:
            import csv
            
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                
                # Write column headers
                headers = ['timestamp', 'depth', 'temperature', 'pressure', 'roll', 'pitch', 'yaw']
                writer.writerow(headers)
                
                # Write data
                for i in range(len(self.data_history['timestamps'])):
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
            
            self._add_log_entry(f"Data exported to {filename}")
            
        except Exception as e:
            self._add_log_entry(f"Error exporting data: {e}")
