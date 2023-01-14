import math

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, \
    QTableWidgetItem, QHeaderView
from PyQt5.QtCore import pyqtSlot, Qt
import sys

import database
from ui import Ui_MainWindow
from subui import Ui_SubWindow

data = {}


def to_none(value):
    if type(value) is float:
        if math.isnan(value):
            return None
    else:
        return value


class Demo(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(Demo, self).__init__(parent)
        self.setupUi(self)
        self.init()

    def init(self):
        self.tableWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.line_id.setPlaceholderText("Please enter a word")

    def insert_row(self, row, pos, derivational_prefix, derivational_suffix, root, inflectional_suffix,
                   inflectional_type):
        pos_item = QTableWidgetItem(pos)
        derivational_prefix_item = QTableWidgetItem(derivational_prefix)
        derivational_suffix = QTableWidgetItem(derivational_suffix)
        root_item = QTableWidgetItem(root)

        inflectional_suffix_item = QTableWidgetItem(inflectional_suffix)
        inflectional_type_item = QTableWidgetItem(inflectional_type)
        self.tableWidget.insertRow(row)
        self.tableWidget.setItem(row, 0, pos_item)
        self.tableWidget.setItem(row, 1, derivational_prefix_item)
        self.tableWidget.setItem(row, 2, derivational_suffix)
        self.tableWidget.setItem(row, 3, root_item)

        self.tableWidget.setItem(row, 4, inflectional_suffix_item)
        self.tableWidget.setItem(row, 5, inflectional_type_item)

    @pyqtSlot()
    def on_button_search_clicked(self):

        self.tableWidget.setRowCount(0)
        self.tableWidget.clearContents()

        word = self.line_id.text()
        if not word:
            QMessageBox.critical(self, "Warning", "Please enter a word!")
            return
        global gl_word
        gl_word = word
        global gl_root
        try:
            data = database.get_data(word)
            if data["root_table"]:
                gl_root = data["root_table"]
            if data["word_table"]:
                results = data["word_table"]
                for item in results:
                    pos = to_none(item["pos"])
                    derivational_prefix = to_none(item["derivationa_prefix"])
                    derivational_suffix = to_none(item["root"])
                    root = to_none(item["derivational_suffix"])
                    inflectional_suffix = to_none(item["inflectional_suffix"])
                    inflectional_type = to_none(item["inflectional_type"])

                    row = self.tableWidget.rowCount()
                    self.insert_row(row, pos, derivational_prefix, derivational_suffix, root, inflectional_suffix,
                                    inflectional_type)
            else:
                QMessageBox.critical(self, "Wrong", "The word does not exist!")

        except:
            QMessageBox.critical(self, "Wrong", "Data error:check file existence or encoding for UTF-8!")

    @pyqtSlot()
    def on_button_add_clicked(self):
        """触发关系词图"""
        self.button_add.clicked.connect(self.show_child)

    def show_child(self):
        self.child_window = childWindow()
        self.child_window.show()


class childWindow(QMainWindow, Ui_SubWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.init()

    def init(self):
        self.tableWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def insert_row(self, row, pos, root):
        pos_item = QTableWidgetItem(pos)
        root_item = QTableWidgetItem(root)

        self.tableWidget.insertRow(row)
        self.tableWidget.setItem(row, 0, pos_item)
        self.tableWidget.setItem(row, 1, root_item)

    @pyqtSlot()
    def on_button_search_clicked(self):

        # word = gl_word
        # print(word)
        try:
            # data = database.data_base_root(word)
            if gl_root:
                results = gl_root
                for item in results:
                    pos = to_none(item["word"])
                    root = to_none(item["root"])
                    row = self.tableWidget.rowCount()
                    self.insert_row(row, pos, root)
            else:
                QMessageBox.critical(self, "Wrong", "The word does not exist!")

        except:
            QMessageBox.critical(self, "Wrong", "Data error:check file existence or encoding for UTF-8!")


if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())
