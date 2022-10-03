from PySide6.QtWidgets import QDialog, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QGridLayout, QFormLayout, \
    QLineEdit


class AddColDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        self.setWindowTitle('Add Column')

        self.__colNameLineEdit = QLineEdit()

        lay = QFormLayout()
        lay.addRow('Name', self.__colNameLineEdit)

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

        self.setFixedSize(self.sizeHint().width(), self.sizeHint().height())

    def getColumnName(self):
        return self.__colNameLineEdit.text()