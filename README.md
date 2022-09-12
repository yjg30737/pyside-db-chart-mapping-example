# pyside-db-chart-mapping-example
Example of mapping database table and chart with PySide6

## Requirements
* PySide6

## Setup
`python -m pip install git+https://github.com/yjg30737/pyside-db-chart-mapping-example.git --upgrade`

## Example
```python
from pyside_db_chart_mapping_example.chart import *

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
```

Result

![image](https://user-images.githubusercontent.com/55078043/189555178-9da916c8-1cb2-4b05-b7d3-988a2655a087.png)

## See Also
* <a href="https://github.com/yjg30737/pyside-database-chart-example">pyside-database-chart-example</a> - non-mapping version (i tried to map each other, but failed)
