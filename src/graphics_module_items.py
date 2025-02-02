from PyQt5.QtWidgets import QGraphicsPixmapItem, QGraphicsRectItem, QGraphicsEllipseItem


class GraphicsModuleItem(QGraphicsPixmapItem):
    def __init__(self, model):
        super().__init__()
        self.model = model

    def mousePressEvent(self, event):
        self.model.dialog = self.model.dialog_class(self.model)
        self.model.dialog.show()

class GraphicsPushSocketItem(QGraphicsRectItem):
    def __init__(self, model, x, y, width, height):
        super().__init__(x, y, width, height)
        self.model = model

    def mousePressEvent(self, event):
        self.model.gui.socket_clicked(self, event)

class GraphicsPullSocketItem(QGraphicsEllipseItem):
    def __init__(self, model, x, y, width, height):
        super().__init__(x, y, width, height)
        self.model = model

    def mousePressEvent(self, event):
        self.model.gui.socket_clicked(self, event)