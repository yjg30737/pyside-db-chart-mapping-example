from PySide6.QtCore import Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QPushButton


class ColorButton(QPushButton):
    colorChanged = Signal(QColor)

    def __init__(self, color, size=20):
        super().__init__()
        self.__initVal(color, size)
        self.__initUi()

    def __initVal(self, color, size):
        self.__color = QColor(color)
        self.__size = size

    def __initUi(self):
        self.setFixedSize(self.__size, self.__size)
        self.__initStyle()

    def setColor(self, rgb):
        if isinstance(rgb, tuple):
            r = int(rgb[0])
            g = int(rgb[1])
            b = int(rgb[2])
            self.__color = QColor(r, g, b)
        elif isinstance(rgb, QColor):
            self.__color = rgb
        self.__initStyle()
        self.colorChanged.emit(self.__color)

    def getColor(self):
        return self.__color

    def __initStyle(self):
        self.setStyleSheet(f'''
                            QPushButton 
                            {{
                            border-width:1px; 
                            border-radius: {str(self.__size//2)};
                            background-color: {self.__color.name()}; 
                            }}
                            '''
                            )