from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer

from src.simulation import Simulation
from src.main_window import Ui_MainWindow



class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(ApplicationWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.show()

        self.simulation = Simulation()

        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.simulation.run)
        self.timer.start()