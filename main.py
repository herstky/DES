from PyQt5 import QtWidgets

from src.gui import ApplicationWindow



if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = ApplicationWindow()
    app.exec_()