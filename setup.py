# coding: utf-8
from setuptools import setup, find_packages

setup(
    name='payByPhone_calendar',
    version='0.1',
    url='https://github.com/Ajira-FR/payByPhone_calendar',
    license='GPL',
    author='Sebastien',
    author_email='',
    description='An HTML calendar with a Python back-end to manage PayByPhone parking ticket',
    long_description=open('README.md').read(),
    packages=find_packages(),
    install_requires=['bottle', 'bottle_sqlite', 'bs4', 'sqlite3', 'requests']
)
