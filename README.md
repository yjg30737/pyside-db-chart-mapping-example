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
* ID cell can't be editable which is supposed to be like that, you can write number only to score 1~3 columns.

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

![image](https://user-images.githubusercontent.com/55078043/192137474-9d927d19-c634-454f-b89e-d5d05fe824fe.png)

## See Also
* <a href="https://doc.qt.io/qt-6/qtcharts-barmodelmapper-example.html">BarModelMapper Example</a> - table(not sql-based table) and chart mapping example in Qt documentation
* <a href="https://github.com/yjg30737/pyside-database-chart-example">pyside-database-chart-example</a> - non-mapping version (i tried to map each other on my own, but failed)

## Note
I'm struggling with the problem that item is not added more than one after table was empty. 

After much research i convince this is gotta be glitch.

Don't want to report this to Qt however. Someone please do it for me. 

I just want to figure it out on my own. 
