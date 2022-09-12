from setuptools import setup, find_packages

setup(
    name='pyside-db-chart-mapping-example',
    version='0.0.11',
    author='Jung Gyu Yoon',
    author_email='yjg30737@gmail.com',
    license='MIT',
    packages=find_packages(),
    description='Example of mapping database table and chart with PySide6',
    url='https://github.com/yjg30737/pyside-db-chart-mapping-example.git',
    install_requires=[
        'PySide6'
    ]
)