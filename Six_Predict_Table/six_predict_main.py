import math
import os

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, \
    QTableWidgetItem, QHeaderView, QFormLayout, QFileDialog
from PyQt5.QtCore import pyqtSlot, Qt
import sys

import six_predicator_database
from fileui import Ui_MainWindow
from six_predict_table.sub_root_ui import Ui_Sub_Root_Window
from six_predict_table.sub_six_ui import Ui_Sub_Six_Window
from six_predict_table.sub_suffix_ui import Ui_Sub_Suffix_Window
from six_predict_table.sub_ui import Ui_SubWindow


def split_words(word_set):
    word_str = ""
    word_set = list(word_set)
    list_str = [word_set[i:i + 5] for i in range(0, len(word_set), 5)]
    for str_set in list_str:
        word_str = word_str + ",".join(word_sole for word_sole in str_set).rstrip(",") + "\n"
    word_str = word_str.rstrip("\n")
    return word_str


def to_none(value):
    if type(value) is float:
        if math.isnan(value):
            return None
        else:
            return str(value)
    else:
        return str(value)


class Demo(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(Demo, self).__init__(parent)
        self.setupUi(self)
        self.init()

    def init(self):
        self.tableWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def insert_row(self, row, count_sub, count_all, coverage):
        count_sub = QTableWidgetItem(count_sub)
        count_all = QTableWidgetItem(count_all)
        coverage = QTableWidgetItem(coverage)

        self.tableWidget.insertRow(row)
        self.tableWidget.setItem(row, 0, count_sub)
        self.tableWidget.setItem(row, 1, count_all)
        self.tableWidget.setItem(row, 2, coverage)

    def main_window(self):
        self.chose_excel_button.setCheckable(True)
        self.chose_excel_button.clicked.connect(lambda: self.click_find_file_path(self.chose_excel_button))

    @pyqtSlot()
    def click_find_file_path(self, button):
        filename, filetype = QFileDialog.getOpenFileName(self, "Choose a file", os.getcwd(),
                                                         "Text Files(*.txt)")
        if button.text() == "Choose a file":
            try:
                if button.isChecked():
                    res = six_predicator_database.data_base(filename)
                    # print(res)
                    global count_sub_list  # 覆盖词数
                    global res_prefix_list  # 前缀对应频率词汇
                    global res_root_list  # 词根对应频率词汇
                    global res_suffix_list  # 后缀对应频率词汇
                    global all_frame_list  # 输出root 六项指标

                    count_sub_list = res["count_sub_list"]
                    res_prefix_list = res['res_prefix_list']
                    res_root_list = res["res_root_list"]
                    res_suffix_list = res["res_suffix_list"]
                    all_frame_list = res["all_frame_list"]
                    try:
                        if count_sub_list:
                            results = count_sub_list
                            for item in results:
                                count_sub = to_none(item["count_sub"])
                                count_all = to_none(item["count_all"])
                                coverage = to_none(item["coverage"])
                                row = self.tableWidget.rowCount()
                                self.insert_row(row, str(count_sub), str(count_all), coverage)
                        else:
                            QMessageBox.critical(self, "Wrong", "Not exist!")

                    except:
                        QMessageBox.critical(self, "Wrong", "Data reading exception!")
            except:
                QMessageBox.critical(self, "Wrong", "Data error:check file existence or encoding for UTF-8!")
        button.toggle()

    @pyqtSlot()
    def on_button_add_clicked(self):
        """触发前缀频率"""
        self.button_add.clicked.connect(self.show_child)

    def show_child(self):
        self.child_window = childWindow()
        self.child_window.show()

    @pyqtSlot()
    def on_button_add_root_clicked(self):
        """触发词根频率"""
        self.button_add_root.clicked.connect(self.show_root_child)

    def show_root_child(self):
        self.child_window = childRootWindow()
        self.child_window.show()

    @pyqtSlot()
    def on_button_add_suffix_clicked(self):
        """触发后缀频率"""
        self.button_add_suffix.clicked.connect(self.show_suffix_child)

    def show_suffix_child(self):
        self.child_window = childSuffixWindow()
        self.child_window.show()

    @pyqtSlot()
    def on_button_add_six_clicked(self):
        """触发六指标"""
        self.button_add_six.clicked.connect(self.show_six_child)

    def show_six_child(self):
        self.child_window = childSixWindow()
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

    def insert_row(self, row, affix, frequency, word):
        affix_item = QTableWidgetItem(affix)
        frequency_item = QTableWidgetItem(frequency)
        word = QTableWidgetItem(word)

        self.tableWidget.insertRow(row)
        self.tableWidget.setItem(row, 0, affix_item)
        self.tableWidget.setItem(row, 1, frequency_item)
        self.tableWidget.setItem(row, 2, word)
        word.setToolTip(word.text())

    @pyqtSlot()
    def on_button_search_clicked(self):
        try:
            if res_prefix_list and res_prefix_list[0]:
                results = res_prefix_list[0]
                for item in results:
                    affix = to_none(item["affix"])
                    frequency = to_none(item["frequency"])
                    word = item["word"]
                    # word = ",".join(word_sole for word_sole in word)
                    word = split_words(word)
                    row = self.tableWidget.rowCount()
                    self.insert_row(row, affix, str(frequency), word)
            else:
                QMessageBox.critical(self, "Wrong", "Wrong")
        except:
            QMessageBox.critical(self, "Wrong", "Wrong")


class childRootWindow(QMainWindow, Ui_Sub_Root_Window):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.init()

    def init(self):
        self.tableWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def insert_row(self, row, affix, frequency, word):
        affix_item = QTableWidgetItem(affix)
        frequency_item = QTableWidgetItem(frequency)
        word = QTableWidgetItem(word)

        self.tableWidget.insertRow(row)
        self.tableWidget.setItem(row, 0, affix_item)
        self.tableWidget.setItem(row, 1, frequency_item)
        self.tableWidget.setItem(row, 2, word)
        word.setToolTip(word.text())

    @pyqtSlot()
    def on_button_search_clicked(self):

        try:
            if res_root_list and res_root_list[0]:
                results = res_root_list[0]
                for item in results:
                    affix = to_none(item["affix"])
                    frequency = to_none(item["frequency"])
                    word = item["word"]
                    word = split_words(word)
                    # word = ",".join(word_sole for word_sole in word)
                    row = self.tableWidget.rowCount()
                    self.insert_row(row, affix, str(frequency), word)
            else:
                QMessageBox.critical(self, "Wrong", "Wrong")
        except:
            QMessageBox.critical(self, "Wrong", "Wrong")


class childSuffixWindow(QMainWindow, Ui_Sub_Suffix_Window):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.init()

    def init(self):
        self.tableWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def insert_row(self, row, affix, frequency, word):
        affix_item = QTableWidgetItem(affix)
        frequency_item = QTableWidgetItem(frequency)
        word = QTableWidgetItem(word)

        self.tableWidget.insertRow(row)
        self.tableWidget.setItem(row, 0, affix_item)
        self.tableWidget.setItem(row, 1, frequency_item)
        self.tableWidget.setItem(row, 2, word)
        word.setToolTip(word.text())

    @pyqtSlot()
    def on_button_search_clicked(self):

        try:
            if res_suffix_list and res_suffix_list[0]:
                results = res_suffix_list[0]
                for item in results:
                    affix = to_none(item["affix"])
                    frequency = to_none(item["frequency"])
                    word = item["word"]
                    word = split_words(word)
                    # word = ",".join(word_sole for word_sole in word)
                    row = self.tableWidget.rowCount()
                    self.insert_row(row, affix, str(frequency), word)
            else:
                QMessageBox.critical(self, "Wrong", "Wrong")
        except:
            QMessageBox.critical(self, "Wrong", "Wrong")


class childSixWindow(QMainWindow, Ui_Sub_Six_Window):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.init()

    def init(self):
        self.tableWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def insert_row(self, row, morpheme, sum_token_frequency, word_family, PMPF,
                   hapax_word_in_word_list,
                   P, PP, affix_length, types):
        morpheme = QTableWidgetItem(morpheme)
        sum_token_frequency = QTableWidgetItem(sum_token_frequency)
        word_family = QTableWidgetItem(word_family)
        PMPF = QTableWidgetItem(PMPF)
        hapax_word_in_word_list = QTableWidgetItem(hapax_word_in_word_list)
        P = QTableWidgetItem(P)
        PP = QTableWidgetItem(PP)
        affix_length = QTableWidgetItem(affix_length)
        types = QTableWidgetItem(types)

        self.tableWidget.insertRow(row)
        self.tableWidget.setItem(row, 0, morpheme)
        self.tableWidget.setItem(row, 1, sum_token_frequency)
        self.tableWidget.setItem(row, 2, word_family)
        self.tableWidget.setItem(row, 3, PMPF)
        PMPF.setToolTip(PMPF.text())
        self.tableWidget.setItem(row, 4, hapax_word_in_word_list)
        self.tableWidget.setItem(row, 5, P)
        P.setToolTip(P.text())
        self.tableWidget.setItem(row, 6, PP)
        PP.setToolTip(PP.text())
        self.tableWidget.setItem(row, 7, affix_length)
        self.tableWidget.setItem(row, 8, types)

    @pyqtSlot()
    def on_button_search_clicked(self):
        """"morpheme", "sum_token_frequency", "word_family", "PMPF", "hapax_word_in_word_list",
                            "P", "P*", "affix_length", "type"""""
        try:
            if all_frame_list and all_frame_list[0]:
                results = all_frame_list[0]
                for item in results:
                    morpheme = to_none(item["morpheme"])
                    sum_token_frequency = to_none(item["sum_token_frequency"])
                    word_family = to_none(item["word_family"])
                    PMPF = to_none(item["PMPF"])
                    hapax_word_in_word_list = to_none(item["hapax_word_in_word_list"])
                    P = to_none(item["P"])
                    PP = to_none(item["P*"])
                    affix_length = to_none(item["affix_length"])
                    types = to_none(item["type"])
                    row = self.tableWidget.rowCount()
                    self.insert_row(row, morpheme, sum_token_frequency, word_family, PMPF, hapax_word_in_word_list,
                                    P, PP, affix_length, types)
            else:
                QMessageBox.critical(self, "Wrong", "Wrong")
        except:
            QMessageBox.critical(self, "Wrong", "Wrong")


if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    demo.main_window()
    sys.exit(app.exec_())
