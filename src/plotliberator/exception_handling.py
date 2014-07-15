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

# std lib imports
import sys
import traceback

# third party imports
from PySide import QtGui, QtCore


class IgnoreException(Exception):
    '''A special exception class to be ignored by the exception handler.'''
    pass


class QuitException(Exception):
    '''A special exception class that signifies the user wants to quit.'''
    pass


def excepthook(exctype, value, traceback):
    '''Show an exception dialog if an uncaught exception occurs'''
    # IgnoreException's are ignored to clear out the stack frame
    # from the previous exception
    if isinstance(value, IgnoreException):
        return
    elif isinstance(value, QuitException):
        sys.exit()
    else:
        d = ExceptionDialog(exctype, value, traceback)
        d.exec_()


def install_excepthook():
    # Install the exception hook
    sys.excepthook = excepthook


class ExceptionDialog(QtGui.QDialog):
    def __init__(self, exctype, excvalue, exctraceback, parent=None, f=0):
        super(ExceptionDialog, self).__init__(parent, f)
        self.setModal(True)  # block input to other windows
        self.resize(600, 500)

        # The error display
        text = ''.join(traceback.format_exception(exctype, excvalue,
                                                  exctraceback))
        tracebackTextEdit = QtGui.QTextEdit(text)
        tracebackTextEdit.setReadOnly(True)

        # The ignore and quit buttons
        self.ignoreButton = QtGui.QPushButton('Ignore')
        self.quitButton = QtGui.QPushButton('Quit')

        # Layout
        grid = QtGui.QGridLayout()
        grid.addWidget(tracebackTextEdit, 0, 0, 1, 3)
        grid.addWidget(self.ignoreButton, 1, 1)
        grid.addWidget(self.quitButton, 1, 2)
        grid.setColumnStretch(0, 1)
        grid.setRowStretch(0, 1)
        self.setLayout(grid)

        # Connect signals and slots
        self.ignoreButton.clicked.connect(self.ignore)
        self.quitButton.clicked.connect(self.quit)

    def _raiseIgnoreException(self):
        raise IgnoreException()

    def _raiseQuitException(self):
        raise QuitException()

    def ignore(self):
        QtCore.QTimer.singleShot(0, self._raiseIgnoreException)
        self.reject()

    def quit(self):
        QtCore.QTimer.singleShot(0, self._raiseQuitException)
        self.reject()

if __name__ == '__main__':
    app = QtGui.QApplication([])
    w = QtGui.QMainWindow()
    w.show()

    # Create a one-shot timer to install the excepthook
    QtCore.QTimer.singleShot(0, install_excepthook)

    def chirp():
        print 'chirp'
    timer1 = QtCore.QTimer()
    timer1.setInterval(100)
    timer1.timeout.connect(chirp)
    timer1.start()

    def fail():
        raise Exception()
    timer2 = QtCore.QTimer()
    timer2.setInterval(1000)
    timer2.timeout.connect(fail)
    timer2.start()

    sys.excepthook = excepthook
    app.exec_()