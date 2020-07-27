from enum import Enum

from PyQt5.QtWidgets import QAction, QPushButton, QLabel, QWidget, QGraphicsScene, QMainWindow, QGraphicsItem
from PyQt5.QtGui import QPixmap, QWindow, QPen, QTransform
from PyQt5.QtCore import QTimer, pyqtSlot, QEvent, Qt, QLineF, QPoint, QPointF, QRectF

from src.simulation import Simulation
from src.main_window import Ui_MainWindow
from src.models import Source, Sink, Stream

class State(Enum):
    RUNNING = 1
    IDLE = 2
    PLACING_MODULE = 3
    PLACING_STREAM = 4
    DRAWING_STREAM = 5

class ApplicationWindow(QMainWindow):
    def __init__(self):
        super(ApplicationWindow, self).__init__()
        self.initUI()
 
    def initUI(self):
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.state = State(State.IDLE)
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(QRectF(0, 0, self.ui.graphicsView.width(), self.ui.graphicsView.height()))
        self.ui.graphicsView.setScene(self.scene)   
        self.setWindowTitle('Flow Modeler')
        self.show()

        self.views = []
        self.simulation = Simulation(self)

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

        self.floating_widget = None
        self.floating_model = None
        self.floating_line = None

    def eventFilter(self, source, event):
        if event.type() == QEvent.HoverMove and source is self:
            self.mouse_x = event.pos().x()
            self.mouse_y = event.pos().y()
            if self.state is State.PLACING_MODULE or self.state is State.PLACING_STREAM:
                self.floating_widget.setGeometry(self.mouse_x, self.mouse_y, self.floating_widget.width(), self.floating_widget.height())
            if self.state is State.DRAWING_STREAM:
                p1 = self.floating_line.line().p1()
                p2 = self.adjust_coords(QPoint(self.mouse_x, self.mouse_y))
                self.floating_line.setLine(QLineF(p1, p2))
        # print(f'({self.mouse_x}, {self.mouse_y})')

        return super(ApplicationWindow, self).eventFilter(source, event)

    def adjust_coords(self, pos):
        pos = self.ui.graphicsView.parent().mapFromParent(pos)
        pos = self.ui.graphicsView.mapFromParent(pos)
        pos = self.ui.graphicsView.mapToScene(pos)
        return pos

    def mousePressEvent(self, event):
        if self.state is State.PLACING_MODULE:
            self.place_module()
        elif self.state is State.DRAWING_STREAM:
            self.complete_stream(self.adjust_coords(event.pos()))
        elif self.state is State.PLACING_STREAM:
            self.place_stream(self.adjust_coords(event.pos()))

    @pyqtSlot()
    def create_source(self):
        self.add_module(Source(self))

    @pyqtSlot()
    def create_sink(self):
        self.add_module(Sink(self))

    def add_module(self, module):
        label = QLabel(self)
        label.setPixmap(module.view.pixmap)
        label.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        label.setGeometry(self.mouse_x, self.mouse_y, module.view.pixmap.width(), module.view.pixmap.height())
        label.show()
        self.state = State.PLACING_MODULE
        self.floating_widget = label
        self.floating_model = module

    def place_module(self):
        self.floating_widget.setParent(None)
        pixmap_item = self.floating_model.view.add_to_scene(self.scene)
        pos = self.adjust_coords(QPoint(self.mouse_x, self.mouse_y))
        pixmap_item.setPos(pos)
        self.state = State.IDLE
        self.floating_widget = None
        self.floating_model = None

    @pyqtSlot()
    def create_stream(self):
        if self.state is State.PLACING_MODULE:
            self.floating_widget.setParent(None)
            self.floating_widget = None
            self.floating_model = None

        self.state = State.PLACING_STREAM
        label = QLabel(self)
        pixmap = QPixmap('assets/connection.png')
        label.setPixmap(pixmap)
        label.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        label.setGeometry(self.mouse_x, self.mouse_y, pixmap.width(), pixmap.height())
        label.show()
        self.floating_widget = label



    def place_stream(self, pos):
        self.state = State.DRAWING_STREAM
        pos = self.adjust_coords(QPoint(self.mouse_x, self.mouse_y))
        line = QLineF(pos, pos)
        self.floating_line = self.scene.addLine(line)
        for colliding_item in self.scene.collidingItems(self.floating_line):
            # if colliding_item.
            pass
        pen = QPen()
        pen.setWidth(2)
        self.floating_line.setPen(pen)

        self.floating_widget.setParent(None)
        self.floating_widget = None
        # print(self.scene.itemAt(pos.x(), pos.y(), QTransform()))


    def complete_stream(self, pos):
        self.state = State.IDLE
        line = QLineF(pos, QPoint(pos.x(), pos.y()))
        line_item = self.scene.addLine(line)
        print(self.scene.collidingItems(line_item))
        self.scene.removeItem(line_item)
    
