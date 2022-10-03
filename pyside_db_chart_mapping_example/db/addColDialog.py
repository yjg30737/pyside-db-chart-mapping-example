import re

from PySide6.QtWidgets import QDialog, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QFormLayout, \
    QLineEdit


class AddColDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        self.setWindowTitle('Add Column')

        self.__colNameLineEdit = QLineEdit()
        self.__colNameLineEdit.textChanged.connect(self.__checkAccept)

        lay = QFormLayout()
        lay.addRow('Name', self.__colNameLineEdit)

        topWidget = QWidget()
        topWidget.setLayout(lay)

        self.__okBtn = QPushButton('OK')
        self.__okBtn.clicked.connect(self.accept)
        self.__okBtn.setEnabled(False)

        closeBtn = QPushButton('Close')
        closeBtn.clicked.connect(self.close)

        lay = QHBoxLayout()
        lay.addWidget(self.__okBtn)
        lay.addWidget(closeBtn)
        lay.setContentsMargins(0, 0, 0, 0)

        bottomWidget = QWidget()
        bottomWidget.setLayout(lay)

        lay = QVBoxLayout()
        lay.addWidget(topWidget)
        lay.addWidget(bottomWidget)

        self.setLayout(lay)

        self.setFixedSize(self.sizeHint().width(), self.sizeHint().height())

    def __checkAccept(self, text):
        p = bool(re.match('^[a-zA-Z0-9]+(\s*[a-zA-Z0-9])+', text))
        self.__okBtn.setEnabled(p)

    def getColumnName(self):
        return self.__colNameLineEdit.text()