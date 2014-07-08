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
from PySide.QtCore import Qt

# local imports
from axis_item import AxesItem
from movable_items import MovableCursorItem


class RightClickToRemoveFilter(QtCore.QObject):
    def __init__(self, plotItem):
        super(RightClickToRemoveFilter, self).__init__()
        self.plotItem = plotItem

    #TODO: get this working
    def eventFilter(self, obj, event):
        print 1,
        if (event.type() == event.MouseButtonPress and
            event.button() == Qt.RightButton):
            print 2,
            # Right click to remove data point
            if obj in self.plotItem.dataPointItems:
                self.plotItem.dataPointItems.remove(obj)
                obj.scene().removeItem(obj)
            return True  # don't propagate the right click any further
        return False  # propagate the event further


class PlotItem(QtGui.QGraphicsPixmapItem):

    dataPointItems = []
    x1 = 0.
    x2 = 1.
    y1 = 0.
    y2 = 1.

    def __init__(self, pixmap, parent=None, scene=None):
        super(PlotItem, self).__init__(pixmap, parent, scene)
        self.initAxes()

    def setXAxisStartValue(self, v):
        try:
            self.x1 = float(v)
        except ValueError:
            pass

    def setXAxisEndValue(self, v):
        try:
            self.x2 = float(v)
        except ValueError:
            pass

    def setYAxisStartValue(self, v):
        try:
            self.y1 = float(v)
        except ValueError:
            pass

    def setYAxisEndValue(self, v):
        try:
            self.y2 = float(v)
        except ValueError:
            pass

    #TODO: Move the axis, plotDataPoints, and mousePressEvent handling to
    # a custom scene? Or use an event filter to allow right click to remove.
    # Still might want to allow left click to add even when not clicking
    # on the pixmapItem.
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Left click to add data point
            dataPointItem = MovableCursorItem(event.pos(),
                                              style='CircleCross',
                                              parent=self)
            dataPointItem.setPen(QtGui.QPen(Qt.darkGreen, 1., Qt.SolidLine))
            filt = RightClickToRemoveFilter(plotItem=self)
            dataPointItem.installEventFilter(filt)
            self.dataPointItems.append(dataPointItem)
            event.accept()
        else:
            super(PlotItem, self).mousePressEvent(event)

    def boundingBox(self):
        rect = super(PlotItem, self).boundingBox()
        rect.unite(self.xAxis.boundingBox())
        rect.unite(self.yAxis.boundingBox())
        for item in self.dataPointItems:
            rect.unite(item.boundingBox())
        return rect

    def initAxes(self):
        w = self.pixmap().width()
        h = self.pixmap().height()
        xline = QtCore.QLineF(0, h, w, h)
        yline = QtCore.QLineF(0, h, 0, 0)
        self.xAxis = AxesItem(xline, parent=self)
        self.yAxis = AxesItem(yline, parent=self)
        self.xAxis.setPen(QtGui.QPen(Qt.red, 1., Qt.DashLine))
        self.yAxis.setPen(QtGui.QPen(Qt.blue, 1., Qt.DashLine))
        self.xAxis.setZValue(-1.)
        self.yAxis.setZValue(-1.)
        #TODO: Link origins of the two axis? Or make it an option?

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

        # Intersection of visible data axes with origin data axis
        xp0 = self.xAxis.line().pointAt(xd1x / (xd1x - xd2x))
        xp0x = xp0.x()
        yp0 = self.yAxis.line().pointAt(yd1y / (yd1y - yd2y))
        yp0y = yp0.y()

        # xp3: intersection with the xAxis of a line from the position origin
        # with the same angle as the yAxis. Related to dx.
        _interceptType, xp3 = self.xAxis.line().intersect(
                        QtCore.QLineF.fromPolar(1, self.yAxis.line().angle()))
        # yp3: intersection with the yAxis of a line from the position origin
        # with the same angle as the xAxis. Related to dy.
        _interceptType, yp3 = self.yAxis.line().intersect(
                        QtCore.QLineF.fromPolar(1, self.xAxis.line().angle()))
        # od: origin of the data axes
        od = xp3 + yp3

        # x scale
        if abs(xp2x - xp0x) > 1e-6:
            m11 = (xd2x) / (xp2x - xp0x)
        else:
            m11 = (xd1x) / (xp1x - xp0x)
        # y scale
        if abs(yp2y - yp0y) > 1e-6:
            m22 = (yd2y) / (yp2y - yp0y)
        else:
            m22 = (yd1y) / (yp1y - yp0y)

        # Horizontal shear (1 / slope of y axis)
        if abs(yp2y - yp1y) > 1e-6:
            m21 = m11 * (yp2x - yp1x) / (yp2y - yp1y)
        else:
            m21 = 0.

        # Vertical shear (slope of x axis)
        if abs(xp2x - xp1x) > 1e-6:
            m12 = m22 * (xp2y - xp1y) / (xp2x - xp1x)
        else:
            m12 = 0.

        #TODO: these only apply if the data origin is to the bottom right
        # of the position origin
        # xSign and ySign should be -1. when the data origin is to the
        # bottom right of the position origin.
        odAngle = QtCore.QLineF(QtCore.QPointF(0., 0.), od).angle()
        print odAngle
        assert odAngle >= 0.
        if odAngle <= 90.:  # Quadrant 1
            xSign = -1.
            ySign = 1.
        elif odAngle <= 180.:  # Quadrant 2
            xSign = 1.
            ySign = 1.
        elif odAngle <= 270.:  # Quadrant 3
            xSign = 1.
            ySign = -1.
        else:  # Quadrant 4
            xSign = -1.
            ySign = -1.
        dx = xSign * m11 * QtCore.QLineF(xp0, xp3).length()
        dy = ySign * m22 * QtCore.QLineF(yp0, yp3).length()

        t = QtGui.QTransform(m11, m12, m21, m22, dx, dy)
        return t

if __name__ == '__main__':
    app = QtGui.QApplication([])
    scene = QtGui.QGraphicsScene()
    view = QtGui.QGraphicsView(scene)
    image = QtGui.QImage('test/test.png')
    pixmap = QtGui.QPixmap.fromImage(image)
    plotItem = PlotItem(pixmap, scene=scene)
    h = plotItem.pixmap().height()
    w = plotItem.pixmap().width()
    pairs = [((0., 0.), (0., 1.)),
             ((0., h), (0., 0.)),
             ((w, 0.), (1., 1.)),
             ((w, h), (1., 0.)),
             ]
    for (xpos, ypos), (xdata, ydata) in pairs:
        x, y = plotItem.mapToData(xpos, ypos)
        if (abs(x - xdata) > 1e-6) or (abs(y - ydata) > 1e-6):
            print 'plotItem.mapToData({}, {}) == ({}, {}) != ({}, {})'.format(
                                            xpos, ypos, x, y, xdata, ydata)
        else:
            print 'plotItem.mapToData({}, {}) == ({}, {})'.format(
                                            xpos, ypos, xdata, ydata)

    # Test with different axis values
    plotItem.setXAxisStartValue(1.)
    plotItem.setXAxisEndValue(2.)
    plotItem.setYAxisStartValue(1.)
    plotItem.setYAxisEndValue(2.)
    h = plotItem.pixmap().height()
    w = plotItem.pixmap().width()
    pairs = [((0., 0.), (1., 2.)),
             ((0., h), (1., 1.)),
             ((w, 0.), (2., 2.)),
             ((w, h), (2., 1.)),
             ]
    for (xpos, ypos), (xdata, ydata) in pairs:
        x, y = plotItem.mapToData(xpos, ypos)
        if (abs(x - xdata) > 1e-6) or (abs(y - ydata) > 1e-6):
            print 'plotItem.mapToData({}, {}) == ({}, {}) != ({}, {})'.format(
                                            xpos, ypos, x, y, xdata, ydata)
        else:
            print 'plotItem.mapToData({}, {}) == ({}, {})'.format(
                                            xpos, ypos, xdata, ydata)
    #view.show()
    #view.raise_()
    #app.exec_()