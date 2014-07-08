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
from math import cos, pi

# third party imports
from PySide import QtGui, QtCore
from PySide.QtCore import Qt

# local imports
from axis_item import AxesItem
from movable_items import MovableCursorItem


class PlotScene(QtGui.QGraphicsScene):

    dataPointItems = []

    #TODO: implement log mode
    _xLog = False
    _yLog = False

    x1 = 0.
    x2 = 1.
    y1 = 0.
    y2 = 1.

    def __init__(self, parent=None):
        super(PlotScene, self).__init__(parent)

        # Initialize axis items
        self.xAxis = AxesItem(QtCore.QLineF(0, 300, 300, 300), scene=self)
        self.yAxis = AxesItem(QtCore.QLineF(0, 300, 0, 0), scene=self)
        self.xAxis.setPen(QtGui.QPen(Qt.red, 1., Qt.DashLine))
        self.yAxis.setPen(QtGui.QPen(Qt.blue, 1., Qt.DashLine))
        self.xAxis.setZValue(1.)
        self.yAxis.setZValue(1.)
        #TODO: Make linking the origins of the two axis an option?
        #      It could be a checkbox next to the xAxisLogCheckBox

        # Initialize pixmap item
        self.pixmapItem = QtGui.QGraphicsPixmapItem(scene=self)
        # Make pixmap zooming look pretty
        self.pixmapItem.setTransformationMode(Qt.SmoothTransformation)

    def setPlotImage(self, image):
        pixmap = QtGui.QPixmap.fromImage(image)
        self.pixmapItem.setPixmap(pixmap)
        w = pixmap.width()
        h = pixmap.height()
        xline = QtCore.QLineF(0, h, w, h)
        yline = QtCore.QLineF(0, h, 0, 0)
        self.xAxis.setLine(xline)
        self.yAxis.setLine(yline)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # First, try to dispatch the event to any other items that might
            # want to accept it for movement purposes.
            super(PlotScene, self).mousePressEvent(event)
            if event.isAccepted():
                return
            # The event wasn't accepted, so we should add a data point.
            dataPointItem = MovableCursorItem(event.scenePos(),
                                              style='CircleCross',
                                              scene=self)
            #TODO: change the dataPointItem pen/overlay style to always
            # contrast against the background (difference? multiply?)
            dataPointItem.setPen(QtGui.QPen(Qt.darkGreen, 1., Qt.SolidLine))
            dataPointItem.setZValue(2.)
            self.dataPointItems.append(dataPointItem)
            event.accept()
        elif event.button() == Qt.RightButton:
            # First, check if the right click was on a dataPointItem.
            # If it was, remove that item and accept the event.
            item = self.itemAt(event.scenePos())
            if item in self.dataPointItems:
                self.dataPointItems.remove(item)
                self.removeItem(item)
                event.accept()
            # Otherwise, dispatch the event.
            super(PlotScene, self).mousePressEvent(event)
        else:
            super(PlotScene, self).mousePressEvent(event)

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
        return self.mapToData(x, y)

    def mapToData(self, x, y):
        '''
        Map position to data

        Returns
        -------
        x : float or list of floats
        y : float or list of floats
        '''
        t = self._axisTransform()
        try:
            return t.map(x, y)
        except:
            xd = []
            yd = []
            for x, y in zip(x, y):
                xtmp, ytmp = t.map(x, y)
                xd.append(xtmp)
                yd.append(ytmp)
            return xd, yd

    def _axisTransform(self):
        '''Get the QTransform for mapping an item pos to data'''
        # Correspondance between matrix position and purpose:
        #    m11,    m12,   m13,    m21,    m22,   m23, m31, m32
        # hScale, vShear, hProj, hShear, vScale, vProj,  dx,  dy

        # In the current version, I'll assume an affine transformation
        # (i.e. parallelogram, i.e. no perspective)

        #TODO: implement NonAffineAxisItem, to allow full perspective
        # transformations. For now, I'm only using affine transformations.

        # QTransform performs the following operations for affine matricies:
        # xd = m11 * xp + m21 * yp + dx
        # yd = m22 * yp + m12 * xp + dy
        # where
        # xd and yd are the x and y values in data coordinates,
        # xp and yp are the x and y values in position coordinates, and
        # m11, m21, m22, m12, dx, and dy are matrix components

        xd1x = self.x1
        xd2x = self.x2
        yd1y = self.y1
        yd2y = self.y2

        xp1x = self.xAxis.p1().x()
        xp1y = self.xAxis.p1().y()
        xp2x = self.xAxis.p2().x()
        xp2y = self.xAxis.p2().y()

        yp1x = self.yAxis.p1().x()
        yp1y = self.yAxis.p1().y()
        yp2x = self.yAxis.p2().x()
        yp2y = self.yAxis.p2().y()

        # Unit vectors:
        xhat = QtCore.QLineF.fromPolar(1., self.xAxis.line().angle())
        yhat = QtCore.QLineF.fromPolar(1., self.yAxis.line().angle())

        # Intersection of the visible data axes
        _intersectType, i = self.xAxis.line().intersect(self.yAxis.line())
#         iLine = QtCore.QLineF(QtCore.QPointF(0., 0.), i)

        # Intersection of visible data axes with origin data axis
        x0 = self.xAxis.line().pointAt(xd1x / (xd1x - xd2x))
        y0 = self.yAxis.line().pointAt(yd1y / (yd1y - yd2y))
#         x0Line = QtCore.QLineF(QtCore.QPointF(0., 0.), x0)
#         y0Line = QtCore.QLineF(QtCore.QPointF(0., 0.), y0)

        # Origin of the data axes
        od = x0 + y0 - i
        odLine = QtCore.QLineF(QtCore.QPointF(0., 0.), od)

        # x3: intersection of the xAxis with yhat
        _intersectType, x3 = self.xAxis.line().intersect(yhat)
        # y3: intersection of the yAxis with xhat
        _intersectType, y3 = self.yAxis.line().intersect(xhat)

        m11 = (xd2x - xd1x) / (xp2x - xp1x)
        m22 = (yd2y - yd1y) / (yp2y - yp1y)
        m21 = m11 * (yp2x - yp1x) / (yp2y - yp1y)
        m12 = m22 * (xp2y - xp1y) / (xp2x - xp1x)
#         Th = odLine.length() * cos(odLine.angle(xhat) * pi / 180.)
#         Tv = odLine.length() * cos(odLine.angle(yhat) * pi / 180.)
        dxLine = QtCore.QLineF(x3, x0)
        dyLine = QtCore.QLineF(y3, y0)
        dx = m11 * dxLine.length() * cos(dxLine.angle(xhat) * pi / 180.)
        dy = m22 * dyLine.length() * cos(dyLine.angle(yhat) * pi / 180.)
        print 'dx = %g' % round(dx, 6), ', dy = %g' % round(dy, 6)

#         # xSign and ySign should be -1. when the data origin is to the
#         # bottom right of the position origin.
#         odAngle = QtCore.QLineF(QtCore.QPointF(0., 0.), od).angle()
#         assert odAngle >= 0.
#         if odAngle <= 90.:  # Quadrant 1
#             xSign = -1.
#             ySign = 1.
#         elif odAngle <= 180.:  # Quadrant 2
#             xSign = 1.
#             ySign = 1.
#         elif odAngle <= 270.:  # Quadrant 3
#             xSign = 1.
#             ySign = -1.
#         else:  # Quadrant 4
#             xSign = -1.
#             ySign = -1.
# 
#         if xd2x > xd1x:
#             xDir = 1.
#         else:
#             xDir = -1.
# 
#         if yd2y > yd1y:
#             yDir = 1.
#         else:
#             yDir = -1.
# 
#         dx = xDir * xSign * m11 * QtCore.QLineF(xp0, xp3).length()
#         dy = yDir * ySign * m22 * QtCore.QLineF(yp0, yp3).length()
#         print 'dx', dx, 'dy', dy

        t = QtGui.QTransform(m11, m12, m21, m22, dx, dy)
        return t

    def _perspectiveTransform(self):
        xd1x = self.x1
        xd2x = self.x2
        yd1y = self.y1
        yd2y = self.y2
        p1 = QtCore.QPointF()
        p2 = QtCore.QPointF()
        p3 = QtCore.QPointF()
        p4 = QtCore.QPointF()
        p1_ = QtCore.QPointF()
        p2_ = QtCore.QPointF()
        p3_ = QtCore.QPointF()
        p4_ = QtCore.QPointF()
        t = QtGui.QTransform(m11, m12, m13, m21, m22, m23, m31, m32)
        return t

if __name__ == '__main__':
    app = QtGui.QApplication([])
    plotScene = PlotScene()
    view = QtGui.QGraphicsView(plotScene)
    image = QtGui.QImage('test/test.png')
    plotScene.setPlotImage(image)
    h = plotScene.pixmapItem.pixmap().height()
    w = plotScene.pixmapItem.pixmap().width()

    def testPairs(pairs):
        for (xpos, ypos), (xdata, ydata) in pairs:
            x, y = plotScene.mapToData(xpos, ypos)
            if (abs(x - xdata) > 1e-6) or (abs(y - ydata) > 1e-6):
                print ('FAIL ({:g}, {:g}) --> ({:g}, {:g}) != ({:g}, {:g})'
                      ''.format(xpos, ypos, round(x, 6), round(y, 6),
                                xdata, ydata))
            else:
                print 'OK ({:g}, {:g}) --> ({:g}, {:g})'.format(
                                                xpos, ypos, xdata, ydata)
        print ''
    # Test mapToData
    print "Testing default values"
    plotScene.x1 = 0.
    plotScene.x2 = 1.
    plotScene.y1 = 0.
    plotScene.y2 = 1.
    pairs = [((0., 0.), (0., 1.)),
             ((0., h), (0., 0.)),
             ((w, 0.), (1., 1.)),
             ((w, h), (1., 0.)),
             ]
    testPairs(pairs)

    # Test mapToData with different axis values
    print "Testing xAxis values + 1."
    plotScene.x1 = 1.
    plotScene.x2 = 2.
    plotScene.y1 = 0.
    plotScene.y2 = 1.
    pairs = [((0., 0.), (1., 1.)),  # top left
             ((0., h), (1., 0.)),  # bottom left
             ((w, 0.), (2., 1.)),  # top right
             ((w, h), (2., 0.)),  # bottom right
             ]
    testPairs(pairs)

    # Test mapToData with different axis values
    print "Testing xAxis and yAxis values + 1."
    plotScene.x1 = 1.
    plotScene.x2 = 2.
    plotScene.y1 = 1.
    plotScene.y2 = 2.
    pairs = [((0., 0.), (1., 2.)),
             ((0., h), (1., 1.)),
             ((w, 0.), (2., 2.)),
             ((w, h), (2., 1.)),
             ]
    testPairs(pairs)

    # Test mapToData with different axis values
    print "Testing swapped xAxis values."
    plotScene.x1 = 1.
    plotScene.x2 = 0.
    plotScene.y1 = 0.
    plotScene.y2 = 1.
    pairs = [((0., 0.), (1., 1.)),  # top left
             ((0., h), (1., 0.)),  # bottom left
             ((w, 0.), (0., 1.)),  # top right
             ((w, h), (0., 0.)),  # bottom right
             ]
    testPairs(pairs)
    # Test mapToData with horizontal shear
    print "Testing horizontal shear."
    plotScene.xAxis.setLine(QtCore.QLineF(w, h, 2*w, h))
    plotScene.x1 = 0.
    plotScene.x2 = 1.
    plotScene.y1 = 0.
    plotScene.y2 = 1.
    # These values assume a square image:
    assert w == h
    pairs = [((0., 0.), (0., 1.)),  # top left of image
             ((0., h), (-1., 0.)),  # bottom left of image
             ((w, 0.), (1., 1.)),  # top right of image
             ((w, h), (0., 0.)),  # bottom right of image
             ]
    testPairs(pairs)
    #TODO: test vertical shear
    #TODO: test shear on rectangular image
    #TODO: fix the transform to pass all test cases

    #view.show()
    #view.raise_()
    #app.exec_()
