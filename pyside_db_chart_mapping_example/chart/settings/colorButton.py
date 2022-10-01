from PySide6.QtCore import Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QPushButton


class ColorButton(QPushButton):
    colorChanged = Signal(QColor)

    def __init__(self, size=20, r=255, g=255, b=255):
        super().__init__()
        self.__initVal(size, r, g, b)
        self.__initUi()

    def __initVal(self, size, r, g, b):
        self.__color = QColor(r, g, b)
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