from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit

from .model_dialog import Ui_Dialog

class ModelDialog(QDialog):
    def __init__(self, model, rows=10, columns=5):
        super().__init__()
        self.model = model
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.fields_table = self.ui.tableWidget
        self.fields_table.setShowGrid(False)
        self.fields_table.verticalHeader().hide()
        self.fields_table.horizontalHeader().hide()
        self.fields_table.setRowCount(rows)
        self.fields_table.setColumnCount(columns)
        self.fields_table.setFocusPolicy(Qt.NoFocus)

        self.init_dialog()


    def init_dialog(self): 
        self.fields_table.setColumnWidth(0, 60)
        self.fields_table.setColumnWidth(1, 60)

        self.fields_table.setCellWidget(0, 0, QLabel('Name'))
        self.fields_table.setCellWidget(0, 1, QLineEdit(self.model.name))

    def accept(self):
        if self.ok():
            super().accept()

    def reject(self):
        if self.cancel():
            super().reject()

    def ok(self):
        self.model.name = self.fields_table.cellWidget(0, 1).text()
        return True

    def cancel(self):
        return True

class SourceDialog(ModelDialog):
    def __init__(self, model):
        super().__init__(model)

    def init_dialog(self):
        super().init_dialog()
        self.fields_table.setCellWidget(1, 0, QLabel('Flowrate'))
        self.fields_table.setCellWidget(1, 1, QLineEdit(str(self.model.capacity())))
        self.fields_table.setCellWidget(1, 2, QLabel(f'm\N{SUPERSCRIPT THREE} / min'))
        i = 2
        for species, fraction in self.model.volumetric_fractions.items():
            self.fields_table.setCellWidget(i, 0, QLabel(species.name))
            self.fields_table.setCellWidget(i, 1, QLineEdit(str(fraction)))
            i += 1

    def ok(self):
        super().ok()
        accum = 0
        for j in range(2, self.fields_table.rowCount()):
            try:
                accum += float(self.fields_table.cellWidget(j, 1).text())
            except Exception:
                pass
        
        if accum != 1:
            return False

        for species, fraction in self.model.volumetric_fractions.items():
            for j in range(self.fields_table.rowCount()):
                try:
                    if self.fields_table.cellWidget(j, 0).text() == species.name:
                        self.model.volumetric_fractions[species] = float(self.fields_table.cellWidget(j, 1).text())
                except Exception:
                    pass
        
        return True

class TankDialog(ModelDialog):
    def __init__(self, model):
        super().__init__(model)

    def init_dialog(self):
        super().init_dialog()

        i = 1
        for species, fraction in self.model.volumetric_fractions.items():
            self.fields_table.setCellWidget(i, 0, QLabel(species.name))
            self.fields_table.setCellWidget(i, 1, QLineEdit(str(fraction)))
            i += 1

    def ok(self):
        super().ok()
        accum = 0
        for j in range(1, self.fields_table.rowCount()):
            try:
                accum += float(self.fields_table.cellWidget(j, 1).text())
            except Exception:
                pass
        
        if accum != 1:
            return False

        for species, fraction in self.model.volumetric_fractions.items():
            for j in range(self.fields_table.rowCount()):
                try:
                    if self.fields_table.cellWidget(j, 0).text() == species.name:
                        self.model.volumetric_fractions[species] = float(self.fields_table.cellWidget(j, 1).text())
                except Exception:
                    pass
        
        return True

class PumpDialog(ModelDialog):
    def __init__(self, model):
        super().__init__(model)

    def init_dialog(self):
        super().init_dialog()
        self.fields_table.setCellWidget(1, 0, QLabel('Flowrate'))
        self.fields_table.setCellWidget(1, 1, QLineEdit(str(self.model.capacity())))
        self.fields_table.setCellWidget(1, 2, QLabel(f'm\N{SUPERSCRIPT THREE} / min'))


    def ok(self):
        super().ok()
        self.model.set_capacity(float(self.fields_table.cellWidget(1, 1).text()))
        return True


class HydrocycloneDialog(ModelDialog):
    def __init__(self, model):
        super().__init__(model)

    def init_dialog(self):
        super().init_dialog()
        self.fields_table.setColumnWidth(1, 100)
        self.fields_table.setCellWidget(1, 0, QLabel('RRV'))
        self.fields_table.setCellWidget(1, 1, QLineEdit(str(self.model.rrv)))
        self.fields_table.setCellWidget(2, 0, QLabel('RRW'))
        self.fields_table.setCellWidget(2, 1, QLineEdit(str(self.model.rrw)))

    def ok(self):
        super().ok()
        self.model.rrv = float(self.fields_table.cellWidget(1, 1).text())
        self.model.rrw = float(self.fields_table.cellWidget(2, 1).text())
        return True


    
