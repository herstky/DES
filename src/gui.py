from PyQt5.QtWidgets import QAction, QPushButton, QLabel, QWidget, QGraphicsScene, QMainWindow, QGraphicsItem
from PyQt5.QtGui import QPixmap, QWindow, QPen
from PyQt5.QtCore import QTimer, pyqtSlot, QEvent, Qt, QLineF, QPoint, QPointF, QRectF

from src.simulation import Simulation
from src.main_window import Ui_MainWindow



class ApplicationWindow(QMainWindow):
    def __init__(self):
        super(ApplicationWindow, self).__init__()
        self.initUI()
 
    def initUI(self):
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(QRectF(0, 0, self.ui.graphicsView.width(), self.ui.graphicsView.height()))
        self.ui.graphicsView.setScene(self.scene)   
        self.setWindowTitle('Flow Modeler')
        self.show()

        self.simulation = Simulation()

        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.simulation.run)
        # self.timer.start()

        self.ui.actionStream.triggered.connect(self.create_stream)
        self.ui.actionSource.triggered.connect(self.create_source)
        self.ui.actionSink.triggered.connect(self.create_sink)

        self.setMouseTracking(True)
        self.ui.centralwidget.setMouseTracking(True)
        self.ui.graphicsView.setMouseTracking(True)

        self.installEventFilter(self)
        self.mouse_x = 0
        self.mouse_y = 0
        self.placing_module = False
        self.floating_widget = None
        self.placing_stream = False
        self.drawing_stream = False
        self.floating_line = None

    def eventFilter(self, source, event):
        if event.type() == QEvent.HoverMove and source is self:
            self.mouse_x = event.pos().x()
            self.mouse_y = event.pos().y()
            if self.placing_module or self.placing_stream:
                self.floating_widget.setGeometry(self.mouse_x, self.mouse_y, self.floating_widget.width(), self.floating_widget.height())
            if self.drawing_stream:
                p1 = self.floating_line.line().p1()
                p2 = self.adjust_coords(QPoint(self.mouse_x, self.mouse_y))
                self.floating_line.setLine(QLineF(p1, p2))
                print(self.floating_line.line().p2())
        # print(f'({self.mouse_x}, {self.mouse_y})')

        return super(ApplicationWindow, self).eventFilter(source, event)

    def adjust_coords(self, pos):
        pos = self.ui.graphicsView.parent().mapFromParent(pos)
        pos = self.ui.graphicsView.mapFromParent(pos)
        pos = self.ui.graphicsView.mapToScene(pos)
        return pos

    def mousePressEvent(self, event):
        if self.placing_module:
            self.place_module()
        elif self.drawing_stream:
            self.complete_stream()
        elif self.placing_stream:
            self.place_stream()


    @pyqtSlot()
    def create_source(self):
        self.create_module('assets/source.png')

    @pyqtSlot()
    def create_sink(self):
        self.create_module('assets/sink.png')

    def create_module(self, path):
        self.placing_module = True
        label = QLabel(self)
        pixmap = QPixmap(path)
        label.setPixmap(pixmap)
        label.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        label.setGeometry(self.mouse_x, self.mouse_y, pixmap.width(), pixmap.height())
        label.show()
        self.floating_widget = label
        # print(f'self: {self}, x: {self.mouse_x}, y: {self.mouse_y}')
        # print(f'({self.mouse_x}, {self.mouse_y}), width: {label.width()}, height: {label.height()}')

    def place_module(self):
        self.placing_module = False
        self.floating_widget.setParent(None)
        pixmap_item = self.ui.graphicsView.scene().addPixmap(self.floating_widget.pixmap())
        pos = self.adjust_coords(QPoint(self.mouse_x, self.mouse_y))
        pixmap_item.setPos(pos)
        self.floating_widget = None

    @pyqtSlot()
    def create_stream(self):
        if self.placing_module:
            self.placing_module = False
            self.floating_widget.setParent(None)
            self.floating_widget = None
        self.placing_stream = True
        label = QLabel(self)
        pixmap = QPixmap('assets/connection.png')
        label.setPixmap(pixmap)
        label.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        label.setGeometry(self.mouse_x, self.mouse_y, pixmap.width(), pixmap.height())
        label.show()
        self.floating_widget = label

    def place_stream(self):
        self.drawing_stream = True
        self.placing_stream = False
        self.floating_widget.setParent(None)
        pos = self.adjust_coords(QPoint(self.mouse_x, self.mouse_y))
        line = QLineF(pos, pos)
        self.floating_line = self.ui.graphicsView.scene().addLine(line)
        pen = QPen()
        pen.setWidth(2)
        self.floating_line.setPen(pen)
        # self.floating_line.setPos(pos)

        self.floating_widget = None

    def complete_stream(self):
        self.drawing_stream = False
    
