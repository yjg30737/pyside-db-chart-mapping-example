import os

from PySide6.QtSql import QSqlTableModel, QSqlQuery, QSqlDatabase, QSqlRecord
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import QTableView, QWidget, QHBoxLayout, QApplication, QLabel, QAbstractItemView, \
    QGridLayout, QLineEdit, QMessageBox, QStyledItemDelegate, QPushButton, QComboBox, QSpacerItem, QSizePolicy, \
    QVBoxLayout, QCheckBox
from PySide6.QtCore import Qt, Signal, QSortFilterProxyModel


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
        self.__searchIcon.setFixedSize(ps * 1.5, ps * 1.5)

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
        self.__searchIcon.load(os.path.join(os.path.dirname(__file__), 'ico/search.svg'))
        # set style sheet
        with open(os.path.join(os.path.dirname(__file__), 'style/lineedit.css'), 'r') as f:
            self.__searchLineEdit.setStyleSheet(f.read())
        with open(os.path.join(os.path.dirname(__file__), 'style/search_bar.css'), 'r') as f:
            self.__searchBar.setStyleSheet(f.read())
        with open(os.path.join(os.path.dirname(__file__), 'style/widget.css'), 'r') as f:
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
        option.displayAlignment = Qt.AlignCenter


class TableModel(QSqlTableModel):

    def __init__(self, *args, **kwargs):
        QSqlTableModel.__init__(self, *args, **kwargs)
        self.__checkableData = {}

    def flags(self, index):
        fl = QSqlTableModel.flags(self, index)
        if index.column() == 0:
            fl |= Qt.ItemIsUserCheckable
        return fl

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.CheckStateRole and (
            self.flags(index) & Qt.ItemIsUserCheckable != Qt.NoItemFlags
        ):
            if index.row() not in self.__checkableData.keys():
                self.setData(index, Qt.Unchecked, Qt.CheckStateRole)
            return self.__checkableData[index.row()]
        else:
            return QSqlTableModel.data(self, index, role)

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.CheckStateRole and (
            self.flags(index) & Qt.ItemIsUserCheckable != Qt.NoItemFlags
        ):
            self.__checkableData[index.row()] = value
            self.dataChanged.emit(index, index, (role,))
            return True
        return QSqlTableModel.setData(self, index, value, role)

    def getCheckedRows(self):
        rows = []
        for i in range(0, self.rowCount()):
            idx = self.index(i, 0)
            if self.data(idx, Qt.CheckStateRole) == 2:
                rows.append(i)
        return rows
        # for i in range(self.rowCount()-1, -1, -1):
        #     idx = self.index(i, 0)
        #     if self.data(idx, Qt.CheckStateRole) == 2:
        #         self.removeRow(i)


class DatabaseWidget(QWidget):
    added = Signal(QSqlRecord)
    deleted = Signal(int)

    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        # table name
        tableName = "contacts"

        # label
        lbl = QLabel(tableName.capitalize())

        columnNames = ['ID', 'Name', 'Job', 'Email', 'Score 1', 'Score 2', 'Score 3']

        # database table
        # set up the model
        self.__model = TableModel(self)
        self.__model.setTable(tableName)
        self.__model.setEditStrategy(QSqlTableModel.OnFieldChange)
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
        self.__tableView.setSelectionMode(QAbstractItemView.SingleSelection)

        # sort (ascending order by default)
        self.__tableView.setSortingEnabled(True)
        self.__tableView.sortByColumn(0, Qt.AscendingOrder)

        # set current index as first record
        self.__tableView.setCurrentIndex(self.__tableView.model().index(0, 0))

        # add/delete buttons
        addBtn = QPushButton('Add')
        addBtn.clicked.connect(self.__add)
        self.__delBtn = QPushButton('Delete')
        self.__delBtn.clicked.connect(self.__delete)

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

        # set checkbox for check all items
        checkBox = QCheckBox()
        checkBox.setText('Check all')
        checkBox.toggled.connect(self.__allChecked)

        # set layout
        lay = QHBoxLayout()
        lay.addWidget(checkBox)
        lay.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.MinimumExpanding))
        lay.addWidget(self.__searchBar)
        lay.addWidget(self.__comboBox)
        lay.addWidget(addBtn)
        lay.addWidget(self.__delBtn)
        lay.setContentsMargins(0, 0, 0, 0)
        btnWidget = QWidget()
        btnWidget.setLayout(lay)

        lay = QVBoxLayout()
        lay.addWidget(lbl)
        lay.addWidget(btnWidget)
        lay.addWidget(self.__tableView)

        self.setLayout(lay)

        # show default result (which means "show all")
        self.__showResult('')

        # init delete button enabled
        self.__delBtnToggle()

        # delete button toggle
        self.__model.dataChanged.connect(self.__delBtnToggle)

    def __delBtnToggle(self):
        self.__delBtn.setEnabled(len(self.__model.getCheckedRows()) > 0)

    def __add(self):
        r = self.__model.record()
        r.setValue("name", '')
        r.setValue("job", '')
        r.setValue("email", '')
        self.__model.insertRecord(-1, r)
        self.__model.select()
        self.__tableView.setCurrentIndex(self.__tableView.model().index(self.__tableView.model().rowCount() - 1, 0))
        self.added.emit(r)
        self.__tableView.edit(self.__tableView.currentIndex().siblingAtColumn(1))
        self.__delBtnToggle()

    def __delete(self):
        rows = self.__model.getCheckedRows()
        for r_idx in rows:
            self.__model.removeRow(r_idx)
        self.__model.select()
        self.__delBtnToggle()
        # r = self.__tableView.currentIndex().row()
        # id = self.__model.index(r, 0).data()
        # self.__model.removeRow(r)
        # self.__model.select()
        # self.__tableView.setCurrentIndex(self.__tableView.model().index(max(0, r - 1), 0))
        # self.deleted.emit(id)
        # self.__delBtnToggle()

    def __showResult(self, text):
        # index -1 will be read from all columns
        # otherwise it will be read the current column number indicated by combobox
        self.__proxyModel.setFilterKeyColumn(self.__comboBox.currentIndex() - 1)
        # regular expression can be used
        self.__proxyModel.setFilterRegularExpression(text)

    def __currentIndexChanged(self, idx):
        self.__showResult(self.__searchBar.getSearchBar().text())

    def __allChecked(self, f):
        for i in range(self.__model.rowCount()):
            idx = self.__model.index(i, 0)
            self.__model.setData(idx, 2 if f else 0, Qt.CheckStateRole)

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
            id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
            name VARCHAR(40) NOT NULL,
            job VARCHAR(50),
            email VARCHAR(40) NOT NULL,
            score1 INTEGER,
            score2 INTEGER,
            score3 INTEGER
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
            name,
            job,
            email,
            score1,
            score2,
            score3
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