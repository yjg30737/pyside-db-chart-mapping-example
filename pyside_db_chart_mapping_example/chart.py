import typing

from PySide6.QtCharts import QChart, QChartView, QBarSeries, QVBarModelMapper, \
    QBarCategoryAxis, QValueAxis, QBarSet
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QPixmap, QColor
from PySide6.QtSql import QSqlQuery
from PySide6.QtWidgets import QVBoxLayout, QWidget, QTextBrowser, QSplitter, QPushButton, QFileDialog, QHBoxLayout, \
    QLabel, QGroupBox, QFormLayout, QSpacerItem, QSizePolicy, QDialog

from pyside_db_chart_mapping_example.db import SqlTableModel


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


class SettingsDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        hoverColorBtn = ColorButton()
        selectColorBtn = ColorButton()

        lay = QFormLayout()
        lay.addRow('Bar border\'s color when cursor is hovering on it', hoverColorBtn)
        lay.addRow('Selected bar\'s color', selectColorBtn)

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


class ChartWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__idNameDict = {}
        self.__model = SqlTableModel()
        self.__curBarSetIdx = 0

    def __initUi(self):
        self.__chart = QChart()
        self.__chart.setAnimationOptions(QChart.AllAnimations)

        self.__textBrowser = QTextBrowser()
        self.__textBrowser.setPlaceholderText('Place the mouse cursor over one of the bars to see the bar info here')

        self.__chartView = QChartView(self.__chart)
        self.__chartView.setRenderHint(QPainter.Antialiasing)

        mainWidget = QSplitter()
        mainWidget.addWidget(self.__chartView)
        mainWidget.addWidget(self.__textBrowser)
        mainWidget.setOrientation(Qt.Vertical)
        mainWidget.setHandleWidth(1)
        mainWidget.setStyleSheet(
            "QSplitterHandle {background-color: lightgray;}")
        mainWidget.setSizes([700, 300])

        saveBtn = QPushButton('Save Chart As Image')
        saveBtn.clicked.connect(self.__save)

        lay = QHBoxLayout()

        settingsBtn = QPushButton('Settings')
        settingsBtn.clicked.connect(self.__settings)

        lay.addWidget(settingsBtn)
        lay.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.MinimumExpanding))
        lay.addWidget(saveBtn)
        lay.setContentsMargins(5, 5, 5, 0)

        topWidget = QWidget()
        topWidget.setLayout(lay)

        lay = QVBoxLayout()
        lay.addWidget(topWidget)
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
        self.__series.barsetsAdded.connect(self.__setBarsetPressSignal)

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
        # self.__barsetCheckListWidget.addItems(barsetLabelLst)

        # get name attributes
        nameLst = []
        while getNameQuery.next():
            name = getNameQuery.value('name')
            id = getNameQuery.value('id')
            self.__idNameDict[id] = name
            nameLst.append(name)

        # set name attributes to list widget
        # self.__axisCheckBoxListWidget.addItems(nameLst)

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
        self.__series.pressed.connect(self.__seriesPressed)

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

    def __seriesHovered(self, status, idx, barset: QBarSet):
        if status:
            pen = barset.pen()
            pen.setColor(QColor(255, 0, 0))
            barset.setPen(pen)
        else:
            pen = barset.pen()
            pen.setColor(QColor.fromHsvF(0.555833, 0.000000, 1.000000, 1.000000))
            barset.setPen(pen)

    def __showSelectedBarInfo(self, idx, barset):
        barset.setBarSelected(idx, True)
        category = self.__axisX.categories()[idx]
        query = QSqlQuery()
        query.prepare(f"SELECT * FROM contacts WHERE name = \'{category}\'")
        query.exec()
        job = email = ''
        while query.next():
            job = query.value('job')
            email = query.value('email')

        hoveredSeriesInfo = f'''
        Index of barset: {idx}
        Barset object: {barset}
        Barset object label: {barset.label()}
        Barset object category: {category}
        Barset object job: {job}
        Barset object email: {email}
        Barset object value: {barset.at(idx)}
                                '''
        self.__textBrowser.setText(hoveredSeriesInfo)

    def __seriesPressed(self, idx, barset):
        if barset.isBarSelected(idx):
            barset.setBarSelected(idx, False)
            self.__textBrowser.clear()
        else:
            for b in self.__series.barSets():
                b.deselectAllBars()
                self.__textBrowser.clear()
            self.__showSelectedBarInfo(idx, barset)

    def __setBarsetPressSignal(self, barsets: typing.Iterable[QBarSet]):
        selectedBarColor = QColor(60, 155, 100)
        for barset in barsets:
            barset.setSelectedColor(selectedBarColor)

    def __settings(self):
        dialog = SettingsDialog()
        reply = dialog.exec()
        if reply == QDialog.Accepted:
            pass
            # color = dialog.getFrameColor()
            # savePath = dialog.getSavePath()
            # self.__settingsStruct.setValue('frameColor', color.name())
            # self.__settingsStruct.setValue('savePath', savePath)
            # self.setFrameColor(color)

    def __save(self):
        filename = QFileDialog.getSaveFileName(self, 'Save', '.', 'PNG (*.png);; JPEG (*.jpg;*.jpeg)')
        ext = filename[1].split('(')[0].strip()
        filename = filename[0]
        if filename:
            pixmap = QPixmap(self.__chartView.size())
            p = QPainter()
            p.begin(pixmap)
            self.__chartView.render(p)
            p.setRenderHint(QPainter.Antialiasing)
            p.end()
            pixmap.save(filename, ext)

    def getBarsetsTextList(self):
        return [barset.label() for barset in self.__series.barSets()]

    def getCategories(self):
        return self.__axisX.categories()