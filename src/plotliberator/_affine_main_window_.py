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
from PySide import QtGui, QtCore
from PySide.QtCore import Qt

# local imports
from plot_scene import PlotScene
from plot_view import PlotView

IMAGE_FILTER = ('Image (*.bmp *.gif *.jpg *.jpeg *.png *.pbm '
                       '*.pgm *.ppm *.tiff *.xbm *.xpm)')
TXT_FILTER = 'Tab Delimited Text (*.txt)'
CSV_FILTER = 'Comma Separated Values (*.csv)'


class MainWindow(QtGui.QMainWindow):

    filepath = ''
    plotScene = None

    def __init__(self):
        super(MainWindow, self).__init__()

        # Initialize GUI stuff
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Plot Liberator')
        self.resize(1280, 800)
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
                                        '%g' % self.plotScene.x1)
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

        # Layout
        widget = QtGui.QWidget()
        grid = QtGui.QGridLayout()
        #TODO: change Tab key to go to the right before going down

        #TODO: Color 'X Axis' red and 'Y Axis' blue?
        #TODO: Reshape this to give visual cues for which values corrispond
        # to what. For example:
        #         -----
        # yEnd   |     |
        #         -----
        # yStart |     |
        #         -----
        #                 -----    -----
        #                |     |  |     |
        #                 -----    -----
        #                xStart    xEnd
        grid.addWidget(QtGui.QLabel('X Axis'), 1, 0)
        grid.addWidget(QtGui.QLabel('Y Axis'), 2, 0)
        grid.addWidget(QtGui.QLabel('Start Value'), 0, 1)
        grid.addWidget(self.x1LineEdit, 1, 1)
        grid.addWidget(self.y1LineEdit, 2, 1)
        grid.addWidget(QtGui.QLabel('End Value'), 0, 2)
        grid.addWidget(self.x2LineEdit, 1, 2)
        grid.addWidget(self.y2LineEdit, 2, 2)
        grid.addWidget(QtGui.QLabel('Logarithmic'), 0, 3)
        grid.addWidget(self.xLogCheckBox, 1, 3, Qt.AlignHCenter)
        grid.addWidget(self.yLogCheckBox, 2, 3, Qt.AlignHCenter)
        grid.setColumnStretch(4, 1)
        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(grid)
        vbox.addWidget(self.view)

        widget.setLayout(vbox)
        self.setCentralWidget(widget)

        # Connect slots and signals

        self.x1LineEdit.textChanged.connect(
                                        self.x1Changed)
        self.x2LineEdit.textChanged.connect(
                                        self.x2Changed)
        self.y1LineEdit.textChanged.connect(
                                        self.y1Changed)
        self.y2LineEdit.textChanged.connect(
                                        self.y2Changed)

        self.xLogCheckBox.stateChanged.connect(self.xLogChanged)
        self.yLogCheckBox.stateChanged.connect(self.yLogChanged)

    def validateAxisValue(self, lineEdit):
        s = lineEdit.text()
        try:
            return float(s)
        except ValueError:
            #TODO: change background to red
            return None

    def x1Changed(self):
        v = self.validateAxisValue(self.x1LineEdit)
        if v is not None:
            self.plotScene.x1 = v

    def x2Changed(self):
        v = self.validateAxisValue(self.x2LineEdit)
        if v is not None:
            self.plotScene.x2 = v

    def y1Changed(self):
        v = self.validateAxisValue(self.y1LineEdit)
        if v is not None:
            self.plotScene.y1 = v

    def y2Changed(self):
        v = self.validateAxisValue(self.y2LineEdit)
        if v is not None:
            self.plotScene.y2 = v

    def xLogChanged(self):
        self.plotScene._xLog = (self.xLogCheckBox.checkState()
                                           == Qt.CheckState.Checked)

    def yLogChanged(self):
        self.plotScene._yLog = (self.yLogCheckBox.checkState()
                                           == Qt.CheckState.Checked)

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
            x, y = self.plotScene.getData()
            for x, y in zip(x, y):
                print x, y
                f.write('%E%s%E\n' % (x, delimiter, y))

    def about(self):
        title = 'About Plot Liberator'
        text = """
   Copyright (c) 2014, Scott J Maddox

   This file is part of Plot Liberator.

   Plot Liberator is free software: you can redistribute it and/or modify
   it under the terms of the GNU Affero General Public License as
   published by the Free Software Foundation, either version 3 of the
   License, or (at your option) any later version.

   Plot Liberator is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU Affero General Public License for more details.

   You should have received a copy of the GNU Affero General Public
   License along with Plot Liberator.  If not, see
   <http://www.gnu.org/licenses/>.
        """
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
