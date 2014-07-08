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
from graphics_view import ZoomableGraphicsView
from plot_item import PlotItem
from axis_item import AxesItem

IMAGE_FILTER = ('Image (*.bmp *.gif *.jpg *.jpeg *.png *.pbm '
                       '*.pgm *.ppm *.tiff *.xbm *.xpm)')
TXT_FILTER = 'Tab Delimited Text (*.txt)'
CSV_FILTER = 'Comma Separated Values (*.csv)'


class MainWindow(QtGui.QMainWindow):

    filepath = ''
    xAxis = None
    yAxis = None
    plotItem = None
    dataPointItems = []

    def __init__(self):
        super(MainWindow, self).__init__()

        # Initialize GUI stuff
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Plot Liberator')
        self.resize(1280, 800)
        self.moveTopLeft()

        # Graphics View, etc.
        self.scene = QtGui.QGraphicsScene()
        self.view = ZoomableGraphicsView(self.scene)
        self.initAxes()

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
        self.x1LineEdit = QtGui.QLineEdit('0.')
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

        # Layout
        widget = QtGui.QWidget()
        grid = QtGui.QGridLayout()
        grid.addWidget(QtGui.QLabel('X Axis Values:'), 0, 0)
        grid.addWidget(QtGui.QLabel('Y Axis Values:'), 1, 0)
        grid.addWidget(self.x1LineEdit, 0, 1)
        grid.addWidget(self.x2LineEdit, 0, 2)
        grid.addWidget(self.y1LineEdit, 1, 1)
        grid.addWidget(self.y2LineEdit, 1, 2)
        grid.setColumnStretch(3, 1)
        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(grid)
        vbox.addWidget(self.view)

        widget.setLayout(vbox)
        self.setCentralWidget(widget)

    def initAxes(self):
        xline = QtCore.QLineF(0., 100., 100., 100.)
        yline = QtCore.QLineF(0., 100., 0., 0.)
        self.xAxis = AxesItem(xline, scene=self.scene())
        self.yAxis = AxesItem(yline, scene=self.scene())
        self.xAxis.setPen(QtGui.QPen(Qt.red, 1., Qt.DashLine))
        self.yAxis.setPen(QtGui.QPen(Qt.blue, 1., Qt.DashLine))
        self.xAxis.setZValue(-1.)
        self.yAxis.setZValue(-1.)

    def open(self):
        filepath, filt = QtGui.QFileDialog.getOpenFileName(
                                parent=self,
                                caption='Open a plot image',
                                dir=self.filepath,
                                filter=IMAGE_FILTER)
        if not filepath:
            return
        dirpath, filename = os.path.split(filepath)
        self.setWindowTitle(u'Plot Liberator - {}'.format(filename))

        image = QtGui.QImage(filepath)
        if image.isNull():
            QtGui.QMessageBox.information(self, "Plot Liberator",
                    "Cannot load %s." % filepath)
            return

        # Store the filepath for use in save
        self.filepath = filepath

        # Replace the old plot with the new one
        if self.plotItem is not None:
            self.scene.removeItem(self.plotItem)
        pixmap = QtGui.QPixmap.fromImage(image)
        self.plotItem = PlotItem(pixmap, scene=self.scene)

        # Make zooming look pretty
        self.plotItem.setTransformationMode(Qt.SmoothTransformation)

        # Put the image on the back plane
        self.plotItem.setZValue(-2.)

        # Update the axis
        rect = self.plotItem.boundingRect()
        x1 = rect.bottomLeft()
        x2 = rect.bottomRight()
        y1 = rect.bottomLeft()
        y2 = rect.topLeft()
        xline = QtCore.QLineF(x1, x2)
        yline = QtCore.QLineF(y1, y2)
        self.xAxis.setLine(xline)
        self.yAxis.setLine(yline)

    def save(self):
        filepath, filt = QtGui.QFileDialog.getSaveFileName(parent=self,
                                caption='Save data',
                                dir=self.filepath,
                                filter=TXT_FILTER + ';;' + CSV_FILTER)
        if not filepath:
            return
        print "save to {}".format(filepath)
        print "filter: {}".format(filter)
        if filt == TXT_FILTER:
            delimiter = '\t'
        elif filt == CSV_FILTER:
            delimiter = ','
        else:
            raise RuntimeError('unexpected execution path')
        with open(filepath, 'w') as f:
            for x, y in zip(self.getData()):
                f.write('%E%s%E\n' % (x, delimiter, y))

    def getData(self):
        '''
        Returns the data, after transforming to the user-defined axis

        Returns
        -------
        x : list of floats
        y : list of floats
        '''
        x = []
        y = []
        for item in self.dataPointItems:
            x.append(item.x())
            y.append(item.y())
        return self.transformData(x, y)

    def transformData(self, x, y):
        '''
        Transforms position data to axis data

        Returns
        -------
        x : list of floats
        y : list of floats
        '''
        #TODO: implement
        raise NotImplementedError()

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
