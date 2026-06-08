"""A small 5-star rating widget."""
from __future__ import annotations

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QWidget

from app import icons


class StarRating(QWidget):
    changed = Signal(int)

    def __init__(self, value: int = 0, star_size: int = 14, interactive: bool = True,
                 fill_color: str = "#f0a020", hover_color: str | None = None,
                 empty_color: str = "#808080", active_empty_color: str | None = None,
                 parent=None):
        super().__init__(parent)
        self._value = value
        self._star = star_size
        self._interactive = interactive
        self._fill = fill_color
        self._hover_color = hover_color or fill_color
        self._empty = empty_color
        self._empty_active = active_empty_color or empty_color
        self.setMouseTracking(interactive)
        self._hover = 0

    def value(self) -> int:
        return self._value

    def setValue(self, v: int) -> None:
        v = max(0, min(5, int(v)))
        if v != self._value:
            self._value = v
            self.update()

    def setStarSize(self, px: int) -> None:
        self._star = px
        self.updateGeometry()
        self.update()

    def sizeHint(self) -> QSize:
        return QSize(self._star * 5, self._star)

    def _star_at(self, x: int) -> int:
        idx = int(x // self._star) + 1
        return max(0, min(5, idx))

    def mouseMoveEvent(self, e):
        if self._interactive:
            self._hover = self._star_at(e.position().x())
            self.update()

    def leaveEvent(self, e):
        self._hover = 0
        self.update()

    def mousePressEvent(self, e):
        if self._interactive and e.button() == Qt.LeftButton:
            n = self._star_at(e.position().x())
            if n == self._value:  # clicking the same star again clears it
                n = 0
            self.setValue(n)
            self.changed.emit(self._value)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        # When a value is set (active) the selected stars use the fill color;
        # otherwise a hover previews the count with the hover color.
        if self._value > 0:
            show, fill, empty = self._value, self._fill, self._empty_active
        else:
            show, fill, empty = self._hover, self._hover_color, self._empty
        y = max(0, (self.height() - self._star) // 2)
        for i in range(5):
            pm = icons.star_pixmap(i < show, self._star, fill, empty)
            p.drawPixmap(i * self._star, y, pm)
        p.end()
