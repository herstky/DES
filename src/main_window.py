# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src\main_window.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(999, 791)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.graphicsView = QtWidgets.QGraphicsView(self.centralwidget)
        self.graphicsView.setObjectName("graphicsView")
        self.verticalLayout.addWidget(self.graphicsView)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 999, 26))
        self.menuBar.setNativeMenuBar(True)
        self.menuBar.setObjectName("menuBar")
        self.menuFile = QtWidgets.QMenu(self.menuBar)
        self.menuFile.setObjectName("menuFile")
        self.menuEdit = QtWidgets.QMenu(self.menuBar)
        self.menuEdit.setObjectName("menuEdit")
        self.menuInsert = QtWidgets.QMenu(self.menuBar)
        self.menuInsert.setObjectName("menuInsert")
        self.menuBlock = QtWidgets.QMenu(self.menuInsert)
        self.menuBlock.setObjectName("menuBlock")
        self.menuView = QtWidgets.QMenu(self.menuBar)
        self.menuView.setObjectName("menuView")
        self.menuWindow = QtWidgets.QMenu(self.menuBar)
        self.menuWindow.setObjectName("menuWindow")
        self.menuHelp = QtWidgets.QMenu(self.menuBar)
        self.menuHelp.setObjectName("menuHelp")
        MainWindow.setMenuBar(self.menuBar)
        self.toolBar = QtWidgets.QToolBar(MainWindow)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.toolBar_2 = QtWidgets.QToolBar(MainWindow)
        self.toolBar_2.setObjectName("toolBar_2")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar_2)
        self.toolBar_3 = QtWidgets.QToolBar(MainWindow)
        self.toolBar_3.setObjectName("toolBar_3")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar_3)
        self.actionNew = QtWidgets.QAction(MainWindow)
        self.actionNew.setObjectName("actionNew")
        self.actionOpen = QtWidgets.QAction(MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.actionSave = QtWidgets.QAction(MainWindow)
        self.actionSave.setObjectName("actionSave")
        self.actionSave_As = QtWidgets.QAction(MainWindow)
        self.actionSave_As.setObjectName("actionSave_As")
        self.actionStop = QtWidgets.QAction(MainWindow)
        self.actionStop.setObjectName("actionStop")
        self.actionStart = QtWidgets.QAction(MainWindow)
        self.actionStart.setObjectName("actionStart")
        self.actionNext = QtWidgets.QAction(MainWindow)
        self.actionNext.setObjectName("actionNext")
        self.action = QtWidgets.QAction(MainWindow)
        self.action.setObjectName("action")
        self.actionSource = QtWidgets.QAction(MainWindow)
        self.actionSource.setObjectName("actionSource")
        self.actionSink = QtWidgets.QAction(MainWindow)
        self.actionSink.setObjectName("actionSink")
        self.actionSplitter = QtWidgets.QAction(MainWindow)
        self.actionSplitter.setObjectName("actionSplitter")
        self.actionJoiner = QtWidgets.QAction(MainWindow)
        self.actionJoiner.setObjectName("actionJoiner")
        self.actionReadout = QtWidgets.QAction(MainWindow)
        self.actionReadout.setObjectName("actionReadout")
        self.actionTank = QtWidgets.QAction(MainWindow)
        self.actionTank.setObjectName("actionTank")
        self.actionPump = QtWidgets.QAction(MainWindow)
        self.actionPump.setObjectName("actionPump")
        self.actionHydrocyclone = QtWidgets.QAction(MainWindow)
        self.actionHydrocyclone.setObjectName("actionHydrocyclone")
        self.actionFiberReadout = QtWidgets.QAction(MainWindow)
        self.actionFiberReadout.setObjectName("actionFiberReadout")
        self.actionJoinerPump = QtWidgets.QAction(MainWindow)
        self.actionJoinerPump.setObjectName("actionJoinerPump")
        self.menuFile.addAction(self.actionNew)
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionSave_As)
        self.menuBlock.addAction(self.actionSource)
        self.menuBlock.addAction(self.actionTank)
        self.menuBlock.addAction(self.actionPump)
        self.menuBlock.addAction(self.actionSink)
        self.menuBlock.addAction(self.actionSplitter)
        self.menuBlock.addAction(self.actionHydrocyclone)
        self.menuBlock.addAction(self.actionJoiner)
        self.menuBlock.addAction(self.actionFiberReadout)
        self.menuBlock.addAction(self.actionReadout)
        self.menuInsert.addAction(self.menuBlock.menuAction())
        self.menuHelp.addAction(self.action)
        self.menuBar.addAction(self.menuFile.menuAction())
        self.menuBar.addAction(self.menuEdit.menuAction())
        self.menuBar.addAction(self.menuInsert.menuAction())
        self.menuBar.addAction(self.menuView.menuAction())
        self.menuBar.addAction(self.menuWindow.menuAction())
        self.menuBar.addAction(self.menuHelp.menuAction())
        self.toolBar.addAction(self.actionNew)
        self.toolBar.addAction(self.actionOpen)
        self.toolBar.addAction(self.actionSave)
        self.toolBar.addAction(self.actionSave_As)
        self.toolBar_2.addAction(self.actionStart)
        self.toolBar_2.addAction(self.actionNext)
        self.toolBar_2.addAction(self.actionStop)
        self.toolBar_3.addAction(self.actionSource)
        self.toolBar_3.addAction(self.actionTank)
        self.toolBar_3.addAction(self.actionPump)
        self.toolBar_3.addAction(self.actionSink)
        self.toolBar_3.addAction(self.actionSplitter)
        self.toolBar_3.addAction(self.actionHydrocyclone)
        self.toolBar_3.addAction(self.actionJoiner)
        self.toolBar_3.addAction(self.actionFiberReadout)
        self.toolBar_3.addAction(self.actionJoinerPump)
        self.toolBar_3.addAction(self.actionReadout)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuEdit.setTitle(_translate("MainWindow", "Edit"))
        self.menuInsert.setTitle(_translate("MainWindow", "Insert"))
        self.menuBlock.setTitle(_translate("MainWindow", "Block"))
        self.menuView.setTitle(_translate("MainWindow", "View"))
        self.menuWindow.setTitle(_translate("MainWindow", "Window"))
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar"))
        self.toolBar_2.setWindowTitle(_translate("MainWindow", "toolBar_2"))
        self.toolBar_3.setWindowTitle(_translate("MainWindow", "toolBar_3"))
        self.actionNew.setText(_translate("MainWindow", "New"))
        self.actionNew.setShortcut(_translate("MainWindow", "Ctrl+N"))
        self.actionOpen.setText(_translate("MainWindow", "Open"))
        self.actionOpen.setShortcut(_translate("MainWindow", "Ctrl+O"))
        self.actionSave.setText(_translate("MainWindow", "Save"))
        self.actionSave.setShortcut(_translate("MainWindow", "Ctrl+S"))
        self.actionSave_As.setText(_translate("MainWindow", "Save As"))
        self.actionStop.setText(_translate("MainWindow", "Stop"))
        self.actionStart.setText(_translate("MainWindow", "Start"))
        self.actionNext.setText(_translate("MainWindow", "Next"))
        self.action.setText(_translate("MainWindow", "¯\\(ツ)/¯"))
        self.actionSource.setText(_translate("MainWindow", "Source"))
        self.actionSink.setText(_translate("MainWindow", "Sink"))
        self.actionSplitter.setText(_translate("MainWindow", "Splitter"))
        self.actionJoiner.setText(_translate("MainWindow", "Joiner"))
        self.actionReadout.setText(_translate("MainWindow", "Readout"))
        self.actionTank.setText(_translate("MainWindow", "Tank"))
        self.actionPump.setText(_translate("MainWindow", "Pump"))
        self.actionHydrocyclone.setText(_translate("MainWindow", "Hydrocyclone"))
        self.actionFiberReadout.setText(_translate("MainWindow", "FiberReadout"))
        self.actionJoinerPump.setText(_translate("MainWindow", "JoinerPump"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
