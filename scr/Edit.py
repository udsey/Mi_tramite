from PyQt6.QtWidgets import (QVBoxLayout,
                             QPushButton, QLabel,
                             QDialog, QHBoxLayout, QLineEdit,
                             QTableView, QMessageBox)
from scr.check_tramite import check_id, test_check_id, update_df
import pandas as pd
from scr.Table import TableModel


class AddUserWindow(QDialog):
    def __init__(self, test, parent=None):
        
        super().__init__(parent)
        self.test = test
        self.main_layout = QVBoxLayout(self)
        self.name_layout = QHBoxLayout(self)
        self.id_layout = QHBoxLayout(self)
        self.button_layout = QHBoxLayout(self)
        
        self.id_label = QLabel('Enter ID: ')
        self.id_input = QLineEdit()
        self.id_input.setFixedSize(100, 20)
       
        self.name_label = QLabel('Enter your name: ')
        self.name_input = QLineEdit()   
        self.name_input.setFixedSize(100, 20)
       
        self.ok_button = QPushButton('OK', self)
        self.ok_button.clicked.connect(self.ok_function)
        self.cancel_button = QPushButton('Cancel', self)       
        self.cancel_button.clicked.connect(self.reject)
        
        
        self.main_layout.addLayout(self.name_layout)
        self.name_layout.addWidget(self.name_label)
        self.name_layout.addWidget(self.name_input)
        self.main_layout.addLayout(self.id_layout)
        self.id_layout.addWidget(self.id_label)
        self.id_layout.addWidget(self.id_input)
        self.main_layout.addLayout(self.button_layout)
        self.button_layout.addWidget(self.ok_button)
        self.button_layout.addWidget(self.cancel_button)

        self.accepted = False
        self.setWindowTitle('Add new ID')
        self.move(100, 100)
    
    def get_params(self):
        return self.name_input.text(), self.id_input.text()
    
    def ok_function(self):
        if self.test:
            if test_check_id(self.id_input.text()):
                self.accepted = True
                self.accept()
                
            else:
                dlg = QMessageBox(self)
                dlg.setWindowTitle("Error")
                dlg.setText("Check your ID!")
                dlg.exec()
                
        else:
            if check_id(self.id_input.text()):
                self.accepted = True
                self.accept()
                
            else:
                dlg = QMessageBox(self)
                dlg.setWindowTitle("Error")
                dlg.setText("Check your ID!")
                dlg.exec()


class EditTable(QDialog):
    def __init__(self, main_dir, test, parent=None):
        super().__init__(parent)

        self.main_dir = main_dir
        self.test = test
        self.table = QTableView()
        self.table.setStyleSheet("QTableView { border: none; }")
        self.table.setFixedWidth(315)
        self.update_table()
        

        self.add_button = QPushButton('Add')
        self.add_button.clicked.connect(self.add_id_func)

        self.delete_button = QPushButton("Delete Rows")
        self.delete_button.clicked.connect(self.delete_selected_rows)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.delete_button)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.table)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        self.setWindowTitle('Edit Table')
        self.move(100, 100)
        
    def add_id_func(self):
        add_id_page = AddUserWindow(self.test)
        add_id_page.exec()
        if add_id_page.accepted:
            name, key = add_id_page.get_params()
            update_df(self.main_dir, name, key)
            self.update_table()
    

    def delete_selected_rows(self):
        selection_model = self.table.selectionModel()
        selected_indexes = selection_model.selectedRows()

        if selected_indexes:
            row_numbers = [index.row() for index in selected_indexes]
            row_numbers.sort(reverse=True)


            self.keys_df.drop(index=row_numbers, inplace=True)
            self.keys_df.to_csv(self.main_dir  + 'data/id_data.csv', index=False)

            self.update_table()
            
    def update_table(self):
        self.keys_df = pd.read_csv(self.main_dir + 'data/id_data.csv')
        self.model = TableModel(self.keys_df)
        self.table.setModel(self.model)
        self.table.reset()