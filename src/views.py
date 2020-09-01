from enum import Enum

from PyQt5.QtGui import QPixmap, QTextBlockFormat, QTextCursor, QPen
from PyQt5.QtWidgets import QGraphicsPixmapItem, QGraphicsRectItem, QGraphicsTextItem, QGraphicsLineItem, QGraphicsEllipseItem
from PyQt5.QtCore import Qt, QPoint, QRectF, QLineF, QPointF

import src.models as models
from src.graphics_module_items import GraphicsModuleItem, GraphicsPushSocketItem, GraphicsPullSocketItem


class View:
    def __init__(self, model, image_path=None):
        self.model = model
        self.model.gui.views.append(self)
        self.image_path = image_path
        if self.image_path:
            self.pixmap = QPixmap(self.image_path)
        else:
            self.pixmap = None
        self.graphics_item = None
    
    def add_to_scene(self, scene):
        self.graphics_item = GraphicsModuleItem(self.model)
        self.graphics_item.setPixmap(self.pixmap)
        scene.addItem(self.graphics_item)
        return self.graphics_item

    def remove_from_scene(self):
        self.model.gui.scene.removeItem(self.graphics_item)
        self.model.gui.views.remove(self)


class ReadoutView(View):
    class Orientation(Enum):
        horizontal = 1
        vertical = 2

    def __init__(self, model):
        super().__init__(model)
        self.graphics_item = QGraphicsRectItem(0, 0, 9, 9)
        self.graphics_item.setBrush(Qt.black)

        inner_rect_item = QGraphicsRectItem(1, 1, 7, 7, self.graphics_item)
        inner_rect_item.setBrush(Qt.white)

        self.text_item = None
        self.orientation = ReadoutView.Orientation.horizontal

    def line(self):
        for child in self.graphics_item.childItems():
            if isinstance(child, QGraphicsLineItem):
                return child.line()

    def line_item(self):
        for child in self.graphics_item.childItems():
            if isinstance(child, QGraphicsLineItem):
                return child

    def init_text(self):
        width = self.graphics_item.boundingRect().width()
        height = self.graphics_item.boundingRect().height()
        self.text_item = QGraphicsTextItem(self.graphics_item)
        self.text_item.setPos(width / 2 + 2, -height)
     

class StreamView(View):
    def __init__(self, model):
        super().__init__(model)
        self.line_pairs = []
        self.line_weight = 2
        self.pen = QPen()
        self.pen.setWidth(self.line_weight)
        self.joint_collision_radius = 2

    def set_lines(self, *args):
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
        scene = self.model.gui.scene
        scene.addItem(line_item)
        pair = (line, line_item)
        self.line_pairs.append(pair)
        return pair

    def set_pen(self, pen):
        self.pen = pen
        for _, line_item in self.line_pairs:
            line_item.setPen(self.pen)

    def snap_line(self):
        line, line_item = self.line_pairs[0]

        start_pos = line.p1()
        end_pos = line.p2()

        horizontal_midpoint = (start_pos.x() + end_pos.x()) / 2

        line1 = QLineF(start_pos.x(), start_pos.y(), horizontal_midpoint, start_pos.y())
        line2 = QLineF(horizontal_midpoint, start_pos.y(), horizontal_midpoint, end_pos.y())
        line3 = QLineF(horizontal_midpoint, end_pos.y(), end_pos.x(), end_pos.y())

        line_item.setLine(line1)
        self.add_graphics_line_item(line2)
        self.add_graphics_line_item(line3)

    def set_joint_line(self, pos):
        left_line_item = self.get_left_line_item()
        left_line = left_line_item.line()
        joint_line_item = self.get_joint_line_item()
        joint_line = joint_line_item.line()
        right_line_item = self.get_right_line_item()
        right_line = right_line_item.line()

        if (pos.x() < min(left_line.x1(), left_line.x2()) 
           or pos.x() > max(right_line.x1(), right_line.x2())):
            return

        if left_line.x1() < left_line.x2():
            left_line.setP2(QPointF(pos.x(), left_line.y1()))
        else:
            left_line.setP1(QPointF(pos.x(), left_line.y1()))

        joint_line.setP1(QPointF(pos.x(), joint_line.y1()))
        joint_line.setP2(QPointF(pos.x(), joint_line.y2()))

        if right_line.x1() < right_line.x2():
            right_line.setP1(QPointF(pos.x(), right_line.y1()))
        else:
            right_line.setP2(QPointF(pos.x(), right_line.y1()))

        left_line_item.setLine(left_line)
        joint_line_item.setLine(joint_line)
        right_line_item.setLine(right_line)

        self.adjust_connected_views()

    def adjust_connected_views(self):
        readout = self.model.readout
        if not readout:
            return

        left_line_item = self.get_left_line_item()
        left_line = left_line_item.line()
        joint_line_item = self.get_joint_line_item()
        joint_line = joint_line_item.line()
        right_line_item = self.get_right_line_item()
        right_line = right_line_item.line()

        readout_line_item = readout.view.line_item()
        readout_line = readout_line_item.line()

        mapped_readout_p1 = readout_line_item.mapToScene(readout_line.p1())
        mapped_readout_p2 = readout_line_item.mapToScene(readout_line.p2())

        # Determine which line of this Stream the Readout is connected to.
        if mapped_readout_p1.y() == left_line.y1() or mapped_readout_p2 == left_line.y1(): # Left line.
            if mapped_readout_p2.x() > joint_line.x1():
                dx = mapped_readout_p2.x() - joint_line.x1()
                readout_line_item.parentItem().moveBy(-dx, 0)
        else: # Right line.
            if mapped_readout_p2.x() < joint_line.x1():
                dx = joint_line.x1() - mapped_readout_p2.x()
                readout_line_item.parentItem().moveBy(dx, 0)

        readout_line_item.setLine(readout_line)

    def get_joints(self):
        joints = []
        for line1 in self.line_items:
            for line2 in self.line_items:
                point = None
                if line1 is line2:
                    continue
                if line1.line().p1() == line2.line().p1() or line1.line().p1() == line2.line().p2():
                    point = line1.line().p1()
                elif line1.line().p2() == line2.line().p1() or line1.line().p2() == line2.line().p2():
                    point = line1.line().p2()
                else:
                    continue
                
                # Ensure point is not already in joints before adding.
                for joint in joints:
                    if point == joint:
                        break
                else:
                    joints.append(point)

        return joints

    def get_joint_line(self):
        for line_item in self.line_items:
            line = line_item.line()
            if line.x1() == line.x2():
                return line

    def get_joint_line_item(self):
        for line_item in self.line_items:
            line = line_item.line()
            if line.x1() == line.x2():
                return line_item

    def get_left_line_item(self):
        leftmost_line_item = None
        for line_item in self.line_items:
            if (not leftmost_line_item
                or min(line_item.line().x1(), line_item.line().x2()) 
                < min(leftmost_line_item.line().x1(), leftmost_line_item.line().x2())):
               leftmost_line_item = line_item
            
        return leftmost_line_item

    def get_right_line_item(self):
        rightmost_line_item = None
        for line_item in self.line_items:
            if (not rightmost_line_item 
                or max(line_item.line().x1(), line_item.line().x2()) 
                > max(rightmost_line_item.line().x1(), rightmost_line_item.line().x2())):
               rightmost_line_item = line_item
            
        return rightmost_line_item

    def check_for_joint_collision(self, pos):
        for joint in self.get_joints():
            line = QLineF(joint, pos)
            if line.length() <= self.joint_collision_radius:
                return True
        return False

    def check_for_joint_line_collision(self, pos):
        joint_line = self.get_joint_line()
        joint_line_top = min(joint_line.y1(), joint_line.y2()) 
        joint_line_bot = max(joint_line.y1(), joint_line.y2()) 

        if abs(joint_line.x1() - pos.x()) > self.line_weight / 2 + self.joint_collision_radius:
            return False

        if (pos.y() >= joint_line_top - self.joint_collision_radius 
            and pos.y() <= joint_line_bot + self.joint_collision_radius):
            return True
        else:
            return False


class SocketView(View):
    def __init__(self, model):
        super().__init__(model)
        if isinstance(self.model, models.PushInletSocket):
            self.graphics_item = GraphicsPushSocketItem(model, 0, 0, 15, 15)
            self.graphics_item.setBrush(Qt.black)

            inner_rect_item = QGraphicsRectItem(1, 1, 13, 13, self.graphics_item)
            inner_rect_item.setBrush(Qt.white)

            self.socket_marker_item = QGraphicsRectItem(4, 4, 7, 7, inner_rect_item)
            self.socket_marker_item.setBrush(Qt.red)
            self.socket_marker_item.setOpacity(0.3)
        elif isinstance(self.model, models.PushOutletSocket):
            self.graphics_item = GraphicsPushSocketItem(model, 0, 0, 15, 15)
            self.graphics_item.setBrush(Qt.black)

            inner_rect_item = QGraphicsRectItem(2, 2, 11, 11, self.graphics_item)
            inner_rect_item.setBrush(Qt.white)

            self.socket_marker_item = QGraphicsRectItem(4, 4, 7, 7, inner_rect_item)
            self.socket_marker_item.setBrush(Qt.red)
            self.socket_marker_item.setOpacity(0.3)
        elif isinstance(self.model, models.PullInletSocket):
            self.graphics_item = GraphicsPullSocketItem(model, 0, 0, 15, 15)
            self.graphics_item.setBrush(Qt.black)

            inner_circle_item = QGraphicsEllipseItem(1, 1, 13, 13, self.graphics_item)
            inner_circle_item.setBrush(Qt.white)

            self.socket_marker_item = QGraphicsEllipseItem(4, 4, 7, 7, inner_circle_item)
            self.socket_marker_item.setBrush(Qt.red)
            self.socket_marker_item.setOpacity(0.3)
        elif isinstance(self.model, models.PullOutletSocket):
            self.graphics_item = GraphicsPullSocketItem(model, 0, 0, 15, 15)
            self.graphics_item.setBrush(Qt.black)

            inner_circle_item = QGraphicsEllipseItem(2, 2, 11, 11, self.graphics_item)
            inner_circle_item.setBrush(Qt.white)

            self.socket_marker_item = QGraphicsEllipseItem(4, 4, 7, 7, inner_circle_item)
            self.socket_marker_item.setBrush(Qt.red)
            self.socket_marker_item.setOpacity(0.3)

    def set_pos(self, pos):
        self.graphics_item.setPos(pos)

    def set_connected(self, connected):
        if connected:
            self.socket_marker_item.setBrush(Qt.green)
        else:
            self.socket_marker_item.setBrush(Qt.red)

class ModuleView(View):
    def __init__(self, model, image_path):
        super().__init__(model, image_path)

    def add_to_scene(self, scene):
        super().add_to_scene(scene)
        self.set_sockets()
        return self.graphics_item

    def set_sockets(self):
        raise NotImplementedError


class SourceView(ModuleView):
    def __init__(self, model):
        super().__init__(model, 'assets/source.png')

    def set_sockets(self):
        socket = self.model.outlet_sockets[0]
        socket.view.graphics_item.setParentItem(self.graphics_item)
        socket.view.set_pos(QPoint(85, 90))


class TankView(ModuleView):
    def __init__(self, model):
        super().__init__(model, 'assets/tank.png')

    def set_sockets(self):
        socket = self.model.outlet_sockets[0]
        socket.view.graphics_item.setParentItem(self.graphics_item)
        socket.view.set_pos(QPoint(85, 90))


class SinkView(ModuleView):
    def __init__(self, model):
        super().__init__(model, 'assets/sink.png')

    def set_sockets(self):
        socket = self.model.inlet_sockets[0]
        socket.view.graphics_item.setParentItem(self.graphics_item)
        socket.view.set_pos(QPoint(-6, 8))


class SplitterView(ModuleView):
    def __init__(self, model):
        super().__init__(model, 'assets/splitter.png')

    def set_sockets(self):
        socket = self.model.inlet_sockets[0]
        socket.view.graphics_item.setParentItem(self.graphics_item)
        socket.view.set_pos(QPoint(-9, 21))

        socket = self.model.outlet_sockets[0]
        socket.view.graphics_item.setParentItem(self.graphics_item)
        socket.view.set_pos(QPoint(20, -7))

        socket = self.model.outlet_sockets[1]
        socket.view.graphics_item.setParentItem(self.graphics_item)
        socket.view.set_pos(QPoint(20, 48))


class HydrocycloneView(ModuleView):
    def __init__(self, model):
        super().__init__(model, 'assets/hydrocyclone.png')

    def set_sockets(self):
        socket = self.model.inlet_sockets[0]
        socket.view.graphics_item.setParentItem(self.graphics_item)
        socket.view.set_pos(QPoint(-8, 18))

        socket = self.model.outlet_sockets[0]
        socket.view.graphics_item.setParentItem(self.graphics_item)
        socket.view.set_pos(QPoint(26, -6))

        socket = self.model.outlet_sockets[1]
        socket.view.graphics_item.setParentItem(self.graphics_item)
        socket.view.set_pos(QPoint(26, 120))

class JoinerView(ModuleView):
    def __init__(self, model):
        super().__init__(model, 'assets/joiner.png')

    def set_sockets(self):
        socket = self.model.inlet_sockets[0]
        socket.view.graphics_item.setParentItem(self.graphics_item)
        socket.view.set_pos(QPoint(-7, 20))

        socket = self.model.inlet_sockets[1]
        socket.view.graphics_item.setParentItem(self.graphics_item)
        socket.view.set_pos(QPoint(21, -8))

        socket = self.model.outlet_sockets[0]
        socket.view.graphics_item.setParentItem(self.graphics_item)
        socket.view.set_pos(QPoint(49, 20))

class PumpView(ModuleView):
    def __init__(self, model):
        super().__init__(model, 'assets/pump.png')

    def set_sockets(self):
        socket = self.model.inlet_sockets[0]
        socket.view.graphics_item.setParentItem(self.graphics_item)
        socket.view.set_pos(QPoint(-6, 16))

        socket = self.model.inlet_sockets[1]
        socket.view.graphics_item.setParentItem(self.graphics_item)
        socket.view.set_pos(QPoint(5, 38))

        socket = self.model.outlet_sockets[0]
        socket.view.graphics_item.setParentItem(self.graphics_item)
        socket.view.set_pos(QPoint(76, 2))