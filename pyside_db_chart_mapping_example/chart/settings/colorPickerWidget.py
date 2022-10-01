import colorsys

from PySide6.QtGui import QColor
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QGridLayout

from pyside_db_chart_mapping_example.chart.settings.colorEditorWidget import ColorEditorWidget
from pyside_db_chart_mapping_example.chart.settings.colorHueBarWidget import ColorHueBarWidget
from pyside_db_chart_mapping_example.chart.settings.colorSquareWidget import ColorSquareWidget


class ColorPickerWidget(QWidget):
    colorChanged = Signal(QColor)

    def __init__(self, color=QColor(255, 255, 255), orientation='horizontal'):
        super().__init__()
        if isinstance(color, QColor):
            pass
        elif isinstance(color, str):
            color = QColor(color)
        self.__initUi(color=color, orientation=orientation)

    def __initUi(self, color, orientation):
        self.__colorSquareWidget = ColorSquareWidget(color)
        self.__colorSquareWidget.colorChanged.connect(self.__colorChanged)

        self.__colorHueBarWidget = ColorHueBarWidget(color)
        self.__colorHueBarWidget.hueChanged.connect(self.__hueChanged)
        self.__colorHueBarWidget.hueChangedByEditor.connect(self.__hueChangedByEditor)

        self.__colorEditorWidget = ColorEditorWidget(color, orientation=orientation)
        self.__colorEditorWidget.colorChanged.connect(self.__colorChangedByEditor)

        if orientation == 'horizontal':
            lay = QHBoxLayout()
            lay.addWidget(self.__colorSquareWidget)
            lay.addWidget(self.__colorHueBarWidget)
            lay.addWidget(self.__colorEditorWidget)
        elif orientation == 'vertical':
            lay = QGridLayout()
            lay.addWidget(self.__colorSquareWidget, 0, 0, 1, 1)
            lay.addWidget(self.__colorHueBarWidget, 0, 1, 1, 1)
            lay.addWidget(self.__colorEditorWidget, 1, 0, 1, 2)
        lay.setAlignment(Qt.AlignTop)

        mainWidget = QWidget()
        mainWidget.setLayout(lay)
        lay.setContentsMargins(0, 0, 0, 0)

        self.setLayout(lay)

    def __hueChanged(self, h):
        self.__colorSquareWidget.changeHue(h)

    def __hueChangedByEditor(self, h):
        self.__colorSquareWidget.changeHueByEditor(h)

    def hsv2rgb(self, h, s, v):
        return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h, s, v))

    def __colorChanged(self, h, s, l):
        r, g, b = self.hsv2rgb(h / 100, s, l)
        color = QColor(r, g, b)
        self.__colorEditorWidget.setColor(color)
        self.colorChanged.emit(color)

    def __colorChangedByEditor(self, color: QColor):
        h, s, v = colorsys.rgb_to_hsv(color.redF(), color.greenF(), color.blueF())
        self.__colorHueBarWidget.moveSelectorByEditor(h)
        self.__colorSquareWidget.moveSelectorByEditor(s, v)
        self.colorChanged.emit(color)

    def getCurrentColor(self):
        return self.__colorEditorWidget.getCurrentColor()