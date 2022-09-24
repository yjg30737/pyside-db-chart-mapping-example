import sys

from PySide6.QtWidgets import QMainWindow, QSplitter, QListWidgetItem, QListWidget, QCheckBox

from pyside_db_chart_mapping_example.chart import ChartWidget
from pyside_db_chart_mapping_example.db import *


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


class CheckWidget(QWidget):
    itemChecked = Signal(int, Qt.CheckState)

    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        self.__checkBoxListWidget = CheckBoxListWidget()
        self.__checkBoxListWidget.checkedSignal.connect(self.itemChecked)

        self.__allCheckBox = QCheckBox('Check all')
        self.__allCheckBox.stateChanged.connect(self.__checkBoxListWidget.toggleState)
        self.__allCheckBox.setChecked(True)

        lay = QHBoxLayout()
        lay.addWidget(QLabel('BarSet'))
        lay.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.MinimumExpanding))
        lay.addWidget(self.__allCheckBox)
        lay.setContentsMargins(0, 0, 0, 0)

        leftTopMenuWidget = QWidget()
        leftTopMenuWidget.setLayout(lay)

        lay = QVBoxLayout()
        lay.addWidget(leftTopMenuWidget)
        lay.addWidget(self.__checkBoxListWidget)

        self.setLayout(lay)

    def addItems(self, items: list):
        for itemText in items:
            item = QListWidgetItem(itemText)
            item.setCheckState(self.__allCheckBox.checkState())
            self.__checkBoxListWidget.addItem(item)

    def getItem(self, idx):
        return self.__checkBoxListWidget.item(idx)


class BarsetItemCheckWidget(CheckWidget):
    def __init__(self):
        super().__init__()


class AxisItemCheckWidget(CheckWidget):
    def __init__(self):
        super().__init__()


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        if not createConnection():
            sys.exit(1)
        initTable()
        addSample()

        self.__barsetCheckListWidget = BarsetItemCheckWidget()
        self.__barsetCheckListWidget.itemChecked.connect(self.__showSeriesItem)

        self.__axisCheckListWidget = AxisItemCheckWidget()
        self.__axisCheckListWidget.itemChecked.connect(self.__showAxisItem)

        leftWidget = QSplitter()
        leftWidget.setOrientation(Qt.Vertical)
        leftWidget.addWidget(self.__barsetCheckListWidget)
        leftWidget.addWidget(self.__axisCheckListWidget)
        leftWidget.setChildrenCollapsible(False)
        leftWidget.setHandleWidth(1)
        leftWidget.setStyleSheet(
            "QSplitterHandle {background-color: lightgray;}")

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

    # fixme
    #  Internal C++ object (PySide6.QtCharts.QBarSet) already deleted.
    #  Update the mapper to solve this problem
    def __showSeriesItem(self, idx, checked):
        # itemText = self.__barsetCheckListWidget.getItem(idx).text()
        # for i in range(self.__model.rowCount()):
        #     if barset.label() == itemText:
        #         if checked == Qt.Checked:
        #             pass
        #             # self.__series.insert(idx, barset)
        #         else:
        #             self.__series.remove(barset)
        #             break
        pass

    def __showAxisItem(self, idx, checked):
        # itemText = self.__axisCheckBoxListWidget.getItem(idx).text()
        # self.__axisX.categories()
        # barsets = [ for barset in self.__chart.axisX(self.__series)]
        # for barset in barsets:
        #     if barset.label() == itemText:
        #         if checked == Qt.Checked:
        #             self.__series.insert(idx, barset)
        #         else:
        #             self.__series.remove(barset)
        #             break
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Window()
    ex.show()
    app.exec()

