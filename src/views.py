from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsPixmapItem, QGraphicsRectItem
from PyQt5.QtCore import QPoint, QRectF

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


class ReadoutView(View):
    def __init__(self, model):
        super().__init__(model)
        self.rect = QRectF(0, 0, 15, 15)

    def add_to_scene(self, scene):
        self.graphics_item = scene.addItem(QGraphicsRectItem(self.rect))
        return self.graphics_item

class StreamView(View):
    def __init__(self, model, multiline=None):
        super().__init__(model)
        self.multiline = multiline

class ConnectionView(View):
    def __init__(self, model):
        super().__init__(model, 'assets/connection.png')


class ModuleView(View):
    def __init__(self, model, image_path):
        super().__init__(model, image_path)

    def add_to_scene(self, scene):
        self.graphics_item = scene.addPixmap(self.pixmap)
        self.set_connections()
        return self.graphics_item

    def set_connections(self):
        pass


class SourceView(ModuleView):
    def __init__(self, model):
        super().__init__(model, 'assets/source.png')

    def set_connections(self):
        connection = self.model.outlet_connections[0]
        connection.view.graphics_item = QGraphicsPixmapItem(connection.view.pixmap, self.graphics_item)
        connection.view.graphics_item.setPos(QPoint(87, 17))


class SinkView(ModuleView):
    def __init__(self, model):
        super().__init__(model, 'assets/sink.png')

    def set_connections(self):
        connection = self.model.inlet_connections[0]
        connection.view.graphics_item = QGraphicsPixmapItem(connection.view.pixmap, self.graphics_item)
        connection.view.graphics_item.setPos(QPoint(-5, -5))


class SplitterView(ModuleView):
    def __init__(self, model):
        super().__init__(model, 'assets/splitter.png')

    def set_connections(self):
        connection = self.model.inlet_connections[0]
        connection.view.graphics_item = QGraphicsPixmapItem(connection.view.pixmap, self.graphics_item)
        connection.view.graphics_item.setPos(QPoint(-5, 37))

        connection = self.model.outlet_connections[0]
        connection.view.graphics_item = QGraphicsPixmapItem(connection.view.pixmap, self.graphics_item)
        connection.view.graphics_item.setPos(QPoint(36, -4))

        connection = self.model.outlet_connections[1]
        connection.view.graphics_item = QGraphicsPixmapItem(connection.view.pixmap, self.graphics_item)
        connection.view.graphics_item.setPos(QPoint(36, 78))


class JoinerView(ModuleView):
    def __init__(self, model):
        super().__init__(model, 'assets/joiner.png')

    def set_connections(self):
        connection = self.model.inlet_connections[0]
        connection.view.graphics_item = QGraphicsPixmapItem(connection.view.pixmap, self.graphics_item)
        connection.view.graphics_item.setPos(QPoint(-5, 36))

        connection = self.model.inlet_connections[1]
        connection.view.graphics_item = QGraphicsPixmapItem(connection.view.pixmap, self.graphics_item)
        connection.view.graphics_item.setPos(QPoint(37, -5))

        connection = self.model.outlet_connections[0]
        connection.view.graphics_item = QGraphicsPixmapItem(connection.view.pixmap, self.graphics_item)
        connection.view.graphics_item.setPos(QPoint(78, 36))