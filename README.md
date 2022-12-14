# pyside-db-chart-mapping-example
PySide6 example of mapping database table(QSqlTableModel based tableview) and chart with QVBarModelMapper.

All basic CRUD feature of database mapped into chart(QChartView).

You can save the chart as image/pdf file, you can see the saved file over <a href="https://github.com/yjg30737/pyside-db-chart-mapping-example/tree/main/pyside_db_chart_mapping_example/save_chart_sample">here</a>.

You can find out more features and usages below. 

## Requirements
* <b>PySide6</b>

## Packages which will be automatically install (All of them are related to import/export as excel feature)
* <b>xlsxwriter</b> - export as excel
* <b>pandas</b> - import as excel
* <b>openpyxl</b> - import as excel

Note: pandas maybe requires more packages than above such as <b>daas</b>.

## Setup
`python -m pip install git+https://github.com/yjg30737/pyside-db-chart-mapping-example.git --upgrade`

### If you don't want to import/export excel feature and install related libraries
`python -m pip install git+https://github.com/yjg30737/pyside-db-chart-mapping-example.git@7d204961cd7462266ab15a20e9c0a62c40ab74fc`


## Usage/Feature
* If you want to delete more than one record, holding ctrl and select records one by one or holding shift and select records as consecutive range.
* If you change the data in table, chart data will be changed as well. Try changing name, score 1~3 fields or adding/deleting the record. It works like a charm.
* 4 records are given by default to show how it works.
* You can search the text in table with writing the text in search bar. Table will show the matched records, chart will be not influenced by search bar.
* ID cell can't be editable which is supposed to be like that, you can write number only to score 1~3 columns.
* You can save the chart as an image/pdf file.
* If you put the mouse cursor on the bar, barset's border color will be changed. If you select/click one of the bar, its background color will be changed and text browser will show the bar's info. If cursor leaves, border color will be restored as normal.
* You can change each color of the bar, choose to set the animation of chart in the settings dialog.
* Import/export excel file
* Being able to view the table info

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

![python_example](https://user-images.githubusercontent.com/55078043/193983371-8fd5c1a3-db4e-45f1-b643-f2df71f9cb77.png)

You don't have to care about left check box list. I'm still working on it.

![image](https://user-images.githubusercontent.com/55078043/193983236-7e5522fd-0cd9-42d7-93a1-f2266691bb51.png)

If you place the mouse cursor on one of the bar, barset border's color will be changed as i mentioned before. In this case, border color turns to be red.

Click the bar will change the bar's background color and show the bar's basic info on the text browser. In this case, background color turns to be green.

## See Also
* <a href="https://doc.qt.io/qt-6/qtcharts-barmodelmapper-example.html">BarModelMapper Example</a> - table(not sql-based table) and chart mapping example in Qt documentation
* <a href="https://github.com/yjg30737/pyside-database-chart-example">pyside-database-chart-example</a> - non-mapping version (i tried to map each other on my own, but failed)

## Note
I'm struggling with the problem that item is not added more than one after table was empty.

After much research i convince this is gotta be glitch.

Don't want to report this to Qt however. Someone please do it for me. 

I just want to figure it out on my own. 

Another glitch i found is that you have to add more than one if you add 1 to the last column of the mapper(QVBarModelMapper).

```python
self.__mapper.setLastBarSetColumn(self.__mapper.lastBarSetColumn()+2)
```

I don't even know what's going on here.
