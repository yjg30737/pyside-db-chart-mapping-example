import sys

from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QApplication, QSplitter

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
        model = dbWidget.getModel()
        chartWidget.mapDbModel(model)

        mainWidget = QSplitter()
        mainWidget.addWidget(dbWidget)
        mainWidget.addWidget(chartWidget)
        mainWidget.setChildrenCollapsible(False)
        mainWidget.setSizes([400, 600])
        mainWidget.setHandleWidth(1)
        mainWidget.setStyleSheet(
            "QSplitterHandle {background-color: lightgray;}")

        self.setCentralWidget(mainWidget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Window()
    ex.show()
    app.exec()

