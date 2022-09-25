import sys

from PySide6.QtWidgets import QMainWindow, QSplitter, QListWidgetItem, QListWidget, QCheckBox

from pyside_db_chart_mapping_example.chart import ChartWidget
from pyside_db_chart_mapping_example.db import *


class CheckBoxListWidget(QListWidget):
    checkedSignal = Signal(str, Qt.CheckState)

    def __init__(self):
        super().__init__()
        self.itemChanged.connect(self.__sendCheckedSignal)

    def __sendCheckedSignal(self, item):
        text = item.text()
        state = item.checkState()
        self.checkedSignal.emit(text, state)

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
    itemChecked = Signal(str, Qt.CheckState)

    def __init__(self, label):
        super().__init__()
        self.__initUi(label)

    def __initUi(self, label):
        self.__checkBoxListWidget = CheckBoxListWidget()
        self.__checkBoxListWidget.checkedSignal.connect(self.itemChecked)

        self.__allCheckBox = QCheckBox('Check all')
        self.__allCheckBox.stateChanged.connect(self.__checkBoxListWidget.toggleState)
        self.__allCheckBox.setChecked(True)

        lay = QHBoxLayout()
        lay.addWidget(QLabel(label))
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
        super().__init__('Barset')


class CategoryCheckWidget(CheckWidget):
    def __init__(self):
        super().__init__('Categories')


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
        self.__barsetCheckListWidget.itemChecked.connect(self.__refreshSeries)

        self.__categoryCheckListWidget = CategoryCheckWidget()
        self.__categoryCheckListWidget.itemChecked.connect(self.__refreshCategory)

        leftWidget = QSplitter()
        leftWidget.setOrientation(Qt.Vertical)
        leftWidget.addWidget(self.__barsetCheckListWidget)
        leftWidget.addWidget(self.__categoryCheckListWidget)
        leftWidget.setChildrenCollapsible(False)
        leftWidget.setHandleWidth(1)
        leftWidget.setStyleSheet(
            "QSplitterHandle {background-color: lightgray;}")

        dbWidget = DatabaseWidget()
        self.__chartWidget = ChartWidget()
        self.__model = dbWidget.getModel()
        self.__chartWidget.mapDbModel(self.__model)

        self.__barsetCheckListWidget.addItems(self.__chartWidget.getBarsetsTextList())
        self.__categoryCheckListWidget.addItems(self.__chartWidget.getCategories())

        mainWidget = QSplitter()
        mainWidget.addWidget(leftWidget)
        mainWidget.addWidget(dbWidget)
        mainWidget.addWidget(self.__chartWidget)
        mainWidget.setChildrenCollapsible(False)
        mainWidget.setSizes([200, 500, 600])
        mainWidget.setHandleWidth(1)
        mainWidget.setStyleSheet(
            "QSplitterHandle {background-color: lightgray;}")

        self.setCentralWidget(mainWidget)

    def __refreshSeries(self, text, checked):
        query = QSqlQuery()
        query.prepare(f'SELECT * FROM contacts WHERE name != {text}')
        query.exec()

    def __refreshCategory(self, text, checked):
        query = QSqlQuery()
        query.prepare(f"SELECT * FROM contacts WHERE name = '{text}'")
        query.exec()
        self.__model.setQuery(query)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Window()
    ex.show()
    app.exec()

