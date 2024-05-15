import sys

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QPushButton

from IDE.main import run_ide
from User.main import myWindow
from Core.CoreController import CoreController


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, core_controller: CoreController, app: QtWidgets.QApplication):
        super(MainWindow, self).__init__()

        self.app = app
        self.core_controller = core_controller
        self.mode = None

        self.setup_ui()

        self.btn_developer.clicked.connect(self.run_developer_mode)
        self.btn_user.clicked.connect(self.run_user_mode)

        # Устанавливаем центральный виджет Window.
        self.setCentralWidget(self.centralwidget)
    
    def setup_ui(self):
        self.setObjectName("MainWindow")
        self.resize(400, 200)
        self.setMinimumSize(QtCore.QSize(400, 200))
        self.setMaximumSize(QtCore.QSize(400, 200))
        self.setBaseSize(QtCore.QSize(400, 200))

        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        self.btn_developer = QPushButton("Developer mode", self.centralwidget)
        self.btn_developer.setGeometry(QtCore.QRect(120, 20, 180, 60))
        
        self.btn_user = QPushButton("User mode", self.centralwidget)
        self.btn_user.setGeometry(QtCore.QRect(120, 100, 180, 60))

    #def closeEvent(self, a0: QCloseEvent) -> None:
    #    if self.mode == "user":
    #        run_user(core_controller=self.core_controller)

    def run_developer_mode(self):
        run_ide(core_controller=self.core_controller)

    def run_user_mode(self):
        self.w = myWindow(
            core_controller=self.core_controller,
            app=self.app
        )
        self.core_controller._update_modules_list()
        self.w._update_funtion_list()
        self.w.show()


if __name__ == "__main__":
    cc = CoreController()

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    application = MainWindow(
        core_controller=cc,
        app=app
    )
    application.show()

    sys.exit(app.exec_())
