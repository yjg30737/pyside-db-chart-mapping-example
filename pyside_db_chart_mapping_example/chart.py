from PySide6.QtCharts import QChart, QChartView, QBarSeries, QVBarModelMapper, \
    QBarCategoryAxis, QValueAxis
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter
from PySide6.QtSql import QSqlQuery
from PySide6.QtWidgets import QVBoxLayout, QWidget

from pyside_db_chart_mapping_example.db import SqlTableModel


class ChartWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__idNameDict = {}
        self.__model = SqlTableModel()

    def __initUi(self):
        self.__chart = QChart()
        self.__chart.setAnimationOptions(QChart.AllAnimations)

        chartView = QChartView(self.__chart)
        chartView.setRenderHint(QPainter.Antialiasing)

        lay = QVBoxLayout()
        lay.addWidget(chartView)
        lay.setContentsMargins(0, 0, 0, 0)
        self.setLayout(lay)

    def mapDbModel(self, model: SqlTableModel):
        self.__model = model
        self.__model.added.connect(self.__addChartXCategory)
        self.__model.updated.connect(self.__updateChartXCategory)
        self.__model.deleted.connect(self.__removeChartXCategory)

        series = QBarSeries()
        self.__mapper = QVBarModelMapper(self)
        self.__mapper.setFirstBarSetColumn(4)
        self.__mapper.setLastBarSetColumn(6)
        self.__mapper.setFirstRow(0)
        self.__mapper.setRowCount(self.__model.rowCount())
        self.__mapper.setSeries(series)
        self.__mapper.setModel(self.__model)
        self.__chart.addSeries(series)

        # get name attributes
        getNameQuery = QSqlQuery()
        getNameQuery.prepare(f'SELECT id, name FROM {self.__model.tableName()} order by ID')
        getNameQuery.exec()
        nameLst = []
        while getNameQuery.next():
            name = getNameQuery.value('name')
            id = getNameQuery.value('id')
            self.__idNameDict[id] = name
            nameLst.append(name)

        self.__axisX = QBarCategoryAxis()
        self.__axisX.append(nameLst)
        self.__chart.addAxis(self.__axisX, Qt.AlignBottom)
        series.attachAxis(self.__axisX)
        axisY = QValueAxis()
        axisY.setTitleText('Score')
        self.__chart.addAxis(axisY, Qt.AlignLeft)
        series.attachAxis(axisY)

    def __addChartXCategory(self, id, name):
        self.__idNameDict[id] = name
        self.__axisX.append([name])
        self.__mapper.setRowCount(self.__model.rowCount())

    def __updateChartXCategory(self, id, newName):
        # get mapped name by id
        oldName = self.__idNameDict[id]
        self.__axisX.replace(oldName, newName)
        self.__idNameDict[id] = newName

    def __removeChartXCategory(self, names):
        # todo fix the bug
        #  incorrect row count of chart
        #  after removing the first row or consecutive rows including first

        # get id related to each name
        idLst = []
        for id, name in self.__idNameDict.items():
            if name in names:
                idLst.append(id)

        # delete the key/value pair in dictionary and category in chart
        for id in idLst:
            name = self.__idNameDict[id]
            self.__axisX.remove(name)
            del self.__idNameDict[id]
        self.__mapper.setRowCount(self.__model.rowCount())


