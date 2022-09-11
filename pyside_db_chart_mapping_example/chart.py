from PySide6.QtCharts import QLineSeries, QVXYModelMapper, QChart, QChartView, QBarSeries, QVBarModelMapper, \
    QBarCategoryAxis, QValueAxis, QDateTimeAxis
from PySide6.QtGui import QPainter
from PySide6.QtSql import QSqlTableModel, QSqlQuery, QSqlDatabase
from PySide6.QtWidgets import QTableView, QHeaderView, QWidget, QHBoxLayout, QApplication, QLabel, QAbstractItemView, \
    QMessageBox
from PySide6.QtCore import Qt, QTime, QDateTime


class Window(QWidget):
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
        model = QSqlTableModel(self)
        model.setTable(tableName)
        model.setEditStrategy(QSqlTableModel.OnFieldChange)
        for i in range(len(columnNames)):
            model.setHeaderData(i, Qt.Horizontal, columnNames[i])
        model.select()

        # set up the view
        tableView = QTableView()
        tableView.setModel(model)
        tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tableView.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # set selection/resize policy
        tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        tableView.resizeColumnsToContents()
        tableView.setSelectionMode(QAbstractItemView.SingleSelection)

        # sort (ascending order by default)
        tableView.setSortingEnabled(True)
        tableView.sortByColumn(0, Qt.AscendingOrder)

        # set current index as first record
        tableView.setCurrentIndex(tableView.model().index(0, 0))

        chart = QChart()
        chart.setAnimationOptions(QChart.AllAnimations)

        series = QBarSeries()
        mapper = QVBarModelMapper(self)
        mapper.setFirstBarSetColumn(4)
        mapper.setLastBarSetColumn(6)
        mapper.setFirstRow(0)
        mapper.setRowCount(model.rowCount())
        mapper.setSeries(series)
        mapper.setModel(model)
        chart.addSeries(series)

        axisX = QBarCategoryAxis()
        axisX.append(['Joe', 'Lara', 'David', 'Jane'])
        chart.addAxis(axisX, Qt.AlignBottom)
        series.attachAxis(axisX)
        axisY = QValueAxis()
        axisY.setTitleText('Score')
        chart.addAxis(axisY, Qt.AlignLeft)
        series.attachAxis(axisY)

        chartView = QChartView(chart)
        chartView.setRenderHint(QPainter.Antialiasing)

        lay = QHBoxLayout()
        lay.addWidget(tableView)
        lay.addWidget(chartView)
        self.setLayout(lay)

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


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    if not createConnection():
        sys.exit(1)
    initTable()
    addSample()
    ex = Window()
    ex.show()
    app.exec()

