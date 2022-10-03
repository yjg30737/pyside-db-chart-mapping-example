from PySide6.QtWidgets import QDialog, QGroupBox, QPushButton, QHBoxLayout, QWidget, QVBoxLayout, QCheckBox


class DelColDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        lay = QVBoxLayout()
        lay.addWidget(QCheckBox('Score 1'))
        lay.addWidget(QCheckBox('Score 2'))
        lay.addWidget(QCheckBox('Score 3'))

        groupBox = QGroupBox()
        groupBox.setLayout(lay)

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
        lay.addWidget(groupBox)
        lay.addWidget(bottomWidget)

        self.setLayout(lay)

        self.setFixedSize(self.sizeHint().width(), self.sizeHint().height())