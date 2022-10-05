import sqlite3

from PySide6.QtWidgets import QDialog, QGroupBox, QPushButton, QHBoxLayout, QWidget, QVBoxLayout, QCheckBox


class DelColDialog(QDialog):
    def __init__(self, table_name):
        super().__init__()
        self.__initVal()
        self.__initUi(table_name)

    def __initVal(self):
        self.__chkBoxes = []

    def __initUi(self, table_name):
        lay = QVBoxLayout()

        conn = sqlite3.connect('contacts.sqlite')
        cur = conn.cursor()

        mysel = cur.execute(f"select * from {table_name}")
        columnNames = list(map(lambda x: x[0], mysel.description))

        columnNames.remove('ID')
        columnNames.remove('Name')
        columnNames.remove('Job')
        columnNames.remove('Email')

        for columnName in columnNames:
            chkBox = QCheckBox(columnName)
            self.__chkBoxes.append(chkBox)
            lay.addWidget(chkBox)

        groupBox = QGroupBox()
        groupBox.setLayout(lay)

        self.__okBtn = QPushButton('OK')
        self.__okBtn.clicked.connect(self.accept)

        closeBtn = QPushButton('Close')
        closeBtn.clicked.connect(self.close)

        lay = QHBoxLayout()
        lay.addWidget(self.__okBtn)
        lay.addWidget(closeBtn)
        lay.setContentsMargins(0, 0, 0, 0)

        bottomWidget = QWidget()
        bottomWidget.setLayout(lay)

        lay = QVBoxLayout()
        lay.addWidget(groupBox)
        lay.addWidget(bottomWidget)

        self.setLayout(lay)

        self.setFixedSize(self.sizeHint().width(), self.sizeHint().height())

    def getColumnNames(self):
        return [checkbox.text() for checkbox in self.__chkBoxes if checkbox.isChecked()]
