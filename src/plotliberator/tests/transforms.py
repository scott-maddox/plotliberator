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


if __name__ == '__main__':
    app = QtGui.QApplication([])
    scene = QtGui.QGraphicsScene()
    view = QtGui.QGraphicsView(scene)
    origin = QtGui.QGraphicsRectItem(-1, -1, 2, 2, scene=scene)
    item1 = QtGui.QGraphicsRectItem(-100, -100, 200, 200, scene=scene)
    item2 = QtGui.QGraphicsRectItem(-100, -100, 200, 200, scene=scene)
    item2.setPen(QtGui.QPen(Qt.blue, 1., Qt.SolidLine))

    # QTransform performs the following operations for affine matricies:
    # xd = m11 * xp + m21 * yp + dx
    # yd = m22 * yp + m12 * xp + dy
    # where
    # xd and yd are the x and y values in data coordinates,
    # xp and yp are the x and y values in position coordinates, and
    # m11, m21, m22, m12, dx, and dy are matrix components

    # Correspondance between matrix position and purpose:
    #    m11,    m12,   m13,    m21,    m22,   m23, m31, m32
    # hScale, vShear, hProj, hShear, vScale, vProj,  dx,  dy

    # Affine-only transform
    hScale = 1.  # zoom horizontal in
    vScale = 1.  # zoom vertical in
    hShear = 1.  # shear bottom to the right
    vShear = 0.  # shear right down
    dx = 0.  # translate right
    dy = 0.  # translate down
    t = QtGui.QTransform(hScale, vShear, hShear, vScale,  dx,  dy)
    # Full transform
#     hScale = 1.  # zoom horizontal in
#     vScale = 1.  # zoom vertical in
#     hShear = 0.  # shear bottom to the right
#     vShear = 0.  # shear right down
#     hProj = 0.  # applies horizontal perspective (rapid)
#     #             looks like pushing the right side into the screen
#     vProj = 0.  # applies vertical perspective (rapid)
#     #             looks like pushing the bottom into the screen
#     proj = 1.  # zoom out
#     dx = 0.  # translate right
#     dy = 0.  # translate down
#     t = QtGui.QTransform(hScale, vShear, hProj, hShear,
#                          vScale, vProj,  dx,  dy, proj)
    # Defaults:
#     hScale = 1.
#     vScale = 1.
#     hShear = 0.
#     vShear = 0.
#     hProj = 0.
#     vProj = 0.
#     proj = 1.
#     dx = 0.
#     dy = 0.
#     t = QtGui.QTransform(1, 0, 0, 0, 1, 0, 0, 0, 1)
#     t = QtGui.QTransform(hScale, vShear, hProj, hShear,
#                          vScale, vProj,  dx,  dy, proj)
    item2.setTransform(t)
    view.resize(400, 400)
    view.show()
    view.raise_()
    app.exec_()