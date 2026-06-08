"""A header that positions each child at a fixed percentage of its width.

Children keep their natural size; only their horizontal center moves with the
window width, so the relative layout stays cohesive (proportional) at any size.
The widget can also report the minimum width at which no two children overlap.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget


class PercentHeader(QWidget):
    def __init__(self, height: int = 72, item_height: int = 50, parent=None):
        super().__init__(parent)
        # QSS backgrounds (#Toolbar) are only painted on QWidget subclasses
        # when this attribute is set.
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setFixedHeight(height)
        self._item_h = item_height
        self._items: list[tuple[QWidget, float]] = []

    def add(self, widget: QWidget, pct: float) -> QWidget:
        widget.setParent(self)
        widget.setFixedHeight(self._item_h)
        widget.ensurePolished()
        widget.adjustSize()
        widget.show()
        self._items.append((widget, pct))
        return widget

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._reposition()

    def showEvent(self, e):
        super().showEvent(e)
        self._reposition()

    def _reposition(self):
        w = self.width()
        h = self.height()
        y = (h - self._item_h) // 2
        for widget, pct in self._items:
            sw = widget.sizeHint().width()
            x = int(round(pct * w - sw / 2))
            x = max(0, x)
            widget.setGeometry(x, y, sw, self._item_h)

    def minimum_width(self, min_gap: int = 6) -> int:
        items = self._items
        if not items:
            return 0
        req = 0.0
        for i in range(len(items) - 1):
            w1, p1 = items[i]
            w2, p2 = items[i + 1]
            dp = p2 - p1
            if dp <= 0:
                continue
            need = (w1.sizeHint().width() / 2 + w2.sizeHint().width() / 2 + min_gap) / dp
            req = max(req, need)
        first_w, first_p = items[0]
        if first_p > 0:
            req = max(req, (first_w.sizeHint().width() / 2) / first_p)
        last_w, last_p = items[-1]
        if last_p < 1:
            req = max(req, (last_w.sizeHint().width() / 2) / (1 - last_p))
        return int(req) + 6
