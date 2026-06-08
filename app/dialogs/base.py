"""Frameless dialog with a custom blue title header, matching the app look."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from app import icons


class FramelessDialog(QDialog):
    def __init__(self, title: str, parent=None, closable: bool = True):
        super().__init__(parent)
        self.setObjectName("Dialog")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setModal(True)
        self._drag = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(1, 1, 1, 1)
        outer.setSpacing(0)

        self.header = QWidget()
        self.header.setObjectName("DialogHeader")
        self.header.setAttribute(Qt.WA_StyledBackground, True)
        self.header.setFixedHeight(30)
        h = QHBoxLayout(self.header)
        h.setContentsMargins(10, 0, 6, 0)
        self.title_label = QLabel(title)
        h.addWidget(self.title_label)
        h.addStretch(1)
        if closable:
            close = QToolButton()
            close.setObjectName("TitleBtn")
            close.setIcon(icons.icon("close", "#ffffff", 24))
            close.clicked.connect(self.reject)
            h.addWidget(close)
        outer.addWidget(self.header)

        self.body = QWidget()
        outer.addWidget(self.body, 1)

    def _center_on(self, ref) -> None:
        if ref is None:
            return
        self.adjustSize()
        geo = ref.frameGeometry()
        x = geo.center().x() - self.width() // 2
        y = geo.center().y() - self.height() // 2
        self.move(max(0, x), max(0, y))

    # allow dragging via the header
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton and self.header.geometry().contains(e.position().toPoint()):
            self._drag = e.globalPosition().toPoint() - self.frameGeometry().topLeft()
            e.accept()

    def mouseMoveEvent(self, e):
        if self._drag is not None and e.buttons() & Qt.LeftButton:
            self.move(e.globalPosition().toPoint() - self._drag)
            e.accept()

    def mouseReleaseEvent(self, e):
        self._drag = None
