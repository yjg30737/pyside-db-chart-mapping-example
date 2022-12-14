from setuptools import setup, find_packages

setup(
    name='pyside-db-chart-mapping-example',
    version='0.0.38',
    author='Jung Gyu Yoon',
    author_email='yjg30737@gmail.com',
    license='MIT',
    packages=find_packages(),
    package_data={'pyside_db_chart_mapping_example.ico': ['search.svg'],
                  'pyside_db_chart_mapping_example.style': ['lineedit.css', 'search_bar.css', 'widget.css',
                                                            'black_overlay.css',
                                                                           'black_ring_of_color_selector.css',
                                                                           'color_selector.css',
                                                                           'hue_bg.css',
                                                                           'hue_frame.css',
                                                                           'hue_selector.css']},
    description='PySide6 example of mapping database table(QSqlTableModel based table view) and chart with QVBarModelMapper',
    url='https://github.com/yjg30737/pyside-db-chart-mapping-example.git',
    install_requires=[
        'PySide6',
        'xlsxwriter',
        'pandas',
        'openpyxl'
    ]
)