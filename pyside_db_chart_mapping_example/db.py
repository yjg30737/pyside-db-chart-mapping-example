import os

from PySide6.QtSql import QSqlTableModel, QSqlQuery, QSqlDatabase
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import QTableView, QHeaderView, QWidget, QHBoxLayout, QApplication, QLabel, QAbstractItemView, \
    QGridLayout, QLineEdit, QMessageBox
from PySide6.QtCore import Qt, Signal


class InstantSearchBar(QWidget):
    searched = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        # search bar label
        self.__label = QLabel()

        self._initUi()

    def _initUi(self):
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


class DatabaseWidget(QWidget):
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
        self.__model = QSqlTableModel(self)
        self.__model.setTable(tableName)
        self.__model.setEditStrategy(QSqlTableModel.OnFieldChange)
        for i in range(len(columnNames)):
            self.__model.setHeaderData(i, Qt.Horizontal, columnNames[i])
        self.__model.select()

        # set up the view
        self.__tableView = QTableView()
        self.__tableView.setModel(self.__model)

        # set selection/resize policy
        self.__tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.__tableView.resizeColumnsToContents()
        self.__tableView.setSelectionMode(QAbstractItemView.SingleSelection)

        # sort (ascending order by default)
        self.__tableView.setSortingEnabled(True)
        self.__tableView.sortByColumn(0, Qt.AscendingOrder)

        # set current index as first record
        self.__tableView.setCurrentIndex(self.__tableView.model().index(0, 0))

        lay = QGridLayout()
        lay.addWidget(self.__tableView)
        self.setLayout(lay)

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