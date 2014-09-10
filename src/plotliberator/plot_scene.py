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
from math import exp, log

# third party imports
from PySide import QtGui, QtCore
from PySide.QtCore import Qt

# local imports
from plotliberator.graphics_items import MovableCursorItem, GuideLineItem


class PlotScene(QtGui.QGraphicsScene):

    dataPointItems = []
    dataTransform = None

    _x1 = 0.
    _x2 = 1.
    _xLog = False
    _y1 = 0.
    _y2 = 1.
    _yLog = False

    def __init__(self, parent=None):
        super(PlotScene, self).__init__(parent)

        # Initialize axis corners:
        # c1  c2
        #
        # c4  c3
        self.c1 = MovableCursorItem(QtCore.QPointF(0, 0), scene=self)
        self.c2 = MovableCursorItem(QtCore.QPointF(300, 0), scene=self)
        self.c3 = MovableCursorItem(QtCore.QPointF(300, 300), scene=self)
        self.c4 = MovableCursorItem(QtCore.QPointF(0, 300), scene=self)

        self.c1.setPen(QtGui.QPen(Qt.red, 1., Qt.SolidLine))
        self.c2.setPen(QtGui.QPen(Qt.red, 1., Qt.SolidLine))
        self.c3.setPen(QtGui.QPen(Qt.red, 1., Qt.SolidLine))
        self.c4.setPen(QtGui.QPen(Qt.red, 1., Qt.SolidLine))

        self.c1.setZValue(2.)
        self.c2.setZValue(2.)
        self.c3.setZValue(2.)
        self.c4.setZValue(2.)

        # Initialize guide lines
        self.gl1 = GuideLineItem(self.c1, self.c2, scene=self)
        self.gl2 = GuideLineItem(self.c2, self.c3, scene=self)
        self.gl3 = GuideLineItem(self.c3, self.c4, scene=self)
        self.gl4 = GuideLineItem(self.c4, self.c1, scene=self)

        self.gl1.setPen(QtGui.QPen(Qt.red, 1., Qt.DashLine))
        self.gl2.setPen(QtGui.QPen(Qt.red, 1., Qt.DashLine))
        self.gl3.setPen(QtGui.QPen(Qt.red, 1., Qt.DashLine))
        self.gl4.setPen(QtGui.QPen(Qt.red, 1., Qt.DashLine))

        self.gl1.setZValue(1.)
        self.gl2.setZValue(1.)
        self.gl3.setZValue(1.)
        self.gl4.setZValue(1.)

        # Initialize the data tranform
        self.updateTransform()

        # Initialize pixmap item
        self.pixmapItem = QtGui.QGraphicsPixmapItem(scene=self)
        # Make pixmap zooming look pretty
        self.pixmapItem.setTransformationMode(Qt.SmoothTransformation)
        self.pixmapItem.setZValue(0.)

        # Connect signals and slots
        self.c1.posChanged.connect(self.updateTransform)
        self.c2.posChanged.connect(self.updateTransform)
        self.c3.posChanged.connect(self.updateTransform)
        self.c4.posChanged.connect(self.updateTransform)

    def x1(self):
        return self._x1

    def x2(self):
        return self._x2

    def y1(self):
        return self._y1

    def y2(self):
        return self._y2

    def setXValues(self, x1, x2, xLog):
        self._x1 = x1
        self._x2 = x2
        self._xLog = xLog
        self.updateTransform()

    def setYValues(self, y1, y2, yLog):
        self._y1 = y1
        self._y2 = y2
        self._yLog = yLog
        self.updateTransform()

    @QtCore.Slot(float)
    def setX1(self, v):
        print v
        self._x1 = v
        self.updateTransform()

    @QtCore.Slot(float)
    def setX2(self, v):
        print v
        self._x2 = v
        self.updateTransform()

    @QtCore.Slot(float)
    def setY1(self, v):
        print v
        self._y1 = v
        self.updateTransform()

    @QtCore.Slot(float)
    def setY2(self, v):
        print v
        self._y2 = v
        self.updateTransform()

    @QtCore.Slot(bool)
    def setXLog(self, v):
        self._xLog = v
        self.updateTransform()

    @QtCore.Slot(bool)
    def setYLog(self, v):
        self._yLog = v
        self.updateTransform()

    @QtCore.Slot()
    def updateTransform(self):
        p1 = self.c1.pos()
        p2 = self.c2.pos()
        p3 = self.c3.pos()
        p4 = self.c4.pos()
        inPolygon = QtGui.QPolygonF((p1, p2, p3, p4))
        if self._xLog:
            x1 = log(self._x1)
            x2 = log(self._x2)
        else:
            x1 = self._x1
            x2 = self._x2
        if self._yLog:
            y1 = log(self._y1)
            y2 = log(self._y2)
        else:
            y1 = self._y1
            y2 = self._y2
        outPolygon = QtGui.QPolygonF((QtCore.QPointF(x1, y2),
                                      QtCore.QPointF(x2, y2),
                                      QtCore.QPointF(x2, y1),
                                      QtCore.QPointF(x1, y1)))
        dataTransform = QtGui.QTransform.quadToQuad(inPolygon, outPolygon)
        if dataTransform is not None:
            self.dataTransform = dataTransform

    def setPlotImage(self, image):
        pixmap = QtGui.QPixmap.fromImage(image)
        self.pixmapItem.setPixmap(pixmap)
        w = image.width()
        h = image.height()

        # Move the corners to the image corners
        self.c1.setPos(0, 0)
        self.c2.setPos(w, 0)
        self.c3.setPos(w, h)
        self.c4.setPos(0, h)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # First, try to dispatch the event to any other items that might
            # want to accept it for movement purposes.
            super(PlotScene, self).mousePressEvent(event)
            if event.isAccepted():
                return
            # The event wasn't accepted, so we should add a data point.
            dataPointItem = MovableCursorItem(event.scenePos(),
                                              style='CircleCross')
            dataPointItem.setPen(QtGui.QPen(Qt.darkGreen, 1., Qt.SolidLine))
            dataPointItem.setZValue(3.)
            self.addDataPointItem(dataPointItem)
            event.accept()
        elif event.button() == Qt.RightButton:
            # First, check if the right click was on a dataPointItem.
            # If it was, remove that item and accept the event.
            item = self.itemAt(event.scenePos())
            if item in self.dataPointItems:
                self.removeDataPointItem(item)
                event.accept()
            # Otherwise, dispatch the event.
            super(PlotScene, self).mousePressEvent(event)
        else:
            super(PlotScene, self).mousePressEvent(event)

    def addDataPointItem(self, item):
        '''
        Add a data point item.
        '''
        self.dataPointItems.append(item)
        self.addItem(item)

    def removeDataPointItem(self, item):
        '''
        Remove a data point item.
        '''
        self.dataPointItems.remove(item)
        self.removeItem(item)

    def clearDataPointItems(self):
        '''
        Clears the data point items.
        '''
        for item in self.dataPointItems:
            self.removeItem(item)
        self.dataPointItems = []

    def getData(self):
        '''
        Returns a list of (x, y) data tuples (mapped from position)
        '''
        return [self.mapToData(item.x(), item.y())
                for item in self.dataPointItems]

    def mapToData(self, x, y):
        '''
        Map position to data
        '''
        newx, newy = self.dataTransform.map(x, y)
        if self._xLog:
            newx = exp(newx)
        if self._yLog:
            newy = exp(newy)
        return newx, newy

if __name__ == '__main__':
    app = QtGui.QApplication([])
    plotScene = PlotScene()
    view = QtGui.QGraphicsView(plotScene)
    image = QtGui.QImage('test/test.png')
    plotScene.setPlotImage(image)
    h = plotScene.pixmapItem.pixmap().height()
    w = plotScene.pixmapItem.pixmap().width()

    view.show()
    view.raise_()
    app.exec_()
