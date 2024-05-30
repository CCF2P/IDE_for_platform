import sys
from pathlib import Path

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import (
    QPalette,
    QColor,
    QGuiApplication,
    QCloseEvent
)
from PyQt5.QtCore import Qt


from User.user_window import Ui_MainWindow


class myWindow(QtWidgets.QWidget):
    VALUES: list

    def __init__(self, core_controller, app: QtWidgets.QApplication):
        super(myWindow, self).__init__()
        self.ui: Ui_MainWindow = Ui_MainWindow()
        self.file_list: list[str] = list()
        self.ui.setupUi(self)

        self.app = app
        self.core_controller = core_controller
        self.VALUES = list()

        self._update_funtion_list()
        #for i in range(len(self.VALUES)):
        #    self.ui.functionsList.insertItem(i, self.VALUES[i][:-3])

        # signals
        self.ui.processTextBtn.clicked.connect(self.processText)
        self.ui.clearInputFieldBtn.clicked.connect(self.clearInputField)
        self.ui.clearOutputFieldBtn.clicked.connect(self.clearOutputField)
        self.ui.copyOutputFieldBtn.clicked.connect(self.copyOutputField)
        self.ui.importFileBtn.clicked.connect(self.importFile)
        self.ui.exportFileBtn.clicked.connect(self.exportFile)

    def _update_funtion_list(self) -> None:
        self.VALUES = self.core_controller.get_modules()
        self.ui.functionsList.clear()
        for i in range(len(self.VALUES)):
            self.ui.functionsList.insertItem(i, self.VALUES[i][:-3])

    def closeEvent(self, a0: QCloseEvent) -> None:
        a0.accept()

    def clearInputField(self) -> None:
        self.ui.inputField.clear()
    
    def clearOutputField(self):
        self.ui.outputField.clear()

    def copyOutputField(self) -> None:
        self.ui.outputField.copy()

    def importFile(self):
        # создаем диалоговое окно для выбора файла(ов) и
        # заносим пути в список file_list
        dialog = QFileDialog(self)
        # dialog.setDirectory(r'C:')
        dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        # dialog.setNameFilter("Images (*.png *.jpg)")
        dialog.setViewMode(QFileDialog.ViewMode.List)
        if dialog.exec():
            filenames = dialog.selectedFiles()
            if filenames:
                self.file_list.append([str(Path(filename)) for filename in filenames])
        #print(self.file_list)

        if len(self.file_list) == 0:
            return

        # обрабатываем файлы которые находятся по пути(ям) из списка file_list
        with open(self.file_list[0][0], 'r', encoding="utf-8") as f:
            self.ui.inputField.setText(' '.join(f.readlines()))

    def exportFile(self):
        filename, _ = QFileDialog.getSaveFileName(
            None,
            "Save File",
            ".",
            "Text Files (*.txt);;All Files (*)"
        )
        if filename:
            with open(filename, 'w', encoding="utf-8") as file:
                file.write(self.ui.outputField.toPlainText())

    def sum_text(self, user_text: str) -> None:
        print("OK")
        self.ui.outputField.setText(user_text)

    def processText(self) -> None:
        self.ui.outputField.clear()
        input_text = self.ui.inputField.toPlainText()
        
        with open(
            file="C:\\Users\\zhora\\Desktop\\Python\\VKR_Platform\\Core\\Databases\\DB_Modules\\TuzovAnalyzer\\input.txt",
            mode="w",
            encoding="utf8"
        ) as file:
            file.write(input_text)
        
        # Пока что возвращаю просто текст, а не результат работы модуля
        self.core_controller.run_module(self.ui.functionsList.currentText())
        with open(
            file="C:/Users/zhora/Desktop/Python/VKR_Platform/Core/output.txt",
            mode="r"
        ) as file:
            text = file.read()
            self.ui.outputField.setText(text)


def run_user(core_controller):
    application = myWindow(core_controller=core_controller)
    application.show()
