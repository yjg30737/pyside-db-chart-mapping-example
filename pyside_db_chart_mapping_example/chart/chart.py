import subprocess
import typing

from PySide6.QtCharts import QChart, QChartView, QBarSeries, QVBarModelMapper, \
    QBarCategoryAxis, QValueAxis, QBarSet
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QPainter, QPixmap, QColor, QPdfWriter
from PySide6.QtSql import QSqlQuery
from PySide6.QtWidgets import QVBoxLayout, QWidget, QTextBrowser, QSplitter, QPushButton, QFileDialog, QHBoxLayout, \
    QSpacerItem, QSizePolicy, QDialog

from pyside_db_chart_mapping_example.chart.settings.settingsDialog import SettingsDialog
from pyside_db_chart_mapping_example.db.db import SqlTableModel


class ChartWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__idNameDict = {}
        self.__model = SqlTableModel()
        self.__initSettings()

    def __initSettings(self):
        self.__settingsStruct = QSettings('chart_settings.ini', QSettings.IniFormat)
        self.__animation = int(self.__settingsStruct.value('animation', 1))
        self.__theme = self.__settingsStruct.value('theme', 'Light')
        self.__hoverColor = self.__settingsStruct.value('hoverColor', '#ff0000')
        self.__selectColor = self.__settingsStruct.value('selectColor', '#329b64')

    def __initUi(self):
        self.__chart = QChart()
        self.__setAnimation()
        self.__setTheme()

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

        saveBtn = QPushButton('Save Chart')
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
        self.__model.addedCol.connect(self.__addColToSeries)
        self.__model.addedCol.connect(self.__removeBarSetColumn)

        # set mapper and series(bars on the chart)
        self.__series = QBarSeries()
        self.__series.barsetsAdded.connect(self.__setSelectedColor)

        self.__mapper = QVBarModelMapper(self)
        self.__mapper.setFirstBarSetColumn(4)
        self.__mapper.setLastBarSetColumn(6)
        self.__mapper.setFirstRow(0)
        self.__mapper.setRowCount(self.__model.rowCount())
        self.__mapper.setSeries(self.__series)
        self.__mapper.setModel(self.__model)
        # self.__mapper.lastBarSetColumnChanged.connect(self.__addBarSetColumn)
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
        self.__axisY = QValueAxis()
        self.__axisY.setTitleText('Score')
        self.__chart.addAxis(self.__axisY, Qt.AlignLeft)
        self.__series.attachAxis(self.__axisY)

        # set hover event to series
        self.__series.hovered.connect(self.__seriesHovered)
        self.__series.clicked.connect(self.__seriesPressed)

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

    def __addColToSeries(self):
        self.__mapper.setLastBarSetColumn(self.__mapper.lastBarSetColumn()+2)

    def __removeBarSetColumn(self):
        self.__mapper.setLastBarSetColumn(self.__mapper.lastBarSetColumn()-1)

    def __seriesHovered(self, status, idx, barset: QBarSet):
        if status:
            pen = barset.pen()
            pen.setColor(self.__hoverColor)
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

    def __setAnimation(self):
        if self.__animation:
            self.__chart.setAnimationOptions(QChart.AllAnimations)
        else:
            self.__chart.setAnimationOptions(QChart.NoAnimation)

    def __setTheme(self):
        if self.__theme == 'Light':
            self.__chart.setTheme(QChart.ChartThemeLight)
        else:
            self.__chart.setTheme(QChart.ChartThemeDark)

    def __setSelectedColor(self, barsets: typing.Iterable[QBarSet]):
        for barset in barsets:
            barset.setSelectedColor(self.__selectColor)

    def __settings(self):
        dialog = SettingsDialog()
        reply = dialog.exec()
        if reply == QDialog.Accepted:
            self.__initSettings()
            self.__setAnimation()
            self.__setTheme()
            self.__setSelectedColor(self.__series.barSets())

    def __save(self):
        filename = QFileDialog.getSaveFileName(self, 'Save', '.', 'PNG (*.png);; '
                                                                  'JPEG (*.jpg;*.jpeg);;'
                                                                  'PDF (*.pdf)')
        ext = filename[1].split('(')[0].strip()
        filename = filename[0]
        if filename:
            # pdf file
            if ext == 'PDF':
                writer = QPdfWriter(filename)
                writer.setResolution(100)
                p = QPainter()
                p.begin(writer)
                self.__chartView.render(p)
                p.setRenderHint(QPainter.SmoothPixmapTransform)
                p.end()
            # image file
            else:
                dpr = self.__chartView.devicePixelRatioF()
                # dpr, *2 is for high quality image
                pixmap = QPixmap(int(self.__chartView.width() * dpr * 2),
                                 int(self.__chartView.height() * dpr * 2))
                # make the background transparent
                pixmap.fill(Qt.transparent)
                p = QPainter(pixmap)
                p.setRenderHint(QPainter.Antialiasing)
                p.begin(pixmap)
                self.__chartView.render(p)
                p.end()
                pixmap.save(filename, ext)

            path = filename.replace('/', '\\')
            subprocess.Popen(r'explorer /select,"' + path + '"')

    def getBarsetsTextList(self):
        return [barset.label() for barset in self.__series.barSets()]

    def getCategories(self):
        return self.__axisX.categories()