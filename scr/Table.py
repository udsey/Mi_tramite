from PyQt6.QtGui import QBrush, QColor, QFont
from PyQt6 import QtCore
from PyQt6.QtCore import Qt

from PyQt6.QtWidgets import QTableView

class TableModel(QtCore.QAbstractTableModel):

    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)
        if role == Qt.ItemDataRole.BackgroundRole:
            # Set different colors for even and odd rows
            if index.row() % 2 == 0:
                return QBrush(QColor("#FCF2E5"))

            else:
                return QBrush(QColor("#E2EEF7"))

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(self._data.columns[section])

            if orientation == Qt.Orientation.Vertical:
                return str(self._data.index[section])
            
        if role == Qt.ItemDataRole.BackgroundRole:
            # Set header background color
            return QBrush(QColor("#295373"))  # Light gray

        if role == Qt.ItemDataRole.ForegroundRole:
            return QColor('#FCF2E5')
        
        if role == Qt.ItemDataRole.FontRole:
            # Set header font to bold
            font = QFont()
            font.setBold(True)
            return font
        
    def removeRows(self, position, rows, parent=None):
        self.beginRemoveRows(parent, position, position + rows - 1)
        self._data.drop(self._data.index[position:position+rows], inplace=True)
        self.endRemoveRows()
        return True    


class EditableTableView(QTableView):
    def __init__(self, model):
        super(EditableTableView, self).__init__()
        self.setModel(model)
        self.setEditTriggers(QtCore.QAbstractItemView.EditTrigger.DoubleClicked)
 