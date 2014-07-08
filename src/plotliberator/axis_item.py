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
from movable_items import MovableLineItem, MovableCursorItem


class AxesItem(MovableLineItem):

    def __init__(self, line, parent=None, scene=None):
        super(AxesItem, self).__init__(line, parent, scene)

        self.startItem = MovableCursorItem(self.line().p1(),
                                      style='Circle',
                                      parent=parent,
                                      scene=scene)
        self.startItem.posChanged.connect(self.setP1)
        self.endItem = MovableCursorItem(self.line().p2(),
                                          parent=parent,
                                          scene=scene)
        self.endItem.posChanged.connect(self.setP2)
        self.p1Changed.connect(self.startItem.setPos)
        self.p2Changed.connect(self.endItem.setPos)

    def setPen(self, pen):
        super(AxesItem, self).setPen(pen)
        pen2 = QtGui.QPen(pen)
        pen2.setStyle(Qt.SolidLine)
        self.startItem.setPen(pen2)
        self.endItem.setPen(pen2)

    def setZValue(self, z):
        super(AxesItem, self).setZValue(z)
        self.startItem.setZValue(z)
        self.endItem.setZValue(z)


if __name__ == '__main__':
    app = QtGui.QApplication([])
    scene = QtGui.QGraphicsScene()
    view = QtGui.QGraphicsView(scene)
    line = QtCore.QLineF(0, 0, 100, 100)
    axisItem = AxesItem(line, scene=scene)
    axisItem.setPen(QtGui.QPen(Qt.red, 1., Qt.DashLine))
    view.show()
    view.raise_()
    app.exec_()