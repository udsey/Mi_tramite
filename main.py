import sys
import PyQt6
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout,
                             QPushButton, QLabel,
                             QSystemTrayIcon, QMenuBar, QMenu, QComboBox,
                             QDialog, QLineEdit, QHBoxLayout, QSpinBox,
                             QTimeEdit, QFrame, QMainWindow, QDockWidget,
                             QTextBrowser, QTableView)

from PyQt6.QtCore import QTimer, QTime, QSize
from PyQt6.QtGui import QIcon, QAction
from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt

from plyer import notification
from time import strftime, localtime
import pandas as pd
from pygame import mixer
from scr.check_tramite import check_tramites, test_check_tramites
import os
from PyQt6.QtGui import QPixmap
import configparser

from scr.Table import TableModel
from scr.TimeSettings import TimeSettingsWindow
from scr.Edit import EditTable
import argparse


class MyApp(QMainWindow):
    
    def __init__(self, test):
        
        super().__init__()
        self.init_ui(test) 


    def init_ui(self, test):
        
        self.main_dir = os.getcwd() + '/'
        mixer.init()
        
        # Loading config file
        config = configparser.ConfigParser()
        config.read(self.main_dir +'data/config.ini')
    
        # Loading settings and df
        self.work_start_time = eval(config.get('TimeSettings', "work_start_time"))
        self.work_end_time  = eval(config.get('TimeSettings', "work_end_time"))
        self.interval_minutes = int(config.get('TimeSettings', "interval_minutes"))
        self.test = test
        self.silent = True
        self.allow_notification = True
        self.parameter_dialog = None
        
        # Widget: Update info
        self.info_text = QTextBrowser(self)
        self.info_text.setStyleSheet("background-color: #FCF2E5; font-size: 15px;")
        
        # Last update time label
        self.additional_label = QLabel(self)
        self.additional_label.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
        self.additional_label.setStyleSheet("background-color: #FCF2E5; font-size: 12px;")

        # Loading cat's picture
        image_label = QLabel(self)
        pixmap = QPixmap(self.main_dir + '/content/cat.png')
        scaled_pixmap = pixmap.scaled(70, 70, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        image_label.setPixmap(scaled_pixmap)
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Frame: Text info
        self.frame = QFrame(self)
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.frame.setStyleSheet("background-color: #FCF2E2; border-radius: 10px;")                  
        self.frame.setLineWidth(2)
        self.frame.setMidLineWidth(2)
        self.frame.setFrameShape(QFrame.Shape.Box)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.frame.setFixedHeight(100)
        
        # Building text frame layout 
        frame_layout = QHBoxLayout(self.frame)
        frame_layout.addWidget(image_label)
        text_layout = QVBoxLayout(self.frame)
        text_layout.addWidget(self.info_text)
        text_layout.addWidget(self.additional_label, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
        frame_layout.addLayout(text_layout)
        
        # Table view
        self.table = QtWidgets.QTableView()
        self.table.setStyleSheet("QTableView { border: none; }")
        self.table.setFixedWidth(315)
        self.update_table()
        
        # Init timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_status)
        
        # Menu bar
        self.menu = QMenuBar()
        self.menu.setStyleSheet(":item:selected { \
                                background-color: #E2EEF7;\
                                color: black}")

        ## Edit action
        self.edit_table = self.menu.addAction('Edit')
        self.edit_table.triggered.connect(self.show_edit_settings)
        
        ## Settings actions
        self.settings_menu = self.menu.addMenu('Settings') 
        ### Notifications
        self.notification_action = QAction('Allow notification', self)
        self.notification_action.setCheckable(True)
        self.notification_action.setChecked(True)
        self.notification_action.triggered.connect(self.notification_func)
        ### Silent mode
        self.silent_action = QAction('Silent mode', self)
        self.silent_action.setCheckable(True)
        self.silent_action.setChecked(True)
        self.silent_action.triggered.connect(self.silent_func)
        ### Time settings
        self.time_settings = self.settings_menu.addAction('Timer settings')
        self.time_settings.triggered.connect(self.show_timer_settings)
        
        ## Building settings menu       
        self.settings_menu.addAction(self.silent_action)
        self.settings_menu.addAction(self.notification_action)

        
        # Update button
        self.update_button = QPushButton('Check', self)
        self.update_button.setFixedSize(100, 40)
        self.update_button.setStyleSheet(
                                        '''
                                        QPushButton {
                                            background-color: #FCF2E5;
                                            border-radius: 10px;
                                            font-size: 16px;
                                            border: 1px solid #A39D94;
                                        }
                                        QPushButton:pressed {
                                            background-color: #A39D94;
                                        }
                                        ''')
        self.update_button.clicked.connect(self.check_status)
        
        # Building central widget
        self.central_widget = QWidget(self)
        self.central_widget.setStyleSheet("background-color: #F5F5F5")

        # Create layout
        layout = QVBoxLayout(self.central_widget)
        layout.addWidget(self.menu)
        layout.addWidget(self.frame)
        layout.addSpacing(15)
        layout.addWidget(self.table, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(5)
        button_layout = QHBoxLayout(self.central_widget)
        layout.addLayout(button_layout)
        layout.addSpacing(15)
        button_layout.addWidget(self.update_button)

        # Set app data
        self.setCentralWidget(self.central_widget)
        self.app_name = 'My tramite'
        self.setWindowIcon(QIcon(self.main_dir + '/content/app.png'))
        self.setFixedSize(QSize(400, 350))
        self.setWindowTitle(self.app_name)
        self.tray_icon = QSystemTrayIcon(QIcon(self.main_dir + '/content/app.png'), self)
        self.tray_icon.show()

        # First update
        self.check_status()
        self.timer.start(self.interval_minutes * 60 * 1000)
        
        
    def update_status(self):
        # Run function from start time to stop time
        current_time = QTime.currentTime()

        if self.work_start_time <= current_time <= self.work_end_time:
            self.info_text.clear()
            self.additional_label.clear()
            print('Work time. Updating status.')
            self.check_status()
        else:
            print('Out of work time. Update was skipped.')


    def show_notification(self, alert):
        notification.notify(title='Tramite update!',message=alert,
                            timeout=10
                            )
        # Play notification sound
        if not self.silent:
            mixer.music.load(self.main_dir + '/content/notification.wav') 
            mixer.music.play()


    def check_status(self):
        
        self.info_text.setPlainText("Updating.........")
        QApplication.processEvents()
        
        if self.test:
            keys_df, flag, alert = test_check_tramites(self.main_dir)
        else:    
            keys_df, flag, alert = check_tramites(self.main_dir)
            
        self.info_text.setText(alert)
        self.additional_label.setText(strftime("%d/%m/%y %H:%M", localtime()))
        
        if flag:
            self.update_table()
            if self.allow_notification:
                self.show_notification(alert)
           
    def notification_func(self):
        if self.notification_action.isChecked():
            self.allow_notification = True
            print('Notification allowed')
        else:
            self.allow_notification = False
            print('Notification prohibited')
            
    def silent_func(self):
        if self.silent_action.isChecked():
            self.silent = True
            print('Silent mode')
        else:
            self.silent = False
            print('Play audio notification')
            
    def on_interval_changed(self):
        self.timer.start(self.interval_minutes * 60 * 1000)
        print(f'Next interval was chosen: {self.interval_minutes} min')
        
    def show_timer_settings(self):
        if self.parameter_dialog is None:
            self.parameter_dialog = TimeSettingsWindow(self.interval_minutes,
                                                       self.work_start_time,
                                                       self.work_end_time)

        self.parameter_dialog.exec()
        freq_value, start_time, stop_time = self.parameter_dialog.get_params()
        
        flag = 0
        if freq_value != self.interval_minutes:
            self.interval_minutes = freq_value
            self.on_interval_changed()
            flag = 1
            
        if start_time != self.work_start_time:
            self.work_start_time = start_time
            flag = 1
            
            print(f'Start time was updeted to {start_time}')
            
        if stop_time != self.work_end_time:
            self.work_end_time = stop_time
            flag = 1 
            print(f'End time was updeted to {stop_time}')
            
        if flag == 1:
            self.save_config(interval_minutes=self.interval_minutes,
                             work_start_time = self.work_start_time,
                             work_end_time = self.work_end_time)
        
    def show_edit_settings(self):
        edit_table = EditTable(self.main_dir, self.test)
        edit_table.exec()
        self.update_table()
        
        
    def save_config(self, **kwargs):
         config = configparser.ConfigParser()
         config['TimeSettings'] = {key:value for key, value in kwargs.items()}
         with open(self.main_dir + 'data/config.ini', 'w') as configfile:
             config.write(configfile)
             
             
    def update_table(self):
        self.keys_df = pd.read_csv(self.main_dir + 'data/id_data.csv')
        self.model = TableModel(self.keys_df)
        self.table.setModel(self.model)
        self.table.reset()

             

        
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='My Tramite Application')
    parser.add_argument('-t', 
                        '--test-mode', 
                        action='store_true',
                        help="Act in test mode. Don't send requests to renaper page" )
    args = parser.parse_args()
    test = args.test_mode
    app = QApplication(sys.argv)
    window = MyApp(test)
    window.show()
    sys.exit(app.exec())
