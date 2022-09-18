# pyside-db-chart-mapping-example
PySide6 example of mapping database table(QSqlTableModel based tableview) and chart with QVBarModelMapper.

All basic CRUD feature of database mapped into chart(QChartView).

## Requirements
* PySide6

## Setup
`python -m pip install git+https://github.com/yjg30737/pyside-db-chart-mapping-example.git --upgrade`

## Usage
* If you want to delete more than one record, holding ctrl and select records one by one or holding shift and select records as consecutive range.
* If you change the data in table, chart data will be changed as well. Try changing name, score 1~3 fields or adding/deleting the record. It works like a charm.
* 4 records are given by default to show how it works.
* You can search the text in table with writing the text in search bar. Table will show the matched records, chart will be not influenced by search bar.

## Example
```python
from PySide6.QtWidgets import QApplication
from pyside_db_chart_mapping_example.main import Window


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())
```

Result

![image](https://user-images.githubusercontent.com/55078043/190842429-dcbc0a37-a70e-4d5b-a1be-97c48f9b2c56.png)

## See Also
* <a href="https://doc.qt.io/qt-6/qtcharts-barmodelmapper-example.html">BarModelMapper Example</a> - table(not sql-based table) and chart mapping example in Qt documentation
* <a href="https://github.com/yjg30737/pyside-database-chart-example">pyside-database-chart-example</a> - non-mapping version (i tried to map each other on my own, but failed)
