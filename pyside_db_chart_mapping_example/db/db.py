import os
import sqlite3, xlsxwriter

import PySide6
import pandas as pd
from typing import Union
import subprocess

from PySide6.QtGui import QIntValidator
from PySide6.QtSql import QSqlTableModel, QSqlQuery, QSqlDatabase
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import QTableView, QWidget, QHBoxLayout, QApplication, QLabel, QAbstractItemView, \
    QGridLayout, QLineEdit, QMessageBox, QStyledItemDelegate, QPushButton, QComboBox, QSpacerItem, QSizePolicy, \
    QVBoxLayout, QDialog, QFileDialog, QSpinBox
from PySide6.QtCore import Qt, Signal, QSortFilterProxyModel, QModelIndex, QPersistentModelIndex

from pyside_db_chart_mapping_example.db.addColDialog import AddColDialog
from pyside_db_chart_mapping_example.db.delColDialog import DelColDialog


class InstantSearchBar(QWidget):
    searched = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initUi()

    def __initUi(self):
        # search bar label
        self.__label = QLabel()

        self.__searchLineEdit = QLineEdit()
        self.__searchIcon = QSvgWidget()
        ps = QApplication.font().pointSize()
        self.__searchIcon.setFixedSize(ps, ps)

        self.__searchBar = QWidget()
        self.__searchBar.setObjectName('searchBar')

        lay = QHBoxLayout()
        lay.addWidget(self.__searchIcon)
        lay.addWidget(self.__searchLineEdit)
        self.__searchBar.setLayout(lay)
        lay.setContentsMargins(ps // 2, 0, 0, 0)
        lay.setSpacing(0)

        self.__searchLineEdit.setFocus()
        self.__searchLineEdit.textChanged.connect(self.__searched)

        self.setAutoFillBackground(True)

        lay = QHBoxLayout()
        lay.addWidget(self.__searchBar)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(2)

        self._topWidget = QWidget()
        self._topWidget.setLayout(lay)

        lay = QGridLayout()
        lay.addWidget(self._topWidget)

        searchWidget = QWidget()
        searchWidget.setLayout(lay)
        lay.setContentsMargins(0, 0, 0, 0)

        lay = QGridLayout()
        lay.addWidget(searchWidget)
        lay.setContentsMargins(0, 0, 0, 0)

        self.__setStyle()

        self.setLayout(lay)

    # ex) searchBar.setLabel(True, 'Search Text')
    def setLabel(self, visibility: bool = True, text=None):
        if text:
            self.__label.setText(text)
        self.__label.setVisible(visibility)

    def __setStyle(self):
        self.__searchIcon.load(os.path.join(os.path.dirname(__file__), '../ico/search.svg'))
        # set style sheet
        with open(os.path.join(os.path.dirname(__file__), '../style/lineedit.css'), 'r') as f:
            self.__searchLineEdit.setStyleSheet(f.read())
        with open(os.path.join(os.path.dirname(__file__), '../style/search_bar.css'), 'r') as f:
            self.__searchBar.setStyleSheet(f.read())
        with open(os.path.join(os.path.dirname(__file__), '../style/widget.css'), 'r') as f:
            self.setStyleSheet(f.read())

    def __searched(self, text):
        self.searched.emit(text)

    def setSearchIcon(self, icon_filename: str):
        self.__searchIcon.load(icon_filename)

    def setPlaceHolder(self, text: str):
        self.__searchLineEdit.setPlaceholderText(text)

    def getSearchBar(self):
        return self.__searchLineEdit

    def getSearchLabel(self):
        return self.__searchIcon

    def showEvent(self, e):
        self.__searchLineEdit.setFocus()


# for search feature
class FilterProxyModel(QSortFilterProxyModel):
    def __init__(self):
        super().__init__()
        self.__searchedText = ''

    @property
    def searchedText(self):
        return self.__searchedText

    @searchedText.setter
    def searchedText(self, value):
        self.__searchedText = value
        self.invalidateFilter()


# for align text in every cell to center
class AlignDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        self.installEventFilter(self)
        option.displayAlignment = Qt.AlignCenter

    def createEditor(self, parent, option, index):
        editor = super().createEditor(parent, option, index)
        c = index.column()
        if c in range(4, 6):
            validator = QIntValidator()
            editor.setValidator(validator)
        return editor

class SqlTableModel(QSqlTableModel):
    added = Signal(int, str)
    updated = Signal(int, str)
    deleted = Signal(list)
    addedCol = Signal()
    deletedCol = Signal()

    def __init__(self, *args, **kwargs):
        super().__init__()
        
    def flags(self, index: Union[QModelIndex, QPersistentModelIndex]) -> Qt.ItemFlags:
        if index.column() == 0:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        return super().flags(index)


class DatabaseWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        # table name
        self.__tableName = "contacts"

        # label
        lbl = QLabel(self.__tableName.capitalize())

        columnNames = ['ID', 'Name', 'Job', 'Email', 'Score 1', 'Score 2', 'Score 3']

        # database table
        # set up the model
        self.__model = SqlTableModel(self)
        self.__model.setTable(self.__tableName)
        self.__model.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.__model.beforeUpdate.connect(self.__updated)
        for i in range(len(columnNames)):
            self.__model.setHeaderData(i, Qt.Horizontal, columnNames[i])
        self.__model.select()

        # init the proxy model
        self.__proxyModel = FilterProxyModel()

        # set the table model as source model to make it enable to feature sort and filter function
        self.__proxyModel.setSourceModel(self.__model)

        # set up the view
        self.__tableView = QTableView()
        self.__tableView.setModel(self.__proxyModel)

        # align to center
        delegate = AlignDelegate()
        for i in range(self.__model.columnCount()):
            self.__tableView.setItemDelegateForColumn(i, delegate)

        # set selection/resize policy
        self.__tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.__tableView.resizeColumnsToContents()
        self.__tableView.setSelectionMode(QAbstractItemView.ExtendedSelection)

        # sort (ascending order by default)
        self.__tableView.setSortingEnabled(True)
        self.__tableView.sortByColumn(0, Qt.AscendingOrder)

        # set current index as first record
        self.__tableView.setCurrentIndex(self.__tableView.model().index(0, 0))

        # add/delete record buttons
        addBtn = QPushButton('Add Record')
        addBtn.clicked.connect(self.__add)
        self.__delBtn = QPushButton('Delete Record')
        self.__delBtn.clicked.connect(self.__delete)

        # column add/delete buttons
        addColBtn = QPushButton('Add Column')
        addColBtn.clicked.connect(self.__addCol)
        self.__delColBtn = QPushButton('Delete Column')
        self.__delColBtn.clicked.connect(self.__deleteCol)

        self.__importBtn = QPushButton('Import As Excel')
        self.__importBtn.clicked.connect(self.__import)

        self.__exportBtn = QPushButton('Export As Excel')
        self.__exportBtn.clicked.connect(self.__export)

        # instant search bar
        self.__searchBar = InstantSearchBar()
        self.__searchBar.setPlaceHolder('Search...')
        self.__searchBar.searched.connect(self.__showResult)

        # combo box to make it enable to search by each column
        self.__comboBox = QComboBox()
        items = ['All'] + columnNames
        for i in range(len(items)):
            self.__comboBox.addItem(items[i])
        self.__comboBox.currentIndexChanged.connect(self.__currentIndexChanged)

        # set layout
        lay = QHBoxLayout()
        lay.addWidget(lbl)
        lay.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.MinimumExpanding))
        lay.addWidget(self.__searchBar)
        lay.addWidget(self.__comboBox)
        lay.addWidget(addBtn)
        lay.addWidget(self.__delBtn)
        lay.addWidget(addColBtn)
        lay.addWidget(self.__delColBtn)
        lay.addWidget(self.__importBtn)
        lay.addWidget(self.__exportBtn)
        lay.setContentsMargins(0, 0, 0, 0)
        btnWidget = QWidget()
        btnWidget.setLayout(lay)

        lay = QVBoxLayout()
        lay.addWidget(btnWidget)
        lay.addWidget(self.__tableView)

        self.setLayout(lay)

        # show default result (which means "show all")
        self.__showResult('')

        # init delete button enabled
        self.__delBtnToggle()

    def __delBtnToggle(self):
        self.__delBtn.setEnabled(len(self.__tableView.selectedIndexes()) > 0)

    def __add(self):
        # add new record
        r = self.__model.record()
        r.setValue("name", '')
        r.setValue("job", '')
        r.setValue("email", '')
        self.__model.insertRecord(-1, r)
        self.__model.select()

        # set new record as current index
        newRecordIdx = self.__tableView.model().index(self.__tableView.model().rowCount() - 1, 0)
        self.__tableView.setCurrentIndex(newRecordIdx)

        # send add signal
        id = newRecordIdx.data()
        self.__model.added.emit(id, r.value('name'))

        # make the record editable right after being added
        self.__tableView.edit(self.__tableView.currentIndex().siblingAtColumn(1))
        self.__delBtnToggle()

        # align to center
        delegate = AlignDelegate()
        for i in range(self.__model.columnCount()):
            self.__tableView.setItemDelegateForColumn(i, delegate)

    def __updated(self, i, r):
        # send updated signal
        self.__model.updated.emit(r.value('id'), r.value('name'))

    def __delete(self):
        # delete select rows(records)
        rows = [idx.row() for idx in self.__tableView.selectedIndexes()]
        names = []
        for r_idx in rows:
            name = self.__model.data(self.__model.index(r_idx, 1))
            if name:
                names.append(name)
            self.__model.removeRow(r_idx)
        self.__model.select()

        # set previous row of first removed one as current index
        self.__tableView.setCurrentIndex(self.__tableView.model().index(max(0, rows[0] - 1), 0))

        # send deleted signal
        self.__model.deleted.emit(names)
        self.__delBtnToggle()

    def __import(self):
        filename = QFileDialog.getOpenFileName(self, 'Select the file', '', 'Excel File (*.xlsx)')
        filename = filename[0]
        if filename:
            try:
                con = sqlite3.connect('contacts.sqlite')
                wb = pd.read_excel(filename, sheet_name=None)
                for sheet in wb:
                    wb[sheet].to_sql(sheet, con, index=False)
                con.commit()
                con.close()
                self.__model.setTable('Sheet1')
                self.__model.select()
            except Exception as e:
                print(e)

    def __addCol(self):
        dialog = AddColDialog()
        reply = dialog.exec()
        if reply == QDialog.Accepted:
            q = QSqlQuery()
            q.prepare(f'ALTER TABLE {self.__tableName} ADD COLUMN "{dialog.getColumnName()}" INTEGER')
            q.exec()
            self.__model.setTable(self.__tableName)
            self.__model.select()
            self.__tableView.resizeColumnsToContents()
            self.__model.addedCol.emit()

            # align to center
            delegate = AlignDelegate()
            for i in range(self.__model.columnCount()):
                self.__tableView.setItemDelegateForColumn(i, delegate)

    def __deleteCol(self):
        dialog = DelColDialog()
        reply = dialog.exec()
        if reply == QDialog.Accepted:
            q = QSqlQuery()
            q.prepare(f'ALTER TABLE {self.__tableName} DROP COLUMN "{dialog.getColumnName()}"')
            q.exec()
            self.__model.setTable(self.__tableName)
            self.__model.select()
            self.__tableView.resizeColumnsToContents()
            self.__model.deletedCol.emit()

    def __export(self):
        filename = QFileDialog.getOpenFileName(self, 'Export', '.', 'Excel File (*.xlsx)')
        filename = filename[0]
        if filename:
            workbook = xlsxwriter.Workbook(filename)
            worksheet = workbook.add_worksheet()
            conn = sqlite3.connect('contacts.sqlite')
            cur = conn.cursor()

            mysel = cur.execute(f"select * from {self.__tableName}")
            columnNames = list(map(lambda x: x[0], mysel.description))

            for c_idx in range(len(columnNames)):
                worksheet.write(0, c_idx, columnNames[c_idx])

            for i, row in enumerate(mysel):
                for j, value in enumerate(row):
                    worksheet.write(i+1, j, row[j])
            workbook.close()

            path = filename.replace('/', '\\')
            subprocess.Popen(r'explorer /select,"' + path + '"')

    def __showResult(self, text):
        # index -1 will be read from all columns
        # otherwise it will be read the current column number indicated by combobox
        self.__proxyModel.setFilterKeyColumn(self.__comboBox.currentIndex() - 1)
        # regular expression can be used
        self.__proxyModel.setFilterRegularExpression(text)

    def __currentIndexChanged(self, idx):
        self.__showResult(self.__searchBar.getSearchBar().text())

    def getModel(self):
        return self.__model

    def getView(self):
        return self.__tableView


def createConnection():
    con = QSqlDatabase.addDatabase("QSQLITE")
    con.setDatabaseName("contacts.sqlite")
    if not con.open():
        QMessageBox.critical(
            None,
            "QTableView Example - Error!",
            "Database Error: %s" % con.lastError().databaseText(),
        )
        return False
    return True


def initTable():
    table = 'contacts'

    dropTableQuery = QSqlQuery()
    dropTableQuery.prepare(
        f'DROP TABLE {table}'
    )
    dropTableQuery.exec()

    createTableQuery = QSqlQuery()
    createTableQuery.prepare(
        f"""
        CREATE TABLE {table} (
            ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
            Name VARCHAR(40) UNIQUE NOT NULL,
            Job VARCHAR(50),
            Email VARCHAR(40) NOT NULL,
            "Score 1" INTEGER,
            "Score 2" INTEGER,
            "Score 3" INTEGER
        )
        """
    )
    createTableQuery.exec()


def addSample():
    table = 'contacts'

    insertDataQuery = QSqlQuery()
    insertDataQuery.prepare(
        f"""
        INSERT INTO {table} (
            Name,
            Job,
            Email,
            "Score 1",
            "Score 2",
            "Score 3"
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """
    )

    # Sample data
    data = [
        ("Joe", "Senior Web Developer", "joe@example.com", "251", "112", "315"),
        ("Lara", "Project Manager", "lara@example.com", "325", "231", "427"),
        ("David", "Data Analyst", "david@example.com", "341", "733", "502"),
        ("Jane", "Senior Python Developer", "jane@example.com", "310", "243", "343"),
    ]

    # Use .addBindValue() to insert data
    for name, job, email, score1, score2, score3 in data:
        insertDataQuery.addBindValue(name)
        insertDataQuery.addBindValue(job)
        insertDataQuery.addBindValue(email)
        insertDataQuery.addBindValue(score1)
        insertDataQuery.addBindValue(score2)
        insertDataQuery.addBindValue(score3)
        insertDataQuery.exec()