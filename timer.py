from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import QTimer
from sqlalchemy import create_engine, Column, Integer, String, distinct
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import time
import sys

Base = declarative_base()

class TimeEntry(Base):
    __tablename__ = 'time_entries'
    id = Column(Integer, primary_key=True)
    category = Column(String)
    time_spent_mins = Column(Integer)

engine = create_engine('sqlite:///time_tracker.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def get_distinct_categories():
    categories = session.query(TimeEntry.category).distinct().all()
    return [category[0] for category in categories]

class TimeTrackerApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.start_time = None

    def initUI(self):
        self.category_label = QtWidgets.QLabel('Category:', self)
        self.category_input = QtWidgets.QComboBox(self)
        self.category_input.setEditable(True)
        self.start_button = QtWidgets.QPushButton('Start', self)
        self.stop_button = QtWidgets.QPushButton('Stop', self)
        self.time_display = QtWidgets.QLabel('00:00:00', self)

        # Populate the combobox with categories from the database
        self.populate_combobox()
        
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.category_label)
        self.layout.addWidget(self.category_input)
        self.layout.addWidget(self.start_button)
        self.layout.addWidget(self.stop_button)
        self.layout.addWidget(self.time_display)
        self.setLayout(self.layout)

        self.start_button.clicked.connect(self.start_timer)
        self.stop_button.clicked.connect(self.stop_timer)

        self.setWindowTitle('Time Tracker')
        self.show()

    def populate_combobox(self):
        categories = get_distinct_categories()
        self.category_input.addItems(categories)

    def start_timer(self):
        self.start_time = time.time()
        self.timer.start(1000)  # Update every second

    def stop_timer(self):
        self.timer.stop()
        elapsed_time = time.time() - self.start_time
        time_spent_mins = self.round_to_next_5_minutes(elapsed_time)
        self.save_time(self.category_input.currentText(), time_spent_mins)
        self.start_time = None
        self.time_display.setText('00:00:00')

    def update_time(self):
        elapsed_time = time.time() - self.start_time
        self.time_display.setText(self.format_time(elapsed_time))

    def format_time(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

    def save_time(self, category, time_spent_mins):
        new_entry = TimeEntry(category=category, time_spent_mins=time_spent_mins)
        session.add(new_entry)
        session.commit()

    def round_to_next_5_minutes(self, seconds):
        minutes = seconds / 60
        rounded_minutes = max((minutes + 4) // 5 * 5, 5)  # Round up to the next 5 minutes
        return rounded_minutes

def main():
    app = QtWidgets.QApplication(sys.argv)
    ex = TimeTrackerApp()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
