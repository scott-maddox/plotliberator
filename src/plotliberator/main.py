#
#   Copyright (c) 2014, Scott J Maddox
#
#   This file is part of Plot Liberator.
#
#   Plot Liberator is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published
#   by the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   Plot Liberator is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with Plot Liberator.  If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

# third party imports
from PySide import QtGui, QtCore

# local imports
from main_window import MainWindow

app = QtGui.QApplication([])

# Set up QSettings
app.setOrganizationName("Scott J Maddox")
app.setApplicationName("Plot Liberator")
settings = QtCore.QSettings()

# Create main window
w = MainWindow()
w.show()
w.activateWindow()
w.raise_()


def run():
    app.exec_()

if __name__ == '__main__':
    run()
