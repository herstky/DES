from enum import Enum

from PyQt5.QtWidgets import QAction, QPushButton, QLabel, QWidget, QGraphicsScene, QMainWindow, QGraphicsItem, QGraphicsLineItem, QGraphicsRectItem
from PyQt5.QtGui import QPixmap, QWindow, QPen, QTransform, QColor
from PyQt5.QtCore import QTimer, pyqtSlot, QEvent, Qt, QLineF, QPoint, QPointF, QRectF

from .simulation import Simulation
from .main_window import Ui_MainWindow
from .models import Source, Sink, Stream, Connection, InletConnection, OutletConnection, Joiner, Splitter, Readout
from .views import StreamView, ReadoutView



class ApplicationWindow(QMainWindow):
    class State(Enum):
        running = 1
        idle = 2
        placing_module = 3
        placing_stream = 4
        drawing_stream = 5
        placing_readout = 6
        drawing_readout = 7

    running = State.running
    idle = State.idle
    placing_module = State.placing_module
    placing_stream = State.placing_stream
    drawing_stream = State.drawing_stream
    placing_readout = State.placing_readout
    drawing_readout = State.drawing_readout

    def __init__(self):
        super(ApplicationWindow, self).__init__()
        self.initUI()
 
    def initUI(self):
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.state = ApplicationWindow.idle
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(QRectF(0, 0, self.ui.graphicsView.width(), self.ui.graphicsView.height()))
        self.ui.graphicsView.setScene(self.scene)   
        self.setWindowTitle('Flow Modeler')
        self.show()

        self.views = []
        self.simulation = Simulation(self)

        self.timer = QTimer()
        self.timer.setInterval(100)
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

        self.floating_model = None
        self.floating_line = None

    def eventFilter(self, source, event):
        if event.type() == QEvent.HoverMove and source is self:
            self.mouse_x = event.pos().x()
            self.mouse_y = event.pos().y()
            if self.state is ApplicationWindow.placing_module:
                width = self.floating_model.view.graphics_item.pixmap().width()
                height = self.floating_model.view.graphics_item.pixmap().height()
                self.floating_model.view.graphics_item.setPos(self.map_from_global_to_scene(QPoint(self.mouse_x - width, self.mouse_y - height)))
            elif self.state is ApplicationWindow.placing_stream or self.state is self.placing_readout:
                width = self.floating_model.view.graphics_item.rect().width()
                height = self.floating_model.view.graphics_item.rect().height()
                self.floating_model.view.graphics_item.setPos(self.map_from_global_to_scene(QPoint(self.mouse_x - width / 2, self.mouse_y - height / 2)))
            elif self.state is ApplicationWindow.drawing_stream:
                p1 = self.floating_line.line().p1()
                p2 = self.map_from_global_to_scene(QPoint(self.mouse_x, self.mouse_y))
                self.floating_line.setLine(QLineF(p1, p2))
            elif self.state is ApplicationWindow.drawing_readout:
                p1 = self.floating_line.mapToScene(self.floating_line.line().p1()) 

                width = self.floating_model.view.graphics_item.rect().width()
                height = self.floating_model.view.graphics_item.rect().height()

                self.floating_model.view.graphics_item.setPos(self.map_from_global_to_scene(QPoint(self.mouse_x - width / 2, self.mouse_y - height / 2)))
                p1 = self.floating_line.mapFromScene(p1)
                p2 = self.floating_line.mapFromScene(self.map_from_global_to_scene(QPoint(self.mouse_x, self.mouse_y)))
                self.floating_line.setLine(QLineF(p1, p2))

        return super(ApplicationWindow, self).eventFilter(source, event)

    def map_from_global_to_scene(self, pos):
        pos = self.ui.graphicsView.parent().mapFromParent(pos)
        pos = self.ui.graphicsView.mapFromParent(pos)
        pos = self.ui.graphicsView.mapToScene(pos)
        return pos

    def mousePressEvent(self, event):
        if self.state is ApplicationWindow.placing_module:
            self.place_module()
        elif self.state is ApplicationWindow.drawing_stream:
            self.complete_stream(self.map_from_global_to_scene(event.pos()))
        elif self.state is ApplicationWindow.placing_stream:
            self.start_stream(self.map_from_global_to_scene(event.pos()))
        elif self.state is ApplicationWindow.drawing_readout:
            self.complete_readout(self.map_from_global_to_scene(event.pos()))
        elif self.state is ApplicationWindow.placing_readout:
            self.start_readout(self.map_from_global_to_scene(event.pos()))
 
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
        self.state = self.placing_module
        module.view.add_to_scene(self.scene)
        width = module.view.graphics_item.pixmap().width()
        height = module.view.graphics_item.pixmap().height()
        module.view.graphics_item.setPos(self.map_from_global_to_scene(QPoint(self.mouse_x - width, self.mouse_y - height)))
        self.floating_model = module

    def place_module(self):
        self.state = self.idle
        self.floating_model = None

    @pyqtSlot()
    def create_stream(self):
        self.state = self.placing_stream
        self.floating_model = Stream(self)
        self.floating_model.view.graphics_item = self.scene.addRect(QRectF(0, 0, 5, 5))
        self.floating_model.view.graphics_item.setBrush(Qt.black)

        width = self.floating_model.view.graphics_item.rect().width()
        height = self.floating_model.view.graphics_item.rect().height()
        self.floating_model.view.graphics_item.setPos(self.map_from_global_to_scene(QPoint(self.mouse_x - width / 2, 
                                                      self.mouse_y - height / 2)))

    def start_stream(self, pos):
        line = QLineF(pos, pos)
        self.floating_line = self.scene.addLine(line)
        self.floating_line.setZValue(-1)
        self.scene.removeItem(self.floating_model.view.graphics_item)
        for colliding_item in self.scene.collidingItems(self.floating_line):
            for view in self.views:
                if isinstance(view.model, Connection) and view.graphics_item is colliding_item:
                    self.floating_model.add_connection(view.model)
                    self.state = self.drawing_stream
                    p1 = QPointF(colliding_item.scenePos().x() + colliding_item.boundingRect().width() / 2 - 1, 
                                 colliding_item.scenePos().y() + colliding_item.boundingRect().height() / 2 - 1)
                    p2 = pos
                    pen = QPen()
                    pen.setWidth(2)
                    self.floating_line.setPen(pen)
                    self.floating_line.setLine(QLineF(p1, p2))  
                    
        if self.state is not ApplicationWindow.drawing_stream:
            self.state = self.idle
            self.views.remove(self.floating_model.view)
            del self.floating_model
            self.scene.removeItem(self.floating_line)
            self.floating_line = None

    def complete_stream(self, pos):
        self.state = self.idle
        line = QLineF(pos, pos)
        test_line_item = self.scene.addLine(line)
        self.floating_model.view.graphics_item = None
        completed = False
        for colliding_item in self.scene.collidingItems(test_line_item):
            for view in self.views:
                if isinstance(view.model, Connection) and view.graphics_item is colliding_item:             
                    if not self.floating_model.add_connection(view.model):
                        continue

                    p1 = QPointF(colliding_item.scenePos().x() + colliding_item.boundingRect().width() / 2 - 1, 
                                 colliding_item.scenePos().y() + colliding_item.boundingRect().height() / 2 - 1)
                    p2 = self.floating_line.line().p1()
                    self.scene.removeItem(self.floating_line)
                    self.floating_line.setLine(QLineF(p1, p2)) 
                    self.floating_model.view.graphics_item = self.floating_line
                    self.floating_model.view.multiline = Multiline(self.scene, self.floating_line.line())
                    self.floating_model.view.multiline.snap_single_line()
                    self.floating_model = None
                    self.floating_line = None
                    completed = True

        self.scene.removeItem(test_line_item)

        if self.floating_model and not completed:
            if self.floating_model.inlet_connection:
                self.floating_model.remove_connection(self.floating_model.remove_connection)
            self.views.remove(self.floating_model.view)
            del self.floating_model
            self.scene.removeItem(self.floating_line)
            self.floating_line = None
    
    @pyqtSlot()
    def create_readout(self):
        self.state = self.placing_readout
        self.floating_model = Readout(self)
        self.scene.addItem(self.floating_model.view.graphics_item)
   
        width = self.floating_model.view.graphics_item.rect().width()
        height = self.floating_model.view.graphics_item.rect().height()

        # Center rect at mouse location
        self.floating_model.view.graphics_item.setPos(self.map_from_global_to_scene(QPoint(self.mouse_x - width / 2, self.mouse_y - height / 2)))

    def start_readout(self, pos):
        for colliding_item in self.scene.collidingItems(self.floating_model.view.graphics_item):
            for view in self.views:
                if type(view.model) is Stream and isinstance(view, StreamView) and colliding_item in view.multiline.line_items:
                    self.state = self.drawing_readout
                    self.floating_model.stream = view.model
                    self.floating_line = self.scene.addLine(QLineF())
                    self.floating_line.setParentItem(self.floating_model.view.graphics_item)
                    p1 = p2 = pos
                    angle = colliding_item.line().angle()
                    
                    # snap readout line to colliding line item
                    if angle == 0.0 or angle == 180.0: 
                        p1.setY(colliding_item.line().y1())
                        self.floating_model.view.orientation = ReadoutView.Orientation.vertical
                    elif angle == 90.0 or angle == 270.0: 
                        p1.setX(colliding_item.line().x1())
                        self.floating_model.view.orientation = ReadoutView.Orientation.horizontal
                    p1 = self.floating_line.mapFromScene(p1)
                    p2 = self.floating_line.mapFromScene(p2)

                    pen = QPen()
                    pen.setWidth(2)
                    self.floating_line.setLine(QLineF(p1, p2))
                    self.floating_line.setPen(pen)
                    self.floating_line.setZValue(-1)

        if self.state is not ApplicationWindow.drawing_readout:
            self.state = self.idle
            self.views.remove(self.floating_model.view)
            self.scene.removeItem(self.floating_model.view.graphics_item)
            del self.floating_model

    def complete_readout(self, pos):
        self.state = self.idle
        rect_graphics_item = self.floating_model.view.graphics_item
        line_graphics_item = self.floating_line

        if self.floating_model.view.orientation is ReadoutView.Orientation.horizontal:
            p1 = QPoint(line_graphics_item.line().x1(), line_graphics_item.line().y1())
            p2 = QPoint(line_graphics_item.line().x2(), line_graphics_item.line().y1())
        else:
            p1 = QPoint(line_graphics_item.line().x1(), line_graphics_item.line().y1())
            p2 = QPoint(line_graphics_item.line().x1(), line_graphics_item.line().y2())

        width = rect_graphics_item.rect().width()
        height = rect_graphics_item.rect().height()

        p1 = rect_graphics_item.mapToScene(p1)
        p2 = rect_graphics_item.mapToScene(p2)
        rect_graphics_item.setPos(QPoint(p2.x() - width / 2 - 1, p2.y() - height / 2 - 1))

        p1 = rect_graphics_item.mapFromScene(p1)
        p2 = rect_graphics_item.mapFromScene(p2)
        line_graphics_item.setLine(QLineF(p1, p2)) 
        
        self.floating_model.view.init_text()

        self.floating_model = None
        self.floating_line = None


class Multiline:
    def __init__(self, scene, *args):
        self.scene = scene
        self.line_pairs = []
        self.pen = QPen()
        self.pen.setWidth(2)

        for line in args:
            self.add_graphics_line_item(line)
  
    @property
    def line_items(self):
        return [line_item for _, line_item in self.line_pairs]

    @property
    def lines(self):
        return [line for line, _ in self.line_pairs]

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







