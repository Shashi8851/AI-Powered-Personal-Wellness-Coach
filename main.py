from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
                             QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox,
                             QDateEdit, QLineEdit, QComboBox, QTabWidget, QGridLayout, QFrame, QSpinBox, 
                             QDoubleSpinBox, QGroupBox, QScrollArea)
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlError
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib
matplotlib.use('Qt5Agg')
import numpy as np
import sys
from datetime import datetime, timedelta

# Main class
class FitTrack(QWidget):
    def __init__(self):
        super().__init__()
        self.setting()
        self.create_database()
        self.initUI()
        self.button_click()
        
    # Setting
    def setting(self):
        self.setWindowTitle("FitTrack - Health & Fitness Tracker")
        self.resize(1000, 800)
        
    # Create Database and Tables
    def create_database(self):
        # Create table if it doesn't exist
        query = QSqlQuery()
        query.exec_("""
            CREATE TABLE IF NOT EXISTS fitness (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                calories REAL,
                distance REAL,
                heart_rate INTEGER,
                body_temp REAL,
                age INTEGER,
                weight REAL,
                height REAL,
                bmi REAL,
                description TEXT
            )
        """)
        
    # Init UI
    def initUI(self):
        # Create tab widget
        self.tabs = QTabWidget()
        
        # Create tabs
        self.data_entry_tab = QWidget()
        self.stats_tab = QWidget()
        self.visualization_tab = QWidget()
        self.history_tab = QWidget()
        
        # Add tabs to widget
        self.tabs.addTab(self.data_entry_tab, "Data Entry")
        self.tabs.addTab(self.stats_tab, "Stats")
        self.tabs.addTab(self.visualization_tab, "Visualizations")
        self.tabs.addTab(self.history_tab, "History")
        
        # Setup each tab
        self.setup_data_entry_tab()
        self.setup_stats_tab()
        self.setup_visualization_tab()
        self.setup_history_tab()
        
        # Master layout
        self.master_layout = QVBoxLayout()
        
        # Settings and theme controls
        settings_layout = QHBoxLayout()
        self.dark_mode = QCheckBox("Dark Mode")
        settings_layout.addWidget(self.dark_mode)
        settings_layout.addStretch()
        
        self.master_layout.addLayout(settings_layout)
        self.master_layout.addWidget(self.tabs)
        
        self.setLayout(self.master_layout)
        self.apply_styles()
        
    # Setup data entry tab
    def setup_data_entry_tab(self):
        layout = QGridLayout()
        
        # Basic workout info
        workout_group = QGroupBox("Workout Information")
        workout_layout = QGridLayout()
        
        # Date
        workout_layout.addWidget(QLabel("Date:"), 0, 0)
        self.date_box = QDateEdit()
        self.date_box.setDate(QDate.currentDate())
        self.date_box.setCalendarPopup(True)
        workout_layout.addWidget(self.date_box, 0, 1)
        
        # Calories
        workout_layout.addWidget(QLabel("Calories Burned:"), 1, 0)
        self.kal_box = QLineEdit()
        self.kal_box.setPlaceholderText("Number of burned calories")
        workout_layout.addWidget(self.kal_box, 1, 1)
        
        # Distance
        workout_layout.addWidget(QLabel("Distance (km):"), 2, 0)
        self.distance_box = QLineEdit()
        self.distance_box.setPlaceholderText("Enter Distance Ran")
        workout_layout.addWidget(self.distance_box, 2, 1)
        
        # Description
        workout_layout.addWidget(QLabel("Description:"), 3, 0)
        self.description = QLineEdit()
        self.description.setPlaceholderText("Enter the description")
        workout_layout.addWidget(self.description, 3, 1)
        
        workout_group.setLayout(workout_layout)
        
        # Health metrics
        health_group = QGroupBox("Health Metrics")
        health_layout = QGridLayout()
        
        # Heart Rate
        health_layout.addWidget(QLabel("Heart Rate (bpm):"), 0, 0)
        self.heart_rate_box = QSpinBox()
        self.heart_rate_box.setRange(40, 220)
        self.heart_rate_box.setValue(70)
        health_layout.addWidget(self.heart_rate_box, 0, 1)
        
        # Body Temperature
        health_layout.addWidget(QLabel("Body Temp (°C):"), 1, 0)
        self.body_temp_box = QDoubleSpinBox()
        self.body_temp_box.setRange(35.0, 42.0)
        self.body_temp_box.setValue(36.6)
        self.body_temp_box.setSingleStep(0.1)
        health_layout.addWidget(self.body_temp_box, 1, 1)
        
        # Age
        health_layout.addWidget(QLabel("Age:"), 2, 0)
        self.age_box = QSpinBox()
        self.age_box.setRange(1, 120)
        self.age_box.setValue(30)
        health_layout.addWidget(self.age_box, 2, 1)
        
        # Weight
        health_layout.addWidget(QLabel("Weight (kg):"), 3, 0)
        self.weight_box = QDoubleSpinBox()
        self.weight_box.setRange(20.0, 300.0)
        self.weight_box.setValue(70.0)
        self.weight_box.setSingleStep(0.1)
        health_layout.addWidget(self.weight_box, 3, 1)
        
        # Height
        health_layout.addWidget(QLabel("Height (cm):"), 4, 0)
        self.height_box = QDoubleSpinBox()
        self.height_box.setRange(50.0, 250.0)
        self.height_box.setValue(170.0)
        self.height_box.setSingleStep(0.1)
        health_layout.addWidget(self.height_box, 4, 1)
        
        # Calculate BMI Button
        self.calc_bmi_btn = QPushButton("Calculate BMI")
        health_layout.addWidget(self.calc_bmi_btn, 5, 0)
        
        # BMI Result
        self.bmi_result = QLabel("BMI: Not calculated")
        health_layout.addWidget(self.bmi_result, 5, 1)
        
        health_group.setLayout(health_layout)
        
        # Action buttons
        button_group = QGroupBox("Actions")
        button_layout = QGridLayout()
        
        self.add_btn = QPushButton("Add Workout")
        self.delete_btn = QPushButton("Delete Selected")
        self.clear_btn = QPushButton("Clear Form")
        
        button_layout.addWidget(self.add_btn, 0, 0)
        button_layout.addWidget(self.delete_btn, 0, 1)
        button_layout.addWidget(self.clear_btn, 1, 0, 1, 2)
        
        button_group.setLayout(button_layout)
        
        # Add all groups to main layout
        layout.addWidget(workout_group, 0, 0)
        layout.addWidget(health_group, 0, 1)
        layout.addWidget(button_group, 1, 0, 1, 2)
        
        self.data_entry_tab.setLayout(layout)
    
    # Setup stats tab
    def setup_stats_tab(self):
        layout = QVBoxLayout()
        
        # Summary stats
        stats_group = QGroupBox("Fitness Summary")
        stats_layout = QGridLayout()
        
        self.total_workouts = QLabel("Total Workouts: 0")
        self.total_distance = QLabel("Total Distance: 0 km")
        self.total_calories = QLabel("Total Calories: 0")
        self.avg_heart_rate = QLabel("Avg Heart Rate: 0 bpm")
        self.max_distance = QLabel("Longest Workout: 0 km")
        self.avg_bmi = QLabel("Average BMI: 0")
        
        stats_layout.addWidget(self.total_workouts, 0, 0)
        stats_layout.addWidget(self.total_distance, 0, 1)
        stats_layout.addWidget(self.total_calories, 1, 0)
        stats_layout.addWidget(self.avg_heart_rate, 1, 1)
        stats_layout.addWidget(self.max_distance, 2, 0)
        stats_layout.addWidget(self.avg_bmi, 2, 1)
        
        stats_group.setLayout(stats_layout)
        
        # Refresh button
        self.refresh_stats_btn = QPushButton("Refresh Stats")
        
        # Mini chart
        mini_chart_group = QGroupBox("Quick View: Last 7 Days")
        mini_chart_layout = QVBoxLayout()
        
        self.mini_figure = plt.figure(figsize=(5, 3))
        self.mini_canvas = FigureCanvas(self.mini_figure)
        
        mini_chart_layout.addWidget(self.mini_canvas)
        mini_chart_group.setLayout(mini_chart_layout)
        
        layout.addWidget(stats_group)
        layout.addWidget(self.refresh_stats_btn)
        layout.addWidget(mini_chart_group)
        layout.addStretch()
        
        self.stats_tab.setLayout(layout)
    
    # Setup visualization tab
    def setup_visualization_tab(self):
        layout = QVBoxLayout()
        
        # Chart controls
        controls_layout = QHBoxLayout()
        
        controls_layout.addWidget(QLabel("Chart Type:"))
        self.chart_type = QComboBox()
        self.chart_type.addItems([
            "Calories Over Time", 
            "Distance Over Time", 
            "Heart Rate Trends", 
            "BMI Tracking",
            "Workout Distribution",
            "Health Metrics Correlation",
            "Weekly Summary"
        ])
        controls_layout.addWidget(self.chart_type)
        
        controls_layout.addWidget(QLabel("Time Range:"))
        self.time_range = QComboBox()
        self.time_range.addItems([
            "Last 7 Days",
            "Last 30 Days",
            "Last 90 Days",
            "All Data"
        ])
        controls_layout.addWidget(self.time_range)
        
        self.generate_chart_btn = QPushButton("Generate Chart")
        controls_layout.addWidget(self.generate_chart_btn)
        
        # Figure for charts
        self.figure = plt.figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        
        layout.addLayout(controls_layout)
        layout.addWidget(self.canvas)
        
        self.visualization_tab.setLayout(layout)
    
    # Setup history tab
    def setup_history_tab(self):
        layout = QVBoxLayout()
        
        # Search controls
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search in description")
        search_layout.addWidget(self.search_box)
        
        self.search_btn = QPushButton("Search")
        search_layout.addWidget(self.search_btn)
        
        self.show_all_btn = QPushButton("Show All")
        search_layout.addWidget(self.show_all_btn)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(11)
        self.table.setHorizontalHeaderLabels([
            "ID", "Date", "Calories", "Distance", "Heart Rate", 
            "Body Temp", "Age", "Weight", "Height", "BMI", "Description"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addLayout(search_layout)
        layout.addWidget(self.table)
        
        self.history_tab.setLayout(layout)
        self.load_table()

    # Events
    def button_click(self):
        self.add_btn.clicked.connect(self.add_workout)
        self.delete_btn.clicked.connect(self.delete_workout)
        self.clear_btn.clicked.connect(self.reset)
        self.dark_mode.stateChanged.connect(self.toggle_dark)
        self.calc_bmi_btn.clicked.connect(self.calculate_bmi)
        self.refresh_stats_btn.clicked.connect(self.update_stats)
        self.generate_chart_btn.clicked.connect(self.generate_chart)
        self.search_btn.clicked.connect(self.search_entries)
        self.show_all_btn.clicked.connect(self.load_table)
        
        # Calculate BMI on weight/height change
        self.weight_box.valueChanged.connect(self.calculate_bmi)
        self.height_box.valueChanged.connect(self.calculate_bmi)
        
        # Initial stats update
        self.update_stats()
    
    # Calculate BMI
    def calculate_bmi(self):
        try:
            weight = self.weight_box.value()
            height = self.height_box.value() / 100  # convert to meters
            
            if height <= 0:
                self.bmi_result.setText("BMI: Invalid height")
                return 0
            
            bmi = weight / (height * height)
            
            # Set BMI category
            category = ""
            if bmi < 18.5:
                category = "Underweight"
            elif bmi < 25:
                category = "Normal"
            elif bmi < 30:
                category = "Overweight"
            else:
                category = "Obese"
                
            self.bmi_result.setText(f"BMI: {bmi:.1f} ({category})")
            return bmi
        except Exception as e:
            self.bmi_result.setText(f"BMI: Error - {str(e)}")
            return 0

    # Load Table
    def load_table(self):
        self.table.setRowCount(0)
        query = QSqlQuery("SELECT * FROM fitness ORDER BY date DESC")
        row = 0
        while query.next():
            fit_id = query.value(0)
            date = query.value(1)
            calories = query.value(2)
            distance = query.value(3)
            heart_rate = query.value(4)
            body_temp = query.value(5)
            age = query.value(6)
            weight = query.value(7)
            height = query.value(8)
            bmi = query.value(9)
            description = query.value(10)
            
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(fit_id)))
            self.table.setItem(row, 1, QTableWidgetItem(str(date)))
            self.table.setItem(row, 2, QTableWidgetItem(str(calories)))
            self.table.setItem(row, 3, QTableWidgetItem(str(distance)))
            self.table.setItem(row, 4, QTableWidgetItem(str(heart_rate)))
            self.table.setItem(row, 5, QTableWidgetItem(str(body_temp)))
            self.table.setItem(row, 6, QTableWidgetItem(str(age)))
            self.table.setItem(row, 7, QTableWidgetItem(str(weight)))
            self.table.setItem(row, 8, QTableWidgetItem(str(height)))
            self.table.setItem(row, 9, QTableWidgetItem(str(bmi)))
            self.table.setItem(row, 10, QTableWidgetItem(description))
            row += 1
        
        self.update_stats()
        self.update_mini_chart()
    
    # Search entries
    def search_entries(self):
        search_text = self.search_box.text().strip().lower()
        
        if not search_text:
            self.load_table()
            return
            
        self.table.setRowCount(0)
        query = QSqlQuery("SELECT * FROM fitness WHERE lower(description) LIKE ?")
        query.addBindValue(f"%{search_text}%")
        
        if query.exec_():
            row = 0
            while query.next():
                fit_id = query.value(0)
                date = query.value(1)
                calories = query.value(2)
                distance = query.value(3)
                heart_rate = query.value(4)
                body_temp = query.value(5)
                age = query.value(6)
                weight = query.value(7)
                height = query.value(8)
                bmi = query.value(9)
                description = query.value(10)
                
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(fit_id)))
                self.table.setItem(row, 1, QTableWidgetItem(str(date)))
                self.table.setItem(row, 2, QTableWidgetItem(str(calories)))
                self.table.setItem(row, 3, QTableWidgetItem(str(distance)))
                self.table.setItem(row, 4, QTableWidgetItem(str(heart_rate)))
                self.table.setItem(row, 5, QTableWidgetItem(str(body_temp)))
                self.table.setItem(row, 6, QTableWidgetItem(str(age)))
                self.table.setItem(row, 7, QTableWidgetItem(str(weight)))
                self.table.setItem(row, 8, QTableWidgetItem(str(height)))
                self.table.setItem(row, 9, QTableWidgetItem(str(bmi)))
                self.table.setItem(row, 10, QTableWidgetItem(description))
                row += 1
        else:
            QMessageBox.warning(self, "Search Error", "Error searching: " + query.lastError().text())

    # Add Workout
    def add_workout(self):
        date = self.date_box.date().toString("yyyy-MM-dd")
        calories = self.kal_box.text()
        distance = self.distance_box.text()
        description = self.description.text()
        heart_rate = self.heart_rate_box.value()
        body_temp = self.body_temp_box.value()
        age = self.age_box.value()
        weight = self.weight_box.value()
        height = self.height_box.value()
        bmi = self.calculate_bmi()
        
        # Validate input
        if not calories or not distance:
            QMessageBox.warning(self, "Error", "Please enter calories and distance")
            return
            
        try:
            calories = float(calories)
            distance = float(distance)
        except ValueError:
            QMessageBox.warning(self, "Error", "Calories and distance must be numbers")
            return
            
        query = QSqlQuery()
        query.prepare("""
            INSERT INTO fitness(date, calories, distance, heart_rate, body_temp, age, weight, height, bmi, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """)
        query.addBindValue(date)
        query.addBindValue(calories)
        query.addBindValue(distance)
        query.addBindValue(heart_rate)
        query.addBindValue(body_temp)
        query.addBindValue(age)
        query.addBindValue(weight)
        query.addBindValue(height)
        query.addBindValue(bmi)
        query.addBindValue(description)
            
        if not query.exec_():
            QMessageBox.warning(self, "Error", "Failed to add workout: " + query.lastError().text())
            return
            
        self.kal_box.clear()
        self.distance_box.clear()
        self.description.clear()
            
        self.load_table()
        self.update_stats()
        self.update_mini_chart()
        QMessageBox.information(self, "Success", "Workout added successfully!")

    # Delete Workout
    def delete_workout(self):
        selected_row = self.table.currentRow()
            
        if selected_row == -1:
            QMessageBox.warning(self, "Error", "Please choose a row to delete")
            return
            
        fit_id = int(self.table.item(selected_row, 0).text())
        confirm = QMessageBox.question(self, "Confirm Delete",
                                    "Are you sure you want to delete this workout?",
                                    QMessageBox.Yes | QMessageBox.No)
            
        if confirm == QMessageBox.No:
            return
            
        query = QSqlQuery()
        query.prepare("DELETE FROM fitness WHERE id = ?")
        query.addBindValue(fit_id)
            
        if not query.exec_():
            QMessageBox.warning(self, "Error", "Failed to delete workout: " + query.lastError().text())
            return
            
        self.load_table()
        self.update_stats()
        self.update_mini_chart()
        QMessageBox.information(self, "Success", "Workout deleted successfully!")

    # Update Stats
    def update_stats(self):
        # Run queries to get stats
        query = QSqlQuery("SELECT COUNT(*) FROM fitness")
        total_workouts = 0
        if query.next():
            total_workouts = query.value(0)
        
        query = QSqlQuery("SELECT SUM(distance), SUM(calories), AVG(heart_rate), MAX(distance), AVG(bmi) FROM fitness")
        total_distance = 0
        total_calories = 0
        avg_heart_rate = 0
        max_distance = 0
        avg_bmi = 0
        
        if query.next():
            total_distance = query.value(0) or 0
            total_calories = query.value(1) or 0
            avg_heart_rate = query.value(2) or 0
            max_distance = query.value(3) or 0
            avg_bmi = query.value(4) or 0
        
        # Update labels
        self.total_workouts.setText(f"Total Workouts: {total_workouts}")
        self.total_distance.setText(f"Total Distance: {total_distance:.1f} km")
        self.total_calories.setText(f"Total Calories: {total_calories:.0f}")
        self.avg_heart_rate.setText(f"Avg Heart Rate: {avg_heart_rate:.1f} bpm")
        self.max_distance.setText(f"Longest Workout: {max_distance:.1f} km")
        self.avg_bmi.setText(f"Average BMI: {avg_bmi:.1f}")
    
    # Update Mini Chart
    def update_mini_chart(self):
        self.mini_figure.clear()
        
        # Get last 7 days of data
        seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        query = QSqlQuery()
        query.prepare("SELECT date, calories FROM fitness WHERE date >= ? ORDER BY date")
        query.addBindValue(seven_days_ago)
        
        dates = []
        calories = []
        
        if query.exec_():
            while query.next():
                dates.append(query.value(0))
                calories.append(float(query.value(1)))
        
        if not dates:
            # No data
            ax = self.mini_figure.add_subplot(111)
            ax.text(0.5, 0.5, "No data for last 7 days", ha='center', va='center')
            ax.set_axis_off()
        else:
            # Create mini bar chart
            ax = self.mini_figure.add_subplot(111)
            ax.bar(dates, calories, color='#4CAF50')
            ax.set_title("Calories - Last 7 Days")
            ax.set_xticklabels(dates, rotation=45)
            self.mini_figure.tight_layout()
        
        self.mini_canvas.draw()

    # Generate Chart
    def generate_chart(self):
        # Clear previous plot
        self.figure.clear()
        
        # Get selected chart type and time range
        chart_type = self.chart_type.currentText()
        time_range = self.time_range.currentText()
        
        # Determine the date cutoff based on time range
        cutoff_date = None
        
        if time_range == "Last 7 Days":
            cutoff_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        elif time_range == "Last 30 Days":
            cutoff_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        elif time_range == "Last 90 Days":
            cutoff_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
        
        # Execute query based on time range
        query = QSqlQuery()
        
        if cutoff_date:
            query.prepare("SELECT * FROM fitness WHERE date >= ? ORDER BY date")
            query.addBindValue(cutoff_date)
        else:
            query.prepare("SELECT * FROM fitness ORDER BY date")
        
        # Extract data
        dates = []
        calories_data = []
        distances = []
        heart_rates = []
        body_temps = []
        bmis = []
        
        if query.exec_():
            while query.next():
                dates.append(query.value(1))
                calories_data.append(float(query.value(2) or 0))
                distances.append(float(query.value(3) or 0))
                heart_rates.append(int(query.value(4) or 0))
                body_temps.append(float(query.value(5) or 0))
                bmis.append(float(query.value(9) or 0))
        
        if not dates:
            # No data
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, "No data available for the selected time range", ha='center', va='center')
            ax.set_axis_off()
            self.canvas.draw()
            return
        
        try:
            if chart_type == "Calories Over Time":
                ax = self.figure.add_subplot(111)
                ax.plot(dates, calories_data, 'o-', color='#4CAF50', linewidth=2, markersize=8)
                ax.set_title("Calories Burned Over Time")
                ax.set_xlabel("Date")
                ax.set_ylabel("Calories Burned")
                ax.grid(True, linestyle='--', alpha=0.7)
                
                # Mark average line
                avg_calories = sum(calories_data) / len(calories_data)
                ax.axhline(y=avg_calories, color='r', linestyle='--', alpha=0.7)
                ax.text(dates[0], avg_calories, f"  Avg: {avg_calories:.1f}", color='r')
                
            elif chart_type == "Distance Over Time":
                ax = self.figure.add_subplot(111)
                ax.plot(dates, distances, 'o-', color='#2196F3', linewidth=2, markersize=8)
                ax.set_title("Distance Over Time")
                ax.set_xlabel("Date")
                ax.set_ylabel("Distance (km)")
                ax.grid(True, linestyle='--', alpha=0.7)
                
                # Trend line
                z = np.polyfit(range(len(dates)), distances, 1)
                p = np.poly1d(z)
                ax.plot(dates, p(range(len(dates))), "r--", alpha=0.7)
                
            elif chart_type == "Heart Rate Trends":
                ax = self.figure.add_subplot(111)
                ax.plot(dates, heart_rates, 'o-', color='#F44336', linewidth=2, markersize=8)
                ax.set_title("Heart Rate Trends")
                ax.set_xlabel("Date")
                ax.set_ylabel("Heart Rate (bpm)")
                ax.grid(True, linestyle='--', alpha=0.7)
                
                # Reference zones
                ax.axhspan(40, 60, alpha=0.2, color='blue', label='Resting')
                ax.axhspan(60, 100, alpha=0.2, color='green', label='Normal')
                ax.axhspan(100, 140, alpha=0.2, color='orange', label='Moderate')
                ax.axhspan(140, 180, alpha=0.2, color='red', label='Intense')
                ax.legend()
                
            elif chart_type == "BMI Tracking":
                ax = self.figure.add_subplot(111)
                ax.plot(dates, bmis, 'o-', color='#9C27B0', linewidth=2, markersize=8)
                ax.set_title("BMI Over Time")
                ax.set_xlabel("Date")
                ax.set_ylabel("BMI")
                ax.grid(True, linestyle='--', alpha=0.7)
                
                # Reference zones
                ax.axhspan(0, 18.5, alpha=0.2, color='blue', label='Underweight')
                ax.axhspan(18.5, 25, alpha=0.2, color='green', label='Normal')
                ax.axhspan(25, 30, alpha=0.2, color='orange', label='Overweight')
                ax.axhspan(30, 40, alpha=0.2, color='red', label='Obese')
                ax.legend()
                
            elif chart_type == "Workout Distribution":
                ax = self.figure.add_subplot(111)
                
                # Group distances into categories
                distance_bins = {"0-2 km": 0, "2-5 km": 0, "5-10 km": 0, "10+ km": 0}
                
                for d in distances:
                    if d < 2:
                        distance_bins["0-2 km"] += 1
                    elif d < 5:
                        distance_bins["2-5 km"] += 1
                    elif d < 10:
                        distance_bins["5-10 km"] += 1
                    else:
                        distance_bins["10+ km"] += 1
                
                # Plot pie chart
                labels = list(distance_bins.keys())
                sizes = list(distance_bins.values())
                
                # Only plot non-zero values
                non_zero_labels = [labels[i] for i in range(len(sizes)) if sizes[i] > 0]
                non_zero_sizes = [size for size in sizes if size > 0]
                
                if non_zero_sizes:
                    ax.pie(non_zero_sizes, labels=non_zero_labels, autopct='%1.1f%%',
                          shadow=True, startangle=90)
                    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
                    ax.set_title("Workout Distance Distribution")
                else:
                    ax.text(0.5, 0.5, "No distance data available", ha='center', va='center')
                    ax.set_axis_off()
                    
            elif chart_type == "Health Metrics Correlation":
                ax = self.figure.add_subplot(111)
                
                # Scatter plot with size based on calories
                scatter = ax.scatter(distances, heart_rates, 
                                   s=[c/10 for c in calories_data],  # Size based on calories
                                   c=body_temps, cmap='viridis',     # Color based on body temp
                                   alpha=0.7)
                
                ax.set_title("Health Metrics Correlation")
                ax.set_xlabel("Distance (km)")
                ax.set_ylabel("Heart Rate (bpm)")
                ax.grid(True, linestyle='--', alpha=0.3)
                
                # Add colorbar
                cbar = self.figure.colorbar(scatter)
                cbar.set_label('Body Temperature (°C)')
                
                # Add annotations for notable points
                for i, (x, y) in enumerate(zip(distances, heart_rates)):
                    if y == max(heart_rates) or x == max(distances):
                        ax.annotate(f"{dates[i]}", (x, y), 
                                   xytext=(5, 5), textcoords='offset points')
                
            elif chart_type == "Weekly Summary":
                # Convert string dates to datetime objects
                date_objects = [datetime.strptime(d, "%Y-%m-%d") for d in dates]
                
                # Get the week number for each date
                week_numbers = [d.isocalendar()[1] for d in date_objects]
                
                # Group data by week
                weeks = sorted(set(week_numbers))
                weekly_calories = [0] * len(weeks)
                weekly_distances = [0] * len(weeks)
                
                for i, week in enumerate(weeks):
                    for j, w in enumerate(week_numbers):
                        if w == week:
                            weekly_calories[i] += calories_data[j]
                            weekly_distances[i] += distances[j]
                
                # Create two subplots
                ax1 = self.figure.add_subplot(211)
                ax2 = self.figure.add_subplot(212)
                
                # Plot weekly calories
                ax1.bar(range(len(weeks)), weekly_calories, color='#FF9800')
                ax1.set_title("Weekly Calories Burned")
                ax1.set_ylabel("Calories")
                ax1.set_xticks(range(len(weeks)))
                ax1.set_xticklabels([f"Week {w}" for w in weeks])
                
                # Plot weekly distances
                ax2.bar(range(len(weeks)), weekly_distances, color='#2196F3')
                ax2.set_title("Weekly Distance")
                ax2.set_ylabel("Distance (km)")
                ax2.set_xticks(range(len(weeks)))
                ax2.set_xticklabels([f"Week {w}" for w in weeks])
                
                self.figure.tight_layout()
            
            # For all chart types, adjust the x-axis labels
            if chart_type != "Workout Distribution" and chart_type != "Health Metrics Correlation" and chart_type != "Weekly Summary":
                plt.xticks(rotation=45)
            
            self.figure.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            QMessageBox.warning(self, "Chart Error", f"Error generating chart: {str(e)}")
            
    # Reset fields
    def reset(self):
        self.date_box.setDate(QDate.currentDate())
        self.kal_box.clear()
        self.distance_box.clear()
        self.description.clear()
        self.heart_rate_box.setValue(70)
        self.body_temp_box.setValue(36.6)
        self.age_box.setValue(30)
        self.weight_box.setValue(70.0)
        self.height_box.setValue(170.0)
        self.bmi_result.setText("BMI: Not calculated")
    
    # Toggle dark mode
    def toggle_dark(self, state):
        if state:
            # Dark mode
            self.apply_dark_theme()
        else:
            # Light mode
            self.apply_light_theme()
    
    # Apply dark theme
    def apply_dark_theme(self):
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)
        
        self.setPalette(dark_palette)
        
        # Set style sheet for additional elements
        self.setStyleSheet("""
            QGroupBox { 
                border: 1px solid gray; 
                border-radius: 5px; 
                margin-top: 10px; 
                font-weight: bold;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
            }
            QTableWidget {
                gridline-color: #5c5c5c;
            }
            QHeaderView::section {
                background-color: #3a3a3a;
                color: white;
                padding: 5px;
                border: 1px solid #5c5c5c;
            }
            QPushButton {
                background-color: #0D47A1;
                color: white;
                border-radius: 4px;
                padding: 5px;
                min-height: 25px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        
        # Set matplotlib style
        plt.style.use('dark_background')
        self.update_mini_chart()
        self.canvas.draw()
    
    # Apply light theme
    def apply_light_theme(self):
        self.setPalette(self.style().standardPalette())
        
        # Set style sheet for additional elements
        self.setStyleSheet("""
            QGroupBox { 
                border: 1px solid gray; 
                border-radius: 5px; 
                margin-top: 10px; 
                font-weight: bold;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
            }
            QTableWidget {
                gridline-color: #d0d0d0;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 5px;
                border: 1px solid #d0d0d0;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border-radius: 4px;
                padding: 5px;
                min-height: 25px;
            }
            QPushButton:hover {
                background-color: #64B5F6;
            }
            QPushButton:pressed {
                background-color: #1976D2;
            }
        """)
        
        # Set matplotlib style
        plt.style.use('default')
        self.update_mini_chart()
        self.canvas.draw()
    
    # Apply styles based on current theme
    def apply_styles(self):
        if self.dark_mode.isChecked():
            self.apply_dark_theme()
        else:
            self.apply_light_theme()

# Main execution
if __name__ == "__main__":
    # Create application
    app = QApplication(sys.argv)
    
    # Set application icon
    app.setWindowIcon(QIcon('fitness.ico'))
    
    # Create database connection
    db = QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName("fitness.db")
    
    if not db.open():
        QMessageBox.critical(None, "Database Error", 
                           "Could not open database file: " + db.lastError().text())
        sys.exit(1)
    
    # Create and show window
    window = FitTrack()
    window.show()
    
    # Execute application
    sys.exit(app.exec_())