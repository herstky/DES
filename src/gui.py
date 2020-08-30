from enum import Enum

from PyQt5.QtWidgets import QAction, QPushButton, QLabel, QWidget, QGraphicsScene, QMainWindow, QGraphicsItem, QGraphicsLineItem, QGraphicsRectItem
from PyQt5.QtGui import QGuiApplication, QPixmap, QWindow, QPen, QTransform, QColor
from PyQt5.QtCore import QTimer, pyqtSlot, QEvent, Qt, QLineF, QPoint, QPointF, QRectF

from .simulation import Simulation
from .main_window import Ui_MainWindow
from .models import Source, Tank, Pump, Sink, Stream, Connection, Splitter, Hydrocyclone, Joiner, JoinerPump, Readout, FiberReadout
from .event import Event
from .views import StreamView, ReadoutView



class ApplicationWindow(QMainWindow):
    class State(Enum):
        running = 1
        idle = 2
        placing_module = 3
        drawing_stream = 4
        placing_readout = 5
        drawing_readout = 6
        dragging_joint = 7

    running = State.running
    idle = State.idle
    placing_module = State.placing_module
    drawing_stream = State.drawing_stream
    placing_readout = State.placing_readout
    drawing_readout = State.drawing_readout
    dragging_joint_line = State.dragging_joint

    def __init__(self):
        super(ApplicationWindow, self).__init__()
        self.initUI()
 
    def initUI(self):
        self.mouse_x = 0
        self.mouse_y = 0
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.state = ApplicationWindow.idle
        self.scene = QGraphicsScene(self)
        self.ui.graphicsView.setScene(self.scene) 
        self.setWindowTitle('Flow Modeler')
        self.show()

        self.views = []
        self.simulation = Simulation(self)
       
        self.timer = QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.simulation.run)

        self.ui.actionStart.triggered.connect(self.run_sim)
        self.ui.actionStop.triggered.connect(self.stop_sim)
        self.ui.actionSource.triggered.connect(self.create_source_slot)
        self.ui.actionTank.triggered.connect(self.create_tank_slot)
        self.ui.actionPump.triggered.connect(self.create_pump_slot)
        self.ui.actionSink.triggered.connect(self.create_sink_slot)
        self.ui.actionSplitter.triggered.connect(self.create_splitter_slot)
        self.ui.actionHydrocyclone.triggered.connect(self.create_hydrocyclone_slot)
        self.ui.actionJoiner.triggered.connect(self.create_joiner_slot)
        self.ui.actionJoinerPump.triggered.connect(self.create_joiner_pump_slot)
        self.ui.actionReadout.triggered.connect(self.create_readout)
        self.ui.actionFiberReadout.triggered.connect(self.create_fiber_readout)

        self.setMouseTracking(True)
        self.ui.centralwidget.setMouseTracking(True)
        self.ui.graphicsView.setMouseTracking(True)
        self.installEventFilter(self)
        self.ui.graphicsView.viewport().installEventFilter(self)

        screen = QGuiApplication.primaryScreen()
        screen_width = screen.geometry().width()
        screen_height = screen.geometry().height()

        self.scene.setSceneRect(QRectF(0, 0, screen_width, screen_height))

        self.floating_model = None
        self.floating_line = None

    def map_from_global_to_scene(self, pos):
        pos = self.ui.graphicsView.parent().mapFromParent(pos)
        pos = self.ui.graphicsView.mapFromParent(pos)
        pos = self.ui.graphicsView.mapToScene(pos)
        return pos

    @property
    def mouse_scene_pos(self):
        return self.map_from_global_to_scene(QPoint(self.mouse_x, self.mouse_y))

    def offset_point(self, point, dx, dy):
        return QPoint(point.x() + dx, point.y() + dy)

    def remove_floating_objects(self):
        try:
            self.views.remove(self.floating_model.view)
        except Exception:
            pass
        self.floating_model = None

        try:
            self.scene.removeItem(self.floating_line)
        except Exception:
            pass
        self.floating_line = None

    # Processes mouse events. Override of parent method.
    def eventFilter(self, source, event):
        if event.type() == QEvent.HoverMove and source is self:                  
            self.mouse_x = event.pos().x()
            self.mouse_y = event.pos().y()

            graphics_view_parent = self.ui.graphicsView.parent()
            mapped_event_pos = graphics_view_parent.mapFromParent(event.pos())
            inbounds = mapped_event_pos.x() >= 0 and \
                       mapped_event_pos.y() >= 0 and \
                       mapped_event_pos.x() < self.ui.graphicsView.width() and \
                       mapped_event_pos.y() < self.ui.graphicsView.height()

            if inbounds and self.state is ApplicationWindow.placing_module:
                width = self.floating_model.view.graphics_item.pixmap().width()
                height = self.floating_model.view.graphics_item.pixmap().height()
                self.floating_model.view.graphics_item.setPos(self.offset_point(self.mouse_scene_pos, -width, -height))
            elif inbounds and self.state is self.placing_readout:
                width = self.floating_model.view.graphics_item.rect().width()
                height = self.floating_model.view.graphics_item.rect().height()
                self.floating_model.view.graphics_item.setPos(self.offset_point(self.mouse_scene_pos, -width / 2, -height / 2))
            elif inbounds and self.state is ApplicationWindow.drawing_stream:
                p1 = self.floating_line.line().p1()
                p2 = self.mouse_scene_pos
                self.floating_line.setLine(QLineF(p1, p2))
            elif inbounds and self.state is ApplicationWindow.drawing_readout:
                p1 = self.floating_line.mapToScene(self.floating_line.line().p1()) 

                width = self.floating_model.view.graphics_item.rect().width()
                height = self.floating_model.view.graphics_item.rect().height()

                self.floating_model.view.graphics_item.setPos(self.offset_point(self.mouse_scene_pos, -width / 2, -height / 2))
                p1 = self.floating_line.mapFromScene(p1)
                p2 = self.floating_line.mapFromScene(self.mouse_scene_pos)
                self.floating_line.setLine(QLineF(p1, p2))
            elif inbounds and self.state is ApplicationWindow.dragging_joint_line:
                self.floating_model.view.set_joint_line(self.mouse_scene_pos)

        elif event.type() == QEvent.MouseButtonRelease:
            scene_pos = self.map_from_global_to_scene(event.pos())
            if self.state is ApplicationWindow.idle:
                pass
            elif self.state is ApplicationWindow.dragging_joint_line:
                self.state = ApplicationWindow.idle
                self.floating_model = None

        return super(ApplicationWindow, self).eventFilter(source, event)

    def mousePressEvent(self, event):
        scene_pos = self.map_from_global_to_scene(event.pos())
        if self.state is ApplicationWindow.idle:
            stream = self.check_for_click_collisions(scene_pos)
            if stream:
                self.state = ApplicationWindow.dragging_joint_line
                self.floating_model = stream
        elif self.state is ApplicationWindow.placing_module:
            self.place_module()
        elif self.state is ApplicationWindow.drawing_stream:
            self.complete_stream(scene_pos)
        elif self.state is ApplicationWindow.drawing_readout:
            self.complete_readout(scene_pos)
        elif self.state is ApplicationWindow.placing_readout:
            self.start_readout(scene_pos)

    def run_sim(self):
        self.state = ApplicationWindow.running
        self.timer.start()

    def stop_sim(self):
        self.state = ApplicationWindow.idle
        self.timer.stop()

    def check_for_click_collisions(self, pos):
        for stream in self.simulation.streams:
            if stream.view.check_for_joint_line_collision(pos):
                return stream
        return None

    @pyqtSlot()
    def create_source_slot(self):
        volume_fractions = {}
        for species in Event.registered_species:
            if species.name == 'fiber':
                volume_fractions[species] = 0.01
            elif species.name == 'water':
                volume_fractions[species] = 0.99

        self.add_module(Source(self, 'Source', 1000, volume_fractions))

    @pyqtSlot()
    def create_tank_slot(self):
        volume_fractions = {}
        for species in Event.registered_species:
            if species.name == 'fiber':
                volume_fractions[species] = 0.00014
            elif species.name == 'water':
                volume_fractions[species] = 0.99986

        self.add_module(Tank(self, 'Tank', 0, volume_fractions))

    @pyqtSlot()
    def create_pump_slot(self):
        self.add_module(Pump(self))

    @pyqtSlot()
    def create_sink_slot(self):
        self.add_module(Sink(self))

    @pyqtSlot()
    def create_splitter_slot(self):
        self.add_module(Splitter(self))

    @pyqtSlot()
    def create_hydrocyclone_slot(self):
        self.add_module(Hydrocyclone(self))

    @pyqtSlot()
    def create_joiner_slot(self):
        self.add_module(Joiner(self))

    @pyqtSlot()
    def create_joiner_pump_slot(self):
        self.add_module(JoinerPump(self))
            
    def add_module(self, module):
        self.state = self.placing_module
        module.view.add_to_scene(self.scene)
        width = module.view.graphics_item.pixmap().width()
        height = module.view.graphics_item.pixmap().height()
        module.view.graphics_item.setPos(self.offset_point(self.mouse_scene_pos, -width, -height))
        self.floating_model = module

    def place_module(self):
        self.state = self.idle
        self.floating_model = None

    def connection_clicked(self, graphics_item, event):
        scene_pos = graphics_item.mapToScene(event.pos())
        if self.state == ApplicationWindow.idle:
            self.create_stream(scene_pos)
        elif self.state == ApplicationWindow.drawing_stream:
            self.complete_stream(scene_pos)

    def create_stream(self, pos):
        self.floating_model = Stream(self)
        
        line = QLineF(pos, pos)
        self.floating_line = self.scene.addLine(line)
        self.floating_line.setZValue(-1)
        for colliding_item in self.scene.collidingItems(self.floating_line):
            for view in self.views:
                if isinstance(view.model, Connection) and view.graphics_item is colliding_item:
                    self.floating_model.add_connection(view.model)
                    self.state = self.drawing_stream
                    width = colliding_item.boundingRect().width()
                    height = colliding_item.boundingRect().height()
                    p1 = self.offset_point(colliding_item.scenePos(), width / 2 - 1, height / 2 - 1)
                    p2 = pos
                    pen = QPen()
                    pen.setWidth(2)
                    self.floating_line.setPen(pen)
                    self.floating_line.setLine(QLineF(p1, p2))  
                    
        if self.state is not ApplicationWindow.drawing_stream:
            self.state = self.idle
            self.floating_model.cleanup()
            self.remove_floating_objects()

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
                    self.floating_model.view.set_lines(self.floating_line.line())
                    self.floating_model.view.snap_line()
                    self.floating_model = None
                    self.floating_line = None
                    completed = True

        self.scene.removeItem(test_line_item)

        # If second connection to stream was not succesfully added
        if not completed:
            self.state = ApplicationWindow.idle

            # Remove initial connection made
            # if self.floating_model.inlet_connection:
            #     self.floating_model.remove_connection(self.floating_model.inlet_connection)
            # elif self.floating_model.outlet_connection:
            #     self.floating_model.remove_connection(self.floating_model.outlet_connection)
            self.floating_model.cleanup()
            self.remove_floating_objects()
    
    @pyqtSlot()
    def create_readout(self):
        self.state = self.placing_readout
        self.floating_model = Readout(self)
        self.scene.addItem(self.floating_model.view.graphics_item)
   
        width = self.floating_model.view.graphics_item.rect().width()
        height = self.floating_model.view.graphics_item.rect().height()

        self.floating_model.view.graphics_item.setPos(self.offset_point(self.mouse_scene_pos, -width / 2, -height / 2))

    @pyqtSlot()
    def create_fiber_readout(self):
        self.state = self.placing_readout
        self.floating_model = FiberReadout(self)
        self.scene.addItem(self.floating_model.view.graphics_item)
   
        width = self.floating_model.view.graphics_item.rect().width()
        height = self.floating_model.view.graphics_item.rect().height()

        self.floating_model.view.graphics_item.setPos(self.offset_point(self.mouse_scene_pos, -width / 2, -height / 2))

    def start_readout(self, pos):
        for colliding_item in self.scene.collidingItems(self.floating_model.view.graphics_item):
            if self.state is ApplicationWindow.idle:
                break
            for view in self.views:
                if type(view.model) is Stream and isinstance(view, StreamView) and colliding_item in view.line_items:
                    # If stream already has a Readout, cancel creation of new Readout.
                    if not self.floating_model.connect_to_stream(view.model):
                        self.state = ApplicationWindow.idle
                        break
                    else:
                        self.state = self.drawing_readout

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
            self.floating_model.cleanup()
            self.remove_floating_objects()

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