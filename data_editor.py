import sys
import os
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QLabel, QLineEdit, QCheckBox, QAbstractItemView
)

class DataEditor(QWidget):
    def __init__(self, json_file):
        super().__init__()
        self.json_file = json_file
        self.data = self.load_data()
        self.property_columns = {}
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Data Editor')
        layout = QVBoxLayout()

        # Horizontal layout for new property inputs
        prop_layout = QHBoxLayout()
        self.prop_name_input = QLineEdit()
        self.prop_value_input = QLineEdit()
        self.apply_button = QPushButton('Apply to Selected')
        self.apply_button.clicked.connect(self.apply_properties)

        prop_layout.addWidget(QLabel('Property Name:'))
        prop_layout.addWidget(self.prop_name_input)
        prop_layout.addWidget(QLabel('Property Value:'))
        prop_layout.addWidget(self.prop_value_input)
        prop_layout.addWidget(self.apply_button)

        layout.addLayout(prop_layout)

        # Table for data display and editing
        self.table = QTableWidget()
        self.table.setColumnCount(3)  # Start with three columns for 'Select', 'GUID', and 'Name'
        self.table.setHorizontalHeaderLabels(['Select', 'GUID', 'Name'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        layout.addWidget(self.table)

        # Save button
        save_button = QPushButton('Save Changes')
        save_button.clicked.connect(self.save_changes)
        layout.addWidget(save_button)

        self.setLayout(layout)
        self.populate_table()

    def load_data(self):
        with open(self.json_file, 'r') as file:
            data = json.load(file)
        return data

    def populate_table(self):
        row_count = sum(len(items) for items in self.data.values())
        self.table.setRowCount(row_count)
        row_idx = 0
        for file_key, entries in self.data.items():
            for entry in entries:
                chk_box = QCheckBox()
                self.table.setCellWidget(row_idx, 0, chk_box)

                guid_str = str(entry.get('guid', '')) if entry.get('guid') is not None else ''
                self.table.setItem(row_idx, 1, QTableWidgetItem(guid_str))
                
                name_str = str(entry.get('name', '')) if entry.get('name') is not None else ''
                self.table.setItem(row_idx, 2, QTableWidgetItem(name_str))

                # Skip last column which seems to be unnecessary based on your requirement
                for i, (prop_name, prop_value) in enumerate(entry['properties'].items()):
                    if i < len(entry['properties']) - 1:  # Skip last column
                        col_idx = 3 + i
                        while col_idx >= self.table.columnCount():
                            self.table.insertColumn(self.table.columnCount())
                        self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(prop_value)))
                        self.property_columns[prop_name] = col_idx
                row_idx += 1

    def apply_properties(self):
        prop_name = self.prop_name_input.text().strip()
        prop_value = self.prop_value_input.text().strip()
        if prop_name and prop_value:
            if prop_name not in self.property_columns:
                col_idx = self.table.columnCount()
                self.property_columns[prop_name] = col_idx
                self.table.insertColumn(col_idx)
                self.table.setHorizontalHeaderLabels(self.table.horizontalHeaderLabels() + [prop_name])
            else:
                col_idx = self.property_columns[prop_name]
            for row in range(self.table.rowCount()):
                if self.table.cellWidget(row, 0).isChecked():
                    self.table.setItem(row, col_idx, QTableWidgetItem(prop_value))

    def save_changes(self):
        # Logic to save changes back to files
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    data_folder = r"C:\Users\LouisTrümpler\Dropbox\01_Projekte\2309 Pi\240423_Excel Attribut export test\240423_Excel Attribut export test\combined_data.json" # replace with your actual data folder path
    ex = DataEditor(data_folder)
    ex.show()
    sys.exit(app.exec_())
