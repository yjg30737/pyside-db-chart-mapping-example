from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QDialog, QWidget, QVBoxLayout, QGroupBox, QFormLayout, QPushButton, QHBoxLayout

from pyside_db_chart_mapping_example.chart.settings.colorButton import ColorButton
from pyside_db_chart_mapping_example.chart.settings.colorPickerDialog import ColorPickerDialog


class SettingsDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.__initVal()
        self.__initUi()
        
    def __initVal(self):
        self.__settingsStruct = QSettings('chart_settings.ini', QSettings.IniFormat)
        self.__hoverColor = self.__settingsStruct.value('hoverColor', '#ff0000')
        self.__selectColor = self.__settingsStruct.value('selectColor', '#329b64')

    def __initUi(self):
        self.setWindowTitle('Chart Settings')

        self.__hoverColorBtn = ColorButton(self.__hoverColor)
        self.__selectColorBtn = ColorButton(self.__selectColor)

        self.__hoverColorBtn.clicked.connect(self.__setHoverColor)
        self.__selectColorBtn.clicked.connect(self.__setSelectColor)

        lay = QFormLayout()
        lay.addRow('Bar border\'s color when cursor is hovering on it', self.__hoverColorBtn)
        lay.addRow('Selected bar\'s color', self.__selectColorBtn)

        settingsGrpBox = QGroupBox()
        settingsGrpBox.setTitle('Chart Settings')
        settingsGrpBox.setLayout(lay)

        lay = QVBoxLayout()
        lay.addWidget(settingsGrpBox)

        topWidget = QWidget()
        topWidget.setLayout(lay)

        okBtn = QPushButton('OK')
        okBtn.clicked.connect(self.accept)

        closeBtn = QPushButton('Close')
        closeBtn.clicked.connect(self.close)

        lay = QHBoxLayout()
        lay.addWidget(okBtn)
        lay.addWidget(closeBtn)
        lay.setContentsMargins(0, 0, 0, 0)

        bottomWidget = QWidget()
        bottomWidget.setLayout(lay)

        lay = QVBoxLayout()
        lay.addWidget(topWidget)
        lay.addWidget(bottomWidget)

        self.setLayout(lay)

    def __setHoverColor(self):
        dialog = ColorPickerDialog(self.__hoverColorBtn.getColor())
        reply = dialog.exec()
        if reply == QDialog.Accepted:
            newColor = dialog.getColor()
            self.__hoverColorBtn.setColor(newColor)
            self.__settingsStruct.setValue('hoverColor', newColor.name())

    def __setSelectColor(self):
        dialog = ColorPickerDialog(self.__selectColorBtn.getColor())
        reply = dialog.exec()
        if reply == QDialog.Accepted:
            newColor = dialog.getColor()
            self.__selectColorBtn.setColor(newColor)
            self.__settingsStruct.setValue('selectColor', newColor.name())

    def getHoverColor(self):
        return self.__hoverColorBtn.getColor()

    def getSelectColor(self):
        return self.__selectColorBtn.getColor()