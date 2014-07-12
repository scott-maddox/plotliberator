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
import os.path

# third party imports
from PySide import QtGui
from PySide.QtCore import Qt

# local imports
from version import __version__
from plot_scene import PlotScene
from plot_view import PlotView

IMAGE_FILTER = ('Image (*.bmp *.gif *.jpg *.jpeg *.png *.pbm '
                       '*.pgm *.ppm *.tiff *.xbm *.xpm)')
TXT_FILTER = 'Tab Delimited Text (*.txt)'
CSV_FILTER = 'Comma Separated Values (*.csv)'
QLABEL_COLOR_RED = 'QLabel{color: red;}'


def floatOrNone(s):
    try:
        return float(s)
    except ValueError:
        return None


class MainWindow(QtGui.QMainWindow):

    filepath = ''
    plotScene = None

    def __init__(self):
        super(MainWindow, self).__init__()

        # Initialize GUI stuff
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Plot Liberator')
#         self.resize(1280, 800)
        self.resize(600, 500)
        self.moveTopLeft()

        # PlotScene, PlotView, etc.
        self.plotScene = PlotScene(parent=self)
        self.view = PlotView(scene=self.plotScene, parent=self)

        # Actions and menus
        self.aboutAction = QtGui.QAction('&About', self)
        self.aboutAction.triggered.connect(self.about)

        self.openAction = QtGui.QAction('&Open', self)
        self.openAction.setStatusTip('Open a plot')
        self.openAction.setToolTip('Open a plot')
        self.openAction.setShortcut('Ctrl+O')
        self.openAction.triggered.connect(self.open)

        self.actualSizeAction = QtGui.QAction('Actual Size', self)
        self.actualSizeAction.setShortcut('Ctrl+0')
        self.actualSizeAction.triggered.connect(self.view.actualSize)
        self.zoomInAction = QtGui.QAction('Zoom In', self)
        self.zoomInAction.setShortcut('Ctrl++')
        self.zoomInAction.triggered.connect(self.view.zoomIn)
        self.zoomOutAction = QtGui.QAction('Zoom Out', self)
        self.zoomOutAction.setShortcut('Ctrl+-')
        self.zoomOutAction.triggered.connect(self.view.zoomOut)

        self.saveAction = QtGui.QAction('&Save', self)
        self.saveAction.setStatusTip('Save data')
        self.saveAction.setToolTip('Save data')
        self.saveAction.setShortcut('Ctrl+S')
        self.saveAction.triggered.connect(self.save)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(self.openAction)
        fileMenu.addAction(self.saveAction)

        viewMenu = menubar.addMenu('&View')
        viewMenu.addAction(self.actualSizeAction)
        viewMenu.addAction(self.zoomInAction)
        viewMenu.addAction(self.zoomOutAction)

        aboutMenu = menubar.addMenu('&About')
        aboutMenu.addAction(self.aboutAction)

        # Create a status bar
        self.statusBar()

        # Axis value line edits
        self.x1LineEdit = QtGui.QLineEdit(
                                        '%g' % self.plotScene._x1)
        self.x2LineEdit = QtGui.QLineEdit('1.')
        self.y1LineEdit = QtGui.QLineEdit('0.')
        self.y2LineEdit = QtGui.QLineEdit('1.')

        self.x1LineEdit.setValidator(QtGui.QDoubleValidator())
        self.x2LineEdit.setValidator(QtGui.QDoubleValidator())
        self.y1LineEdit.setValidator(QtGui.QDoubleValidator())
        self.y2LineEdit.setValidator(QtGui.QDoubleValidator())

        self.x1LineEdit.setMinimumWidth(50)
        self.x2LineEdit.setMinimumWidth(50)
        self.y1LineEdit.setMinimumWidth(50)
        self.y2LineEdit.setMinimumWidth(50)

        # Axis log mode check boxes
        self.xLogCheckBox = QtGui.QCheckBox()
        self.yLogCheckBox = QtGui.QCheckBox()

        # Labels
        self.x1Label = QtGui.QLabel('x1')
        self.x2Label = QtGui.QLabel('x2')
        self.y1Label = QtGui.QLabel('y1')
        self.y2Label = QtGui.QLabel('y2')
        self.xLogLabel = QtGui.QLabel('log')
        self.yLogLabel = QtGui.QLabel('log')

        # Layout
        widget = QtGui.QWidget()
        grid = QtGui.QGridLayout()

        # GridLayout:
        #      0      1          2         3      4      5
        #                    |-------------------------------|
        #  0                 |                               |
        #                    |                               |
        #          |---|     |                               |
        #  1  log  |   |     |                               |
        #          |---|     |            PlotView           |
        #          |------|  |                               |
        #  2   y2  |      |  |                               |
        #          |------|  |                               |
        #          |------|  |                               |
        #  3   y1  |      |  |                               |
        #          |------|  |-------------------------------|
        #                    |------|  |------|  |---|
        #  4                 |      |  |      |  |   |
        #                    |------|  |------|  |---|
        #
        #  5                    x1        x2      log

        grid.addWidget(self.yLogLabel, 1, 0)
        grid.addWidget(self.y2Label, 2, 0)
        grid.addWidget(self.y1Label, 3, 0)
        grid.addWidget(self.yLogCheckBox, 1, 1)
        grid.addWidget(self.y2LineEdit, 2, 1)
        grid.addWidget(self.y1LineEdit, 3, 1)

        grid.addWidget(self.x1LineEdit, 4, 2)
        grid.addWidget(self.x2LineEdit, 4, 3)
        grid.addWidget(self.xLogCheckBox, 4, 4)
        grid.addWidget(self.x1Label, 5, 2, Qt.AlignHCenter)
        grid.addWidget(self.x2Label, 5, 3, Qt.AlignHCenter)
        grid.addWidget(self.xLogLabel, 5, 4, Qt.AlignHCenter)

        grid.addWidget(self.view, 0, 2, 4, 4)
        grid.setRowStretch(0, 1)
        grid.setColumnStretch(5, 1)

        widget.setLayout(grid)
        self.setCentralWidget(widget)

        # Connect slots and signals

        self.x1LineEdit.textChanged.connect(self.xValueChanged)
        self.x2LineEdit.textChanged.connect(self.xValueChanged)
        self.xLogCheckBox.stateChanged.connect(self.xValueChanged)
        self.y1LineEdit.textChanged.connect(self.yValueChanged)
        self.y2LineEdit.textChanged.connect(self.yValueChanged)
        self.yLogCheckBox.stateChanged.connect(self.yValueChanged)

    def xValueChanged(self):
        x1 = floatOrNone(self.x1LineEdit.text())
        x2 = floatOrNone(self.x2LineEdit.text())
        xLog = (self.xLogCheckBox.checkState() == Qt.CheckState.Checked)

        fail = False
        if x1 is None:
            self.x1Label.setStyleSheet(QLABEL_COLOR_RED)
            fail = True
        if x2 is None:
            self.x2Label.setStyleSheet(QLABEL_COLOR_RED)
            fail = True
        if xLog and x1 == 0.:
            self.xLogLabel.setStyleSheet(QLABEL_COLOR_RED)
            self.x1Label.setStyleSheet(QLABEL_COLOR_RED)
            fail = True
        if xLog and x2 == 0.:
            self.xLogLabel.setStyleSheet(QLABEL_COLOR_RED)
            self.x1Label.setStyleSheet(QLABEL_COLOR_RED)
            fail = True

        if not fail:
            self.xLogLabel.setStyleSheet('')
            self.x1Label.setStyleSheet('')
            self.x2Label.setStyleSheet('')
            self.plotScene.setXValues(x1, x2, xLog)

    def yValueChanged(self):
        y1 = floatOrNone(self.y1LineEdit.text())
        y2 = floatOrNone(self.y2LineEdit.text())
        yLog = (self.yLogCheckBox.checkState() == Qt.CheckState.Checked)

        fail = False
        if y1 is None:
            self.y1Label.setStyleSheet(QLABEL_COLOR_RED)
            fail = True
        if y2 is None:
            self.y2Label.setStyleSheet(QLABEL_COLOR_RED)
            fail = True
        if yLog and y1 == 0.:
            self.yLogLabel.setStyleSheet(QLABEL_COLOR_RED)
            self.y1Label.setStyleSheet(QLABEL_COLOR_RED)
            fail = True
        if yLog and y2 == 0.:
            self.yLogLabel.setStyleSheet(QLABEL_COLOR_RED)
            self.y1Label.setStyleSheet(QLABEL_COLOR_RED)
            fail = True

        if not fail:
            self.yLogLabel.setStyleSheet('')
            self.y1Label.setStyleSheet('')
            self.y2Label.setStyleSheet('')
            self.plotScene.setYValues(y1, y2, yLog)

    def open(self):
        filepath, _filt = QtGui.QFileDialog.getOpenFileName(
                                parent=self,
                                caption='Open a plot image',
                                dir=self.filepath,
                                filter=IMAGE_FILTER)
        if not filepath:
            return
        _dirpath, filename = os.path.split(filepath)
        self.setWindowTitle(u'Plot Liberator - {}'.format(filename))

        image = QtGui.QImage(filepath)
        if image.isNull():
            QtGui.QMessageBox.information(self, "Plot Liberator",
                    "Cannot load %s." % filepath)
            return

        # Store the filepath for use in save
        self.filepath = filepath

        # Replace the old plot with the new one
        self.plotScene.setPlotImage(image)

    def save(self):
        filepath, filt = QtGui.QFileDialog.getSaveFileName(parent=self,
                                caption='Save data',
                                dir=self.filepath,
                                filter=TXT_FILTER + ';;' + CSV_FILTER)
        if not filepath:
            return

        if filt == TXT_FILTER:
            delimiter = '\t'
        elif filt == CSV_FILTER:
            delimiter = ','
        else:
            raise RuntimeError('unexpected execution path')
        with open(filepath, 'w') as f:
            for x, y in self.plotScene.getData():
                f.write('%E%s%E\n' % (x, delimiter, y))

    def about(self):
        title = 'About Plot Liberator'
        text = ('Plot Liberator\n'
                'Version {}\n'
                '\n'
                'Copyright (c) 2014, Scott J Maddox\n'
                '\n'
                'Plot Liberator is free software: you can redistribute it'
                ' and/or modify it under the terms of the GNU Affero General'
                ' Public License as published by the Free Software Foundation,'
                ' either version 3 of the License, or (at your option) any'
                ' later version.\n'
                '\n'
                'Plot Liberator is distributed in the hope that it will be'
                ' useful, but WITHOUT ANY WARRANTY; without even the implied'
                ' warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR'
                ' PURPOSE.  See the GNU Affero General Public License for'
                ' more details.\n'
                '\n'
                'You should have received a copy of the GNU Affero General'
                ' Public License along with Plot Liberator.  If not, see'
                ' <http://www.gnu.org/licenses/>.'
                ''.format(__version__))
        QtGui.QMessageBox.about(self, title, text)

    def moveCenter(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def moveTopLeft(self):
        p = QtGui.QDesktopWidget().availableGeometry().topLeft()
        self.move(p)

    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, 'Quit?',
                'Are you sure you want to quit?',
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
