from distutils.core import setup

setup(
    name='payByPhone_calendar',
    version='0.1',
    url='https://github.com/Ajira-FR/payByPhone_calendar',
    license='',
    author='Sébastien',
    author_email='',
    description='An HTML calendar with a Python back-end to manage PayByPhone parking ticket',
    packages=['bottle', 'bottle_sqlite', 'bs4', 'sqlite3', 'requests']
)
