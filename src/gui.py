from enum import Enum

from PyQt5.QtWidgets import QAction, QPushButton, QLabel, QWidget, QGraphicsScene, QMainWindow, QGraphicsItem, QGraphicsLineItem
from PyQt5.QtGui import QPixmap, QWindow, QPen, QTransform, QColor
from PyQt5.QtCore import QTimer, pyqtSlot, QEvent, Qt, QLineF, QPoint, QPointF, QRectF

from src.simulation import Simulation
from src.main_window import Ui_MainWindow
from src.models import Source, Sink, Stream, Connection, Joiner, Splitter, Readout

class State(Enum):
    RUNNING = 1
    IDLE = 2
    PLACING_MODULE = 3
    PLACING_STREAM = 4
    DRAWING_STREAM = 5
    PLACING_READOUT = 6

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

        self.ui.actionStart.triggered.connect(self.timer.start)
        self.ui.actionStop.triggered.connect(self.timer.stop)
        self.ui.actionStream.triggered.connect(self.create_stream)
        self.ui.actionSource.triggered.connect(self.create_source)
        self.ui.actionSink.triggered.connect(self.create_sink)
        self.ui.actionSplitter.triggered.connect(self.create_splitter)
        self.ui.actionJoiner.triggered.connect(self.create_joiner)
        self.ui.actionReadout.triggered.connect(self.create_readout)

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
            if self.state is State.PLACING_MODULE or self.state is State.PLACING_STREAM or self.state is State.PLACING_READOUT:
                self.floating_widget.setGeometry(self.mouse_x, self.mouse_y, self.floating_widget.width(), self.floating_widget.height())
            if self.state is State.DRAWING_STREAM:
                p1 = self.floating_line.line().p1()
                p2 = self.adjust_coords(QPoint(self.mouse_x, self.mouse_y))
                self.floating_line.setLine(QLineF(p1, p2))

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
        self.add_module(Source(self, 'Source', 500))

    @pyqtSlot()
    def create_sink(self):
        self.add_module(Sink(self, 'Sink'))

    @pyqtSlot()
    def create_splitter(self):
        self.add_module(Splitter(self, 'Splitter'))

    @pyqtSlot()
    def create_joiner(self):
        self.add_module(Joiner(self, 'Joiner'))

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
        line = QLineF(pos, pos)
        self.floating_line = self.scene.addLine(line)
        for colliding_item in self.scene.collidingItems(self.floating_line):
            for view in self.views:
                if type(view.model) is Connection and view.graphics_item is colliding_item:
                    self.state = State.DRAWING_STREAM
                    p1 = QPointF(colliding_item.scenePos().x() + colliding_item.boundingRect().width() / 2 - 1, 
                                 colliding_item.scenePos().y() + colliding_item.boundingRect().height() / 2 - 1)
                    p2 = pos
                    pen = QPen()
                    pen.setWidth(2)
                    self.floating_line.setPen(pen)
                    self.floating_line.setLine(QLineF(p1, p2))  
                    self.floating_model = Stream(self, 'Stream', view.model) 

        if self.state is not State.DRAWING_STREAM:
            self.state = State.IDLE
            self.scene.removeItem(self.floating_line)
            self.floating_line = None
        self.floating_widget.setParent(None)
        self.floating_widget = None


    def complete_stream(self, pos):
        self.state = State.IDLE
        line = QLineF(pos, pos)
        test_line_item = self.scene.addLine(line)
        completed = False
        for colliding_item in self.scene.collidingItems(test_line_item):
            for view in self.views:
                if type(view.model) is Connection and view.graphics_item is colliding_item:
                    p1 = QPointF(colliding_item.scenePos().x() + colliding_item.boundingRect().width() / 2 - 1, 
                                 colliding_item.scenePos().y() + colliding_item.boundingRect().height() / 2 - 1)
                    p2 = self.floating_line.line().p1()
                    self.scene.removeItem(self.floating_line)
                    self.floating_line.setLine(QLineF(p1, p2)) 
                    self.floating_model.add_outlet_connection(view.model)
                    self.floating_model.view.multiline = Multiline(self.scene, self.floating_line.line())
                    self.floating_model.view.multiline.snap_single_line()
                    self.floating_model = None
                    self.floating_line = None
                    completed = True

        self.scene.removeItem(test_line_item)
        if self.floating_model and not completed:
            del self.floating_model
            self.scene.removeItem(self.floating_line)
            self.floating_line = None
    
    @pyqtSlot()
    def create_readout(self):
        label = QLabel(self)
        label.setPixmap(QPixmap(15, 15))
        label.pixmap().fill(QColor(0, 0, 0))
        label.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        label.setGeometry(self.mouse_x, self.mouse_y, 15, 15)
        label.show()
        self.state = State.PLACING_READOUT
        self.floating_widget = label
        self.floating_model = Readout(self)

class Multiline:
    def __init__(self, scene, *args):
        self.scene = scene
        self.line_pairs = []
        self.pen = QPen()
        self.pen.setWidth(2)

        for line in args:
            self.add_graphics_line_item(line)
  

    def add_graphics_line_item(self, line):
        line_item = QGraphicsLineItem(line)
        line_item.setPen(self.pen)
        line_item.setZValue(-1)
        self.scene.addItem(line_item)
        pair = (line, line_item)
        self.line_pairs.append(pair)
        return pair

    def set_pen(self, pen):
        self.pen = pen
        for _, line_item in self.line_pairs:
            line_item.setPen(self.pen)

    def snap_single_line(self):
        line, line_item = self.line_pairs[0]
 
        line1 = QLineF(line.p1().x(), line.p1().y(), line.p1().x(), line.p2().y())
        line2 = QLineF(line.p1().x(), line.p2().y(), line.p2().x(), line.p2().y())
        line_item.setLine(line1)
        self.add_graphics_line_item(line2)


    def drag_joint(self):
        pass







