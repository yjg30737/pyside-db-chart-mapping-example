import sys

from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QApplication

from pyside_db_chart_mapping_example.chart import ChartWidget
from pyside_db_chart_mapping_example.db import *


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        if not createConnection():
            sys.exit(1)
        initTable()
        addSample()

        dbWidget = DatabaseWidget()
        chartWidget = ChartWidget()
        chartWidget.mapDb(dbWidget)

        lay = QHBoxLayout()
        lay.addWidget(dbWidget)
        lay.addWidget(chartWidget)

        mainWidget = QWidget()
        mainWidget.setLayout(lay)

        self.setCentralWidget(mainWidget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Window()
    ex.show()
    app.exec()

