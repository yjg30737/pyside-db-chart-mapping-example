from PySide6.QtCharts import QChart, QChartView, QBarSeries, QVBarModelMapper, \
    QBarCategoryAxis, QValueAxis
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QVBoxLayout, QWidget


class ChartWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        self.__chart = QChart()
        self.__chart.setAnimationOptions(QChart.AllAnimations)

        chartView = QChartView(self.__chart)
        chartView.setRenderHint(QPainter.Antialiasing)

        lay = QVBoxLayout()
        lay.addWidget(chartView)
        lay.setContentsMargins(0, 0, 0, 0)
        self.setLayout(lay)

    def mapDb(self, db):
        db.deleted.connect(self.__removeChartXCategory)
        model = db.getModel()

        series = QBarSeries()
        mapper = QVBarModelMapper(self)
        mapper.setFirstBarSetColumn(4)
        mapper.setLastBarSetColumn(6)
        mapper.setFirstRow(0)
        mapper.setRowCount(model.rowCount())
        mapper.setSeries(series)
        mapper.setModel(model)
        self.__chart.addSeries(series)

        self.__axisX = QBarCategoryAxis()
        self.__axisX.append(['Joe', 'Lara', 'David', 'Jane'])
        self.__chart.addAxis(self.__axisX, Qt.AlignBottom)
        series.attachAxis(self.__axisX)
        axisY = QValueAxis()
        axisY.setTitleText('Score')
        self.__chart.addAxis(axisY, Qt.AlignLeft)
        series.attachAxis(axisY)

    def __removeChartXCategory(self, names):
        for name in names:
            self.__axisX.remove(name)