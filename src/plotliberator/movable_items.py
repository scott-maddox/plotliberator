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


class MovableItemBase(QtGui.QGraphicsObject):

    _pen = Qt.NoPen
    posChanged = QtCore.Signal(QtCore.QPointF)

    def __init__(self, parent=None, scene=None):
        if parent is not None and scene is not None:
            raise ValueError("Either parent or scene must be None")
        super(MovableItemBase, self).__init__(parent)
        if scene is not None:
            scene.addItem(self)

        self.setAcceptHoverEvents(True)
        self.setAcceptTouchEvents(True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsScenePositionChanges)
        self.setCursor(Qt.CrossCursor)

    def pen(self):
        return self._pen

    def setPen(self, pen):
        self.prepareGeometryChange()
        self._pen = pen

    def itemChange(self, change, value):
        if change == QtGui.QGraphicsItem.ItemPositionHasChanged:
            self.posChanged.emit(value)
        return super(MovableItemBase, self).itemChange(change, value)


class MovablePointItem(MovableItemBase):

    def __init__(self, pos, parent=None, scene=None):
        super(MovablePointItem, self).__init__(parent, scene)
        self.setPos(pos)

    def x(self):
        return self.pos().x()

    def y(self):
        return self.pos().y()

    def boundingRect(self):
        if self.pen() is not Qt.NoPen:
            w = self.pen().widthF()
        else:
            w = 0.
        rect = QtCore.QRectF(-w / 2., -w / 2., w, w)
        return rect

    def paint(self, painter, option, widget=None):
        painter.setPen(self.pen())
        painter.drawPoint(0, 0)


class MovableCursorItem(MovableItemBase):

    size = 6.
    style = 'Cross'

    def __init__(self, pos, size=6., style='Cross', parent=None, scene=None):
        '''
        Parameters
        ----------
        size : float
            the size of the cursor
        style : str
            The cursor style ('Cross', 'Circle', or 'CircleCross')
        '''
        super(MovableCursorItem, self).__init__(parent, scene)
        self.setPos(pos)
        self.size = size
        self.style = style

    def rect(self):
        rect = QtCore.QRectF(-self.size / 2., -self.size / 2.,
                             self.size, self.size)
        return rect

    def boundingRect(self):
        rect = self.rect()
        if self.pen() is not Qt.NoPen:
            r = self.pen().widthF()
        else:
            r = 0.
        rect.adjust(-r, -r, r, r)
        return rect

    def paint(self, painter, option, widget=None):
        painter.setPen(self.pen())
        rect = self.rect()
        if self.style in ['Cross', 'CircleCross']:
            painter.drawLine(rect.topLeft(), rect.bottomRight())
            painter.drawLine(rect.bottomLeft(), rect.topRight())
        if self.style in ['Circle', 'CircleCross']:
            painter.drawEllipse(rect)


class MovableLineItem(MovableItemBase):

    p1Changed = QtCore.Signal(QtCore.QPointF)
    p2Changed = QtCore.Signal(QtCore.QPointF)

    _length = 0.

    def __init__(self, line, parent=None, scene=None):
        super(MovableLineItem, self).__init__(parent, scene)
        self._length = line.length()
        self.setRotation(-line.angle())
        self.setPos(line.p1())

    def line(self):
        '''
        Returns the item's line in parent coordinates. If the item has no
        parent, the line will be in scene coordinates.
        '''
        return QtCore.QLineF.fromPolar(self._length, -self.rotation()
                                       ).translated(self.pos())

    def setLine(self, line):
        '''
        Sets the item's line to be the given line in parent coordinates.
        If the item has no parent, the line should be in scene coordinates.
        Emits p1Changed and p2Changed.
        '''
        if self.line() == line:
            return
        self.prepareGeometryChange()
        self._length = line.length()
        self.setRotation(-line.angle())
        self.setPos(line.p1())
        self.p1Changed.emit(line.p1())
        self.p2Changed.emit(line.p2())

    def p1(self):
        '''
        Returns the start point of the item's line in parent coordinates.
        If the item has no parent, the point will be in scene coordinates.
        '''
        return self.pos()

    def setP1(self, p):
        '''
        Sets the start point of the item's line in parent coordinates.
        If the item has no parent, the point should be in scene coordinates.
        Emits p1Changed.
        '''
        line = self.line()
        if line.p1() == p:
            return
        self.prepareGeometryChange()
        line.setP1(p)
        self._length = line.length()
        self.setRotation(-line.angle())
        self.setPos(line.p1())
        self.p1Changed.emit(p)

    def p2(self):
        '''
        Returns the end point of the item's line in parent coordinates.
        If the item has no parent, the point will be in scene coordinates.
        '''
        return self.line().p2()

    def setP2(self, p):
        '''
        Sets the end point of the item's line in parent coordinates.
        If the item has no parent, the point should be in scene coordinates.
        Emits p2Changed.
        '''
        line = self.line()
        if line.p2() == p:
            return
        self.prepareGeometryChange()
        line.setP2(p)
        self._length = line.length()
        self.setRotation(-line.angle())
        self.p2Changed.emit(p)

    def boundingRect(self):
        # The angle of the line in local coordinates is always 0, so I just
        # make a box of the appropriate length and then expand it to contain
        # the pen width
        rect = QtCore.QRectF(0, 0, self._length, 0)
        if self.pen() is not Qt.NoPen:
            w = max(self.pen().widthF(), 2.5)
        else:
            w = 2.5
        rect.adjust(-w, -w, w, w)  # expand by w pixels
        return rect

    def paint(self, painter, option, widget=None):
        # The angle of the line in local coordinates is always 0, so I just
        # draw a line of the appropriate length
        painter.setPen(self.pen())
        painter.drawLine(0, 0, self._length, 0)

    def itemChange(self, change, value):
        if change == QtGui.QGraphicsItem.ItemPositionHasChanged:
            line = self.line()
            self.p1Changed.emit(line.p1())
            self.p2Changed.emit(line.p2())
        return super(MovableLineItem, self).itemChange(change, value)


if __name__ == '__main__':
    app = QtGui.QApplication([])
    scene = QtGui.QGraphicsScene()
    view = QtGui.QGraphicsView(scene)
    lineItem = MovableLineItem(QtCore.QLineF(0, 0, 0, 100), scene=scene)
    lineItem.setPen(QtGui.QPen(Qt.red, 1., Qt.DashLine))
    pointItem1 = MovableCursorItem(QtCore.QPointF(0, 0), scene=scene)
    pointItem1.setPen(QtGui.QPen(Qt.black, 1., Qt.SolidLine))
    pointItem1.posChanged.connect(lineItem.setP1)
    pointItem2 = MovableCursorItem(QtCore.QPointF(0, 100), scene=scene)
    pointItem2.setPen(QtGui.QPen(Qt.red, 1., Qt.SolidLine))
    pointItem2.posChanged.connect(lineItem.setP2)
    lineItem.p1Changed.connect(pointItem1.setPos)
    lineItem.p2Changed.connect(pointItem2.setPos)
    view.show()
    view.raise_()
    app.exec_()
