from PyQt6.QtWidgets import (QWidget, QVBoxLayout,
                             QPushButton, QLabel,
                             QDialog, QHBoxLayout, QSpinBox,
                             QTimeEdit, QFrame)


from PyQt6.QtCore import Qt


class TimeSettingsWindow(QDialog):
    def __init__(self, default_freq_value, default_start_time,
                 default_stop_time,
                 parent=None):
        super().__init__(parent)
        
        
        
        self.default_start_time = default_start_time
        self.default_stop_time = default_stop_time
        
        self.default_freq_value = default_freq_value

        
        line = QFrame(self)
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        
        spacer = QWidget(self)
        
        self.header_1 = QLabel('Update frequency')
        self.header_1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header_2 = QLabel('Update period')
        self.header_2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.update_freq_label = QLabel('Update every (min)')
        self.update_period_start_label = QLabel('From')
        self.update_period_stop_label = QLabel('To')

        self.update_freq = QSpinBox(self)

        self.update_freq.setMinimum(1)
        self.update_freq.setMaximum(360)
        self.update_freq.setSingleStep(20)
        self.update_freq.setValue(self.default_freq_value)

        self.update_period_start = QTimeEdit(self)
        self.update_period_start.setTime(self.default_start_time)
        
        self.update_period_stop = QTimeEdit(self)
        self.update_period_stop.setTime(self.default_stop_time)

        self.confirm_button = QPushButton('Ok', self)
        self.confirm_button.clicked.connect(self.ok_button)
        self.cancel_button = QPushButton('Cancel', self)
        self.cancel_button.clicked.connect(self.c_button)


        main_layout = QVBoxLayout(self)

        form_layout = QHBoxLayout()
        to_layout = QHBoxLayout()
        freq_layout = QHBoxLayout()
        button_layout = QHBoxLayout()


        freq_layout.addWidget(self.update_freq_label)
        freq_layout.addWidget(self.update_freq)
        
        
        form_layout.addWidget(self.update_period_start_label)
        form_layout.addWidget(self.update_period_start)
        
        
        to_layout.addWidget(self.update_period_stop_label)
        to_layout.addWidget(self.update_period_stop)


        button_layout.addWidget(self.confirm_button)
        button_layout.addWidget(self.cancel_button)


        
        main_layout.addWidget(self.header_1)
        main_layout.addLayout(freq_layout)
        
        main_layout.addWidget(line)
        main_layout.addWidget(self.header_2)
        main_layout.addLayout(form_layout)
        main_layout.addLayout(to_layout)
        
        main_layout.addWidget(spacer)
        main_layout.addLayout(button_layout)

        self.setWindowTitle('Timer settings')

        self.accepted = False  # Устанавливаем флаг в False
        self.move(100, 100)

    def get_params(self):
        freq_value = self.update_freq.value()
        start_time = self.update_period_start.time()
        stop_time = self.update_period_stop.time()
        return freq_value, start_time, stop_time
        

    def ok_button(self):

        self.default_start_time = self.update_period_start.time()
        self.default_stop_time = self.update_period_stop.time()
        self.default_freq_value = self.update_freq.value()
        self.accepted = True 
        self.accept()

    def c_button(self):

        self.update_period_start.setTime(self.default_start_time)
        self.update_period_stop.setTime(self.default_stop_time)
        self.update_freq.setValue(self.default_freq_value)
        self.accepted = False 
        self.reject()
        
        
    def closeEvent(self, event):
        if event.spontaneous() and not self.result():
            self.c_button()