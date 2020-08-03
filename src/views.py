from enum import Enum

from PyQt5.QtGui import QPixmap, QTextBlockFormat, QTextCursor
from PyQt5.QtWidgets import QGraphicsPixmapItem, QGraphicsRectItem, QGraphicsTextItem, QGraphicsLineItem, QGraphicsEllipseItem
from PyQt5.QtCore import Qt, QPoint, QRectF

import src.models as models


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
        self.graphics_item = scene.addPixmap(self.pixmap)
        return self.graphics_item

    def remove_from_scene(self, scene):
        self.scene.removeItem(self.graphics_item)
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

    def init_text(self):
        width = self.graphics_item.boundingRect().width()
        height = self.graphics_item.boundingRect().height()
        self.text_item = QGraphicsTextItem(self.graphics_item)
        if self.orientation is ReadoutView.Orientation.vertical:
            self.text_item.setPos(width / 2, height / 2)
        else:
            self.text_item.setPos(width / 2, height / 2)
     

class StreamView(View):
    def __init__(self, model, multiline=None):
        super().__init__(model)
        self.multiline = multiline        


class ConnectionView(View):
    def __init__(self, model):
        super().__init__(model)
        if isinstance(self.model, models.PushInletConnection) or isinstance(self.model, models.PushOutletConnection):
            self.graphics_item = QGraphicsRectItem(0, 0, 15, 15)
            self.graphics_item.setBrush(Qt.black)

            inner_rect_item = QGraphicsRectItem(1, 1, 13, 13, self.graphics_item)
            inner_rect_item.setBrush(Qt.white)

            self.connection_marker_item = QGraphicsRectItem(4, 4, 7, 7, inner_rect_item)
            self.connection_marker_item.setBrush(Qt.red)
            self.connection_marker_item.setOpacity(0.3)
        else:
            self.graphics_item = QGraphicsEllipseItem(0, 0, 15, 15)
            self.graphics_item.setBrush(Qt.black)

            inner_circle_item = QGraphicsEllipseItem(1, 1, 13, 13, self.graphics_item)
            inner_circle_item.setBrush(Qt.white)

            self.connection_marker_item = QGraphicsEllipseItem(4, 4, 7, 7, inner_circle_item)
            self.connection_marker_item.setBrush(Qt.red)
            self.connection_marker_item.setOpacity(0.3)

    def set_pos(self, pos):
        self.graphics_item.setPos(pos)

    def set_connected(self, connected):
        if connected:
            self.connection_marker_item.setBrush(Qt.green)
        else:
            self.connection_marker_item.setBrush(Qt.red)

class ModuleView(View):
    def __init__(self, model, image_path):
        super().__init__(model, image_path)

    def add_to_scene(self, scene):
        self.graphics_item = scene.addPixmap(self.pixmap)
        self.set_connections()
        return self.graphics_item

    def set_connections(self):
        raise NotImplementedError


class SourceView(ModuleView):
    def __init__(self, model):
        super().__init__(model, 'assets/source.png')

    def set_connections(self):
        connection = self.model.outlet_connections[0]
        connection.view.graphics_item.setParentItem(self.graphics_item)
        connection.view.set_pos(QPoint(87, 17))


class TankView(ModuleView):
    def __init__(self, model):
        super().__init__(model, 'assets/source.png')

    def set_connections(self):
        connection = self.model.outlet_connections[0]
        connection.view.graphics_item.setParentItem(self.graphics_item)
        connection.view.set_pos(QPoint(87, 17))

class PumpView(ModuleView):
    def __init__(self, model):
        super().__init__(model, 'assets/sink.png')

    def set_connections(self):
        connection = self.model.inlet_connections[0]
        connection.view.graphics_item.setParentItem(self.graphics_item)
        connection.view.set_pos(QPoint(-5, -5))

        connection = self.model.outlet_connections[0]
        connection.view.graphics_item.setParentItem(self.graphics_item)
        connection.view.set_pos(QPoint(37, -5))

class SinkView(ModuleView):
    def __init__(self, model):
        super().__init__(model, 'assets/sink.png')

    def set_connections(self):
        connection = self.model.inlet_connections[0]
        connection.view.graphics_item.setParentItem(self.graphics_item)
        connection.view.set_pos(QPoint(-5, -5))


class SplitterView(ModuleView):
    def __init__(self, model):
        super().__init__(model, 'assets/splitter.png')

    def set_connections(self):
        connection = self.model.inlet_connections[0]
        connection.view.graphics_item.setParentItem(self.graphics_item)
        connection.view.set_pos(QPoint(-5, 37))

        connection = self.model.outlet_connections[0]
        connection.view.graphics_item.setParentItem(self.graphics_item)
        connection.view.set_pos(QPoint(36, -4))

        connection = self.model.outlet_connections[1]
        connection.view.graphics_item.setParentItem(self.graphics_item)
        connection.view.set_pos(QPoint(36, 78))


class HydrocycloneView(ModuleView):
    def __init__(self, model):
        super().__init__(model, 'assets/splitter.png')

    def set_connections(self):
        connection = self.model.inlet_connections[0]
        connection.view.graphics_item.setParentItem(self.graphics_item)
        connection.view.set_pos(QPoint(-5, 37))

        connection = self.model.outlet_connections[0]
        connection.view.graphics_item.setParentItem(self.graphics_item)
        connection.view.set_pos(QPoint(36, -4))

        connection = self.model.outlet_connections[1]
        connection.view.graphics_item.setParentItem(self.graphics_item)
        connection.view.set_pos(QPoint(36, 78))

class JoinerView(ModuleView):
    def __init__(self, model):
        super().__init__(model, 'assets/joiner.png')

    def set_connections(self):
        connection = self.model.inlet_connections[0]
        connection.view.graphics_item.setParentItem(self.graphics_item)
        connection.view.set_pos(QPoint(-5, 36))

        connection = self.model.inlet_connections[1]
        connection.view.graphics_item.setParentItem(self.graphics_item)
        connection.view.set_pos(QPoint(37, -5))

        connection = self.model.outlet_connections[0]
        connection.view.graphics_item.setParentItem(self.graphics_item)
        connection.view.set_pos(QPoint(78, 36))