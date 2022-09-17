# pyside-db-chart-mapping-example
Example of mapping database table and chart with PySide6

## Requirements
* PySide6

## Setup
`python -m pip install git+https://github.com/yjg30737/pyside-db-chart-mapping-example.git --upgrade`

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
* <a href="https://github.com/yjg30737/pyside-database-chart-example">pyside-database-chart-example</a> - non-mapping version (i tried to map each other, but failed)
