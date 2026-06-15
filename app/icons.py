"""Vector icons drawn with QPainter so no binary assets are needed."""
from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QIcon,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QPolygonF,
)

ACTIVE = "#3f4042"
DISABLED = "#c2c6cb"
WHITE = "#ffffff"


def _pix(size: int) -> QPixmap:
    pm = QPixmap(size, size)
    pm.fill(Qt.transparent)
    return pm


def _painter(pm: QPixmap) -> QPainter:
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing, True)
    return p


def _pen(p: QPainter, color: str, w: float = 2.0) -> None:
    pen = QPen(QColor(color))
    pen.setWidthF(w)
    pen.setCapStyle(Qt.RoundCap)
    pen.setJoinStyle(Qt.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.NoBrush)


def draw(name: str, color: str = ACTIVE, size: int = 28) -> QPixmap:
    pm = _pix(size)
    p = _painter(pm)
    s = size
    c = QColor(color)
    try:
        if name == "add_patient":
            # person on the right, plus sign on the left
            _pen(p, color, 2)
            p.drawEllipse(QRectF(s * 0.44, s * 0.12, s * 0.34, s * 0.34))
            path = QPainterPath()
            path.moveTo(s * 0.38, s * 0.86)
            path.cubicTo(s * 0.40, s * 0.58, s * 0.82, s * 0.58, s * 0.84, s * 0.86)
            p.drawPath(path)
            _pen(p, color, 2)
            p.drawLine(QPointF(s * 0.22, s * 0.32), QPointF(s * 0.22, s * 0.60))
            p.drawLine(QPointF(s * 0.08, s * 0.46), QPointF(s * 0.36, s * 0.46))
        elif name == "edit":
            _pen(p, color, 2)
            path = QPainterPath()
            path.moveTo(s * 0.20, s * 0.80)
            path.lineTo(s * 0.24, s * 0.62)
            path.lineTo(s * 0.64, s * 0.22)
            path.lineTo(s * 0.80, s * 0.38)
            path.lineTo(s * 0.40, s * 0.78)
            path.closeSubpath()
            p.drawPath(path)
            p.drawLine(QPointF(s * 0.58, s * 0.28), QPointF(s * 0.74, s * 0.44))
        elif name == "delete":
            _pen(p, color, 2)
            p.drawLine(QPointF(s * 0.22, s * 0.28), QPointF(s * 0.78, s * 0.28))
            p.drawLine(QPointF(s * 0.40, s * 0.28), QPointF(s * 0.43, s * 0.20))
            p.drawLine(QPointF(s * 0.43, s * 0.20), QPointF(s * 0.57, s * 0.20))
            p.drawLine(QPointF(s * 0.57, s * 0.20), QPointF(s * 0.60, s * 0.28))
            path = QPainterPath()
            path.moveTo(s * 0.28, s * 0.30)
            path.lineTo(s * 0.32, s * 0.82)
            path.lineTo(s * 0.68, s * 0.82)
            path.lineTo(s * 0.72, s * 0.30)
            p.drawPath(path)
            for x in (0.42, 0.50, 0.58):
                p.drawLine(QPointF(s * x, s * 0.38), QPointF(s * x, s * 0.74))
        elif name == "refresh":
            _pen(p, color, 2)
            rect = QRectF(s * 0.24, s * 0.24, s * 0.52, s * 0.52)
            p.drawArc(rect, 60 * 16, 250 * 16)
            # arrow head
            ah = QPolygonF([
                QPointF(s * 0.70, s * 0.20),
                QPointF(s * 0.80, s * 0.34),
                QPointF(s * 0.63, s * 0.34),
            ])
            p.setBrush(c)
            p.setPen(Qt.NoPen)
            p.drawPolygon(ah)
        elif name == "camera":
            _pen(p, color, 2)
            p.drawRoundedRect(QRectF(s * 0.14, s * 0.34, s * 0.72, s * 0.46), 4, 4)
            # viewfinder hump on top
            path = QPainterPath()
            path.moveTo(s * 0.34, s * 0.34)
            path.lineTo(s * 0.40, s * 0.24)
            path.lineTo(s * 0.54, s * 0.24)
            path.lineTo(s * 0.60, s * 0.34)
            p.drawPath(path)
            # lens
            p.drawEllipse(QRectF(s * 0.37, s * 0.44, s * 0.26, s * 0.26))
            p.drawEllipse(QRectF(s * 0.45, s * 0.52, s * 0.10, s * 0.10))
        elif name == "person":
            _pen(p, color, 2)
            p.setBrush(c)
            p.drawEllipse(QRectF(s * 0.34, s * 0.16, s * 0.32, s * 0.32))
            path = QPainterPath()
            path.moveTo(s * 0.18, s * 0.86)
            path.cubicTo(s * 0.20, s * 0.54, s * 0.80, s * 0.54, s * 0.82, s * 0.86)
            p.drawPath(path)
        elif name in ("import", "export"):
            _pen(p, color, 2)
            # tray
            p.drawLine(QPointF(s * 0.22, s * 0.78), QPointF(s * 0.78, s * 0.78))
            p.drawLine(QPointF(s * 0.22, s * 0.66), QPointF(s * 0.22, s * 0.78))
            p.drawLine(QPointF(s * 0.78, s * 0.66), QPointF(s * 0.78, s * 0.78))
            p.setBrush(c)
            p.setPen(QPen(c, 2))
            if name == "import":
                p.drawLine(QPointF(s * 0.5, s * 0.18), QPointF(s * 0.5, s * 0.58))
                head = QPolygonF([
                    QPointF(s * 0.38, s * 0.46),
                    QPointF(s * 0.62, s * 0.46),
                    QPointF(s * 0.5, s * 0.62),
                ])
            else:
                p.drawLine(QPointF(s * 0.5, s * 0.20), QPointF(s * 0.5, s * 0.60))
                head = QPolygonF([
                    QPointF(s * 0.38, s * 0.32),
                    QPointF(s * 0.62, s * 0.32),
                    QPointF(s * 0.5, s * 0.16),
                ])
            p.setPen(Qt.NoPen)
            p.drawPolygon(head)
        elif name == "convert":
            _pen(p, color, 2)
            p.drawArc(QRectF(s * 0.22, s * 0.22, s * 0.56, s * 0.56), 30 * 16, 140 * 16)
            p.drawArc(QRectF(s * 0.22, s * 0.22, s * 0.56, s * 0.56), 210 * 16, 140 * 16)
            p.setBrush(c)
            p.setPen(Qt.NoPen)
            p.drawPolygon(QPolygonF([
                QPointF(s * 0.20, s * 0.40), QPointF(s * 0.34, s * 0.40), QPointF(s * 0.27, s * 0.26)]))
            p.drawPolygon(QPolygonF([
                QPointF(s * 0.80, s * 0.60), QPointF(s * 0.66, s * 0.60), QPointF(s * 0.73, s * 0.74)]))
        elif name == "cest":
            _pen(p, color, 2)
            p.drawRoundedRect(QRectF(s * 0.20, s * 0.22, s * 0.60, s * 0.56), 4, 4)
            f = QFont("Arial", int(s * 0.22))
            f.setBold(True)
            p.setFont(f)
            p.setPen(QPen(c))
            p.drawText(QRectF(0, 0, s, s), Qt.AlignCenter, "C")
        elif name == "scan":
            # Flatbed scanner: outer body + glass platen lines + bright scan beam
            _pen(p, color, 2)
            p.drawRoundedRect(QRectF(s * 0.14, s * 0.24, s * 0.72, s * 0.52), 4, 4)
            # two faint boundary lines (top and bottom of scan area)
            _pen(p, color, 1.5)
            p.drawLine(QPointF(s * 0.22, s * 0.37), QPointF(s * 0.78, s * 0.37))
            p.drawLine(QPointF(s * 0.22, s * 0.63), QPointF(s * 0.78, s * 0.63))
            # bright central scan beam
            _pen(p, color, 2.5)
            p.drawLine(QPointF(s * 0.22, s * 0.50), QPointF(s * 0.78, s * 0.50))
        elif name == "gear":
            _pen(p, color, 1.6)
            p.setBrush(Qt.NoBrush)
            cx, cy, r = s * 0.5, s * 0.5, s * 0.26
            import math
            path = QPainterPath()
            teeth = 8
            for i in range(teeth * 2):
                ang = math.pi * i / teeth
                rr = r if i % 2 == 0 else r * 0.78
                x = cx + rr * math.cos(ang)
                y = cy + rr * math.sin(ang)
                if i == 0:
                    path.moveTo(x, y)
                else:
                    path.lineTo(x, y)
            path.closeSubpath()
            p.drawPath(path)
            p.drawEllipse(QPointF(cx, cy), r * 0.4, r * 0.4)
        elif name == "tab":
            _pen(p, color, 1.8)
            p.setBrush(QColor(color))
            path = QPainterPath()
            path.moveTo(s * 0.32, s * 0.18)
            path.lineTo(s * 0.68, s * 0.18)
            path.lineTo(s * 0.68, s * 0.82)
            path.lineTo(s * 0.50, s * 0.68)
            path.lineTo(s * 0.32, s * 0.82)
            path.closeSubpath()
            p.drawPath(path)
        elif name == "min":
            _pen(p, color, 1.4)
            p.drawLine(QPointF(s * 0.30, s * 0.55), QPointF(s * 0.70, s * 0.55))
        elif name == "max":
            _pen(p, color, 1.4)
            p.drawRect(QRectF(s * 0.32, s * 0.32, s * 0.36, s * 0.36))
        elif name == "restore":
            _pen(p, color, 1.4)
            p.drawRect(QRectF(s * 0.30, s * 0.36, s * 0.30, s * 0.30))
            p.drawRect(QRectF(s * 0.40, s * 0.26, s * 0.30, s * 0.30))
        elif name == "close":
            _pen(p, color, 1.4)
            p.drawLine(QPointF(s * 0.32, s * 0.32), QPointF(s * 0.68, s * 0.68))
            p.drawLine(QPointF(s * 0.68, s * 0.32), QPointF(s * 0.32, s * 0.68))
        elif name == "grid":
            p.setBrush(c)
            p.setPen(Qt.NoPen)
            g = s * 0.16
            for gx in (0.24, 0.46, 0.68):
                for gy in (0.24, 0.46, 0.68):
                    p.drawRect(QRectF(s * gx, s * gy, g, g))
        elif name == "list":
            _pen(p, color, 2)
            for gy in (0.30, 0.50, 0.70):
                p.drawLine(QPointF(s * 0.42, s * gy), QPointF(s * 0.78, s * gy))
                p.setBrush(c)
                p.setPen(Qt.NoPen)
                p.drawEllipse(QRectF(s * 0.24, s * gy - s * 0.03, s * 0.06, s * 0.06))
                _pen(p, color, 2)
        elif name == "male":
            _pen(p, "#2f6fb0", 2)
            p.drawEllipse(QRectF(s * 0.20, s * 0.38, s * 0.34, s * 0.34))
            p.drawLine(QPointF(s * 0.52, s * 0.40), QPointF(s * 0.80, s * 0.18))
            p.drawLine(QPointF(s * 0.62, s * 0.18), QPointF(s * 0.80, s * 0.18))
            p.drawLine(QPointF(s * 0.80, s * 0.18), QPointF(s * 0.80, s * 0.36))
        elif name == "female":
            _pen(p, "#d2691e", 2)
            p.drawEllipse(QRectF(s * 0.30, s * 0.16, s * 0.34, s * 0.34))
            p.drawLine(QPointF(s * 0.47, s * 0.50), QPointF(s * 0.47, s * 0.82))
            p.drawLine(QPointF(s * 0.34, s * 0.68), QPointF(s * 0.60, s * 0.68))
        elif name == "link":
            _pen(p, color, 2)
            p.drawRoundedRect(QRectF(s * 0.20, s * 0.42, s * 0.30, s * 0.20), 8, 8)
            p.drawRoundedRect(QRectF(s * 0.50, s * 0.38, s * 0.30, s * 0.20), 8, 8)
            p.drawLine(QPointF(s * 0.40, s * 0.52), QPointF(s * 0.60, s * 0.50))
        elif name == "globe":
            _pen(p, color, 2)
            p.drawEllipse(QRectF(s * 0.16, s * 0.16, s * 0.68, s * 0.68))
            # meridian (vertical ellipse) + equator
            p.drawEllipse(QRectF(s * 0.38, s * 0.16, s * 0.24, s * 0.68))
            p.drawLine(QPointF(s * 0.16, s * 0.50), QPointF(s * 0.84, s * 0.50))
            # two latitude lines (shorter than the equator)
            p.drawLine(QPointF(s * 0.27, s * 0.34), QPointF(s * 0.73, s * 0.34))
            p.drawLine(QPointF(s * 0.27, s * 0.66), QPointF(s * 0.73, s * 0.66))
        elif name == "lock":
            _pen(p, color, 2)
            # shackle (upper half arc)
            p.drawArc(QRectF(s * 0.33, s * 0.20, s * 0.34, s * 0.42), 0, 180 * 16)
            # body
            p.drawRoundedRect(QRectF(s * 0.27, s * 0.46, s * 0.46, s * 0.34), 4, 4)
            # keyhole
            p.setBrush(c)
            p.setPen(QPen(c, 1))
            p.drawEllipse(QRectF(s * 0.455, s * 0.55, s * 0.09, s * 0.09))
            _pen(p, color, 2)
            p.drawLine(QPointF(s * 0.50, s * 0.61), QPointF(s * 0.50, s * 0.71))
        elif name == "user_caret":
            _pen(p, color, 2)
            p.setBrush(c)
            p.drawEllipse(QRectF(s * 0.22, s * 0.16, s * 0.26, s * 0.26))
            path = QPainterPath()
            path.moveTo(s * 0.12, s * 0.80)
            path.cubicTo(s * 0.14, s * 0.50, s * 0.56, s * 0.50, s * 0.58, s * 0.80)
            p.drawPath(path)
            # dropdown caret to the right of the figure
            p.setBrush(c)
            p.setPen(Qt.NoPen)
            p.drawPolygon(QPolygonF([
                QPointF(s * 0.66, s * 0.44),
                QPointF(s * 0.88, s * 0.44),
                QPointF(s * 0.77, s * 0.58),
            ]))
        elif name == "arrow_left":
            _pen(p, color, 2)
            p.drawLine(QPointF(s * 0.60, s * 0.28), QPointF(s * 0.38, s * 0.50))
            p.drawLine(QPointF(s * 0.38, s * 0.50), QPointF(s * 0.60, s * 0.72))
        elif name == "arrow_right":
            _pen(p, color, 2)
            p.drawLine(QPointF(s * 0.40, s * 0.28), QPointF(s * 0.62, s * 0.50))
            p.drawLine(QPointF(s * 0.62, s * 0.50), QPointF(s * 0.40, s * 0.72))
    finally:
        p.end()
    return pm


def icon(name: str, color: str = ACTIVE, size: int = 28) -> QIcon:
    return QIcon(draw(name, color, size))


def star_pixmap(filled: bool, size: int = 14, color: str = "#f0a020",
                empty_color: str = "#808080") -> QPixmap:
    pm = _pix(size)
    p = _painter(pm)
    import math
    cx = cy = size / 2
    r_out = size * 0.46
    r_in = size * 0.2
    poly = QPolygonF()
    for i in range(10):
        ang = -math.pi / 2 + math.pi * i / 5
        r = r_out if i % 2 == 0 else r_in
        poly.append(QPointF(cx + r * math.cos(ang), cy + r * math.sin(ang)))
    if filled:
        p.setBrush(QColor(color))
        p.setPen(QPen(QColor(color), 1))
    else:
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(QColor(empty_color), 1.2))
    p.drawPolygon(poly)
    p.end()
    return pm
