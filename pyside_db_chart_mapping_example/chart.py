from PySide6.QtCharts import QChart, QChartView, QBarSeries, QVBarModelMapper, \
    QBarCategoryAxis, QValueAxis
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter
from PySide6.QtSql import QSqlQuery
from PySide6.QtWidgets import QVBoxLayout, QWidget, QListWidget, QListWidgetItem, QTextBrowser, QSplitter, QCheckBox, \
    QFormLayout, QHBoxLayout, QLabel, QSpacerItem, QSizePolicy

from pyside_db_chart_mapping_example.db import SqlTableModel


class CheckBoxListWidget(QListWidget):
    checkedSignal = Signal(int, Qt.CheckState)

    def __init__(self):
        super().__init__()
        self.itemChanged.connect(self.__sendCheckedSignal)

    def __sendCheckedSignal(self, item):
        r_idx = self.row(item)
        state = item.checkState()
        self.checkedSignal.emit(r_idx, state)

    def addItems(self, items) -> None:
        for item in items:
            self.addItem(item)

    def addItem(self, item) -> None:
        if isinstance(item, str):
            item = QListWidgetItem(item)
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(Qt.Unchecked)
        super().addItem(item)

    def toggleState(self, state):
        state = Qt.Checked if state == 2 else Qt.Unchecked
        for i in range(self.count()):
            item = self.item(i)
            item.setCheckState(state)

    def getCheckedRows(self):
        return self.__getFlagRows(Qt.Checked)

    def getUncheckedRows(self):
        return self.__getFlagRows(Qt.Unchecked)

    def __getFlagRows(self, flag: Qt.CheckState):
        flag_lst = []
        for i in range(self.count()):
            item = self.item(i)
            if item.checkState() == flag:
                flag_lst.append(i)

        return flag_lst

    def removeCheckedRows(self):
        self.__removeFlagRows(Qt.Checked)

    def removeUncheckedRows(self):
        self.__removeFlagRows(Qt.Unchecked)

    def __removeFlagRows(self, flag):
        flag_lst = self.__getFlagRows(flag)
        flag_lst = reversed(flag_lst)
        for i in flag_lst:
            self.takeItem(i)


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

        # left widget
        ## left top widget
        self.__barsetCheckBoxListWidget = CheckBoxListWidget()
        self.__barsetCheckBoxListWidget.checkedSignal.connect(self.__showSeries)

        barsetAllCheckBox = QCheckBox('Check all')
        barsetAllCheckBox.setChecked(True)
        barsetAllCheckBox.stateChanged.connect(self.__barsetCheckBoxListWidget.toggleState)

        lay = QHBoxLayout()
        lay.addWidget(QLabel('BarSet'))
        lay.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.MinimumExpanding))
        lay.addWidget(barsetAllCheckBox)
        lay.setContentsMargins(0, 0, 0, 0)

        leftTopMenuWidget = QWidget()
        leftTopMenuWidget.setLayout(lay)

        lay = QVBoxLayout()
        lay.addWidget(leftTopMenuWidget)
        lay.addWidget(self.__barsetCheckBoxListWidget)

        leftTopWidget = QWidget()
        leftTopWidget.setLayout(lay)

        ## left bottom widget
        self.__axisCheckBoxListWidget = CheckBoxListWidget()
        self.__axisCheckBoxListWidget.checkedSignal.connect(self.__showAxisItem)

        axisAllCheckBox = QCheckBox('Check all')
        axisAllCheckBox.setChecked(True)
        axisAllCheckBox.stateChanged.connect(self.__axisCheckBoxListWidget.toggleState)

        lay = QHBoxLayout()
        lay.addWidget(QLabel('AxisX'))
        lay.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.MinimumExpanding))
        lay.addWidget(axisAllCheckBox)
        lay.setContentsMargins(0, 0, 0, 0)

        leftBottomMenuWidget = QWidget()
        leftBottomMenuWidget.setLayout(lay)

        lay = QVBoxLayout()
        lay.addWidget(leftBottomMenuWidget)
        lay.addWidget(self.__axisCheckBoxListWidget)

        leftBottomWidget = QWidget()
        leftBottomWidget.setLayout(lay)

        leftWidget = QSplitter()
        leftWidget.setOrientation(Qt.Vertical)
        leftWidget.addWidget(leftTopWidget)
        leftWidget.addWidget(leftBottomWidget)
        leftWidget.setChildrenCollapsible(False)
        leftWidget.setHandleWidth(1)
        leftWidget.setStyleSheet(
            "QSplitterHandle {background-color: lightgray;}")

        self.__textBrowser = QTextBrowser()
        self.__textBrowser.setPlaceholderText('Place the mouse cursor over one of the bars to see the bar info here')

        chartView = QChartView(self.__chart)
        chartView.setRenderHint(QPainter.Antialiasing)

        rightWidget = QSplitter()
        rightWidget.addWidget(chartView)
        rightWidget.addWidget(self.__textBrowser)
        rightWidget.setOrientation(Qt.Vertical)
        rightWidget.setHandleWidth(1)
        rightWidget.setStyleSheet(
            "QSplitterHandle {background-color: lightgray;}")
        rightWidget.setSizes([700, 300])

        mainWidget = QSplitter()
        mainWidget.addWidget(leftWidget)
        mainWidget.addWidget(rightWidget)
        mainWidget.setHandleWidth(1)
        mainWidget.setStyleSheet(
            "QSplitterHandle {background-color: lightgray;}")
        mainWidget.setSizes([300, 700])

        lay = QVBoxLayout()
        lay.addWidget(mainWidget)
        lay.setContentsMargins(0, 0, 0, 0)
        self.setLayout(lay)

    def mapDbModel(self, model: SqlTableModel):
        # set model and connect all events
        self.__model = model
        self.__model.added.connect(self.__addChartXCategory)
        self.__model.updated.connect(self.__updateChartXCategory)
        self.__model.deleted.connect(self.__removeChartXCategory)

        # set mapper and series(bars on the chart)
        self.__series = QBarSeries()
        self.__mapper = QVBarModelMapper(self)
        self.__mapper.setFirstBarSetColumn(4)
        self.__mapper.setLastBarSetColumn(6)
        self.__mapper.setFirstRow(0)
        self.__mapper.setRowCount(self.__model.rowCount())
        self.__mapper.setSeries(self.__series)
        self.__mapper.setModel(self.__model)
        self.__chart.addSeries(self.__series)

        # get name attributes
        getNameQuery = QSqlQuery()
        getNameQuery.prepare(f'SELECT id, name FROM {self.__model.tableName()} order by ID')
        getNameQuery.exec()

        barsetLabelLst = [barset.label() for barset in self.__series.barSets()]

        # set name attributes to list widget
        self.__barsetCheckBoxListWidget.addItems(barsetLabelLst)

        # check all items
        for i in range(self.__barsetCheckBoxListWidget.count()):
            self.__barsetCheckBoxListWidget.item(i).setCheckState(Qt.Checked)

        # get name attributes
        nameLst = []
        while getNameQuery.next():
            name = getNameQuery.value('name')
            id = getNameQuery.value('id')
            self.__idNameDict[id] = name
            nameLst.append(name)

        # set name attributes to list widget
        self.__axisCheckBoxListWidget.addItems(nameLst)

        # check all items
        for i in range(self.__axisCheckBoxListWidget.count()):
            self.__axisCheckBoxListWidget.item(i).setCheckState(Qt.Checked)

        # define axis X, set name attributes to it
        self.__axisX = QBarCategoryAxis()
        self.__axisX.append(nameLst)
        self.__chart.addAxis(self.__axisX, Qt.AlignBottom)
        self.__series.attachAxis(self.__axisX)

        # define axis Y
        axisY = QValueAxis()
        axisY.setTitleText('Score')
        self.__chart.addAxis(axisY, Qt.AlignLeft)
        self.__series.attachAxis(axisY)

        # set hover event to series
        self.__series.hovered.connect(self.__seriesHovered)

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

    def __seriesHovered(self, status, idx, barset):
        hoveredSeriesInfo = f'''
        On the bar: {status}
        Index of barset: {idx}
        Barset object: {barset}
        Barset object label: {barset.label()}
        Barset object category: {self.__axisX.categories()[idx]}
        Barset object value: {barset.at(idx)}
        '''
        self.__textBrowser.setText(hoveredSeriesInfo)

    def __showSeries(self, idx, checked):
        itemText = self.__axisCheckBoxListWidget.item(idx).text()
        barsets = [barset for barset in self.__series.barSets()]
        for barset in barsets:
            if barset.label() == itemText:
                if checked == Qt.Checked:
                    self.__series.insert(idx, barset)
                else:
                    self.__series.remove(barset)

    def __showAxisItem(self, idx, checked):
        print(idx, checked)
