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


def searchsorted(a, v):
    for i, c in enumerate(a):
        if v < c:
            return i - 1
    else:
        return i


class ZoomableGraphicsView(QtGui.QGraphicsView):
    '''
    A subclass of QGraphicsView that supports:
        Zooming
            zoomIn, ZoomOut, and actualSize slots
            Control + Mouse Wheel
            Pinch gesture
    '''
    plotItem = None
    zoomLevels = [0.1, 0.125, 0.15, 0.2, 0.25,
                  0.3,   0.4,  0.5, 0.6,  0.8, 1.,
                 1.25,   1.5,   2., 2.5,   3.,
                   4.,    5.,   6.,  7.,   9.]
    numZoomLevels = len(zoomLevels)

    def __init__(self, scene=None, parent=None):
        if scene is None:
            super(ZoomableGraphicsView, self).__init__(parent)
        else:
            super(ZoomableGraphicsView, self).__init__(scene, parent)

        # Enable pinch to zoom
        self.grabGesture(Qt.PinchGesture)

    def getZoom(self):
        '''Returns the current zoom as a float value'''
        return self.transform().m11()  # assume m11 == m22

    def setZoom(self, zoom):
        '''Sets the zoom to the given float value'''
        self.setTransform(QtGui.QTransform.fromScale(zoom, zoom))

    def gentleZoom(self, factor, pos):
        if isinstance(pos, QtCore.QPointF):
            targetViewportPos = pos
            targetScenePos = QtCore.QPointF(self.mapToScene(pos.toPoint()))
        else:  # assume isinstance(pos, QtCore.QPoint)
            targetViewportPos = QtCore.QPointF(pos)
            targetScenePos = QtCore.QPointF(self.mapToScene(pos))

        # First, perform the zoom
        self.scale(factor, factor)

        # Next, move the scene, so that the zoom is centered on the mouse
        self.centerOn(targetScenePos)
        deltaViewportPos = (targetViewportPos -
                            QtCore.QPointF(self.viewport().width() / 2.,
                                           self.viewport().height() / 2.))
        newTargetViewportPos = QtCore.QPointF(
                                        self.mapFromScene(targetScenePos))
        viewport_center = (newTargetViewportPos - deltaViewportPos)
        self.centerOn(self.mapToScene(viewport_center.toPoint()))

    def event(self, event):
        if event.type() == event.Gesture:
            # Dispatch gesture events
            return self.gestureEvent(event)
        else:
            return super(ZoomableGraphicsView, self).event(event)

    def wheelEvent(self, event):
        if QtGui.QApplication.keyboardModifiers() == Qt.ControlModifier:
            # Control + mouse wheel zooming
            if event.orientation() == Qt.Vertical:
                angle = event.delta()
                factor = 1.0015 ** angle
                self.gentleZoom(factor, event.pos())
            return True  # don't scroll if control is held
        return super(ZoomableGraphicsView, self).wheelEvent(event)

    def gestureEvent(self, event):
        # pinch zooming
        pinchGesture = event.gesture(Qt.PinchGesture)
        factor = pinchGesture.scaleFactor() / pinchGesture.lastScaleFactor()
        pos = pinchGesture.centerPoint()
        self.gentleZoom(factor, pos)
        return True

    @QtCore.Slot()
    def actualSize(self):
        '''Resets the zoom to 1.'''
        self.setZoom(1.)

    @QtCore.Slot()
    def zoomIn(self):
        i = searchsorted(self.zoomLevels, self.getZoom())
        i = min(i + 1, self.numZoomLevels - 1)
        self.setZoom(self.zoomLevels[i])

    @QtCore.Slot()
    def zoomOut(self):
        i = searchsorted(self.zoomLevels, self.getZoom())
        i = max(i - 1, 0)
        self.setZoom(self.zoomLevels[i])


class PlotView(ZoomableGraphicsView):
    '''
    A subclass of ZoomableGraphicsView that creates and updates a statusBar
    widget with the PlotScene's data coordinates.
    '''
    dataCoordLabel = None

    def __init__(self, scene=None, parent=None):
        super(PlotView, self).__init__(scene, parent)
        self.dataCoordLabel = QtGui.QLabel('No position')
#         self.parent().statusBar().addWidget(self.dataCoordLabel)
        self.parent().statusBar().addPermanentWidget(self.dataCoordLabel)

    def event(self, event):
        if event.type() == event.Leave:
            if self.dataCoordLabel is not None:
                self.dataCoordLabel.setText('No position')
#                 self.dataCoordLabel.hide()
        return super(PlotView, self).event(event)

    def mouseMoveEvent(self, event):
        # Update dataCoordLabel
        p = self.mapToScene(event.pos())
        x = p.x()
        y = p.y()
        xd, yd = self.scene().mapToData(x, y)
        self.dataCoordLabel.setText('x={:.4g}, y={:.4g}'.format(xd, yd))

        # Then use QGraphicsView's event handler
        super(PlotView, self).mouseMoveEvent(event)
