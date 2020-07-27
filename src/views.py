from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsPixmapItem
from PyQt5.QtCore import QPoint

class View:
    def __init__(self, model, image_path):
        self.model = model
        self.model.gui.views.append(self)
        self.image_path = image_path
        self.pixmap = QPixmap(self.image_path)
        self.graphics_item = None
    
    def add_to_scene(self, scene):
        self.graphics_item = scene.addPixmap(self.pixmap)
        return self.graphics_item

class ModuleView(View):
    def __init__(self, model, image_path):
        super().__init__(model, image_path)

    def add_to_scene(self, scene):
        self.graphics_item = scene.addPixmap(self.pixmap)
        self.set_connections()
        return self.graphics_item

    def set_connections(self):
        pass


class ConnectionView(ModuleView):
    def __init__(self, model):
        super().__init__(model, 'assets/connection.png')


class SourveView(ModuleView):
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