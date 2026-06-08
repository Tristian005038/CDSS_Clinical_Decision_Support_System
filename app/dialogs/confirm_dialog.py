"""Reusable yes/no confirmation popup (是 / 否)."""
from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from app.dialogs.base import FramelessDialog


class ConfirmDialog(FramelessDialog):
    def __init__(self, message: str, title: str = "提示", parent=None):
        super().__init__(title, parent)
        lay = QVBoxLayout(self.body)
        lay.setContentsMargins(24, 22, 24, 18)
        lay.setSpacing(18)

        label = QLabel(message)
        label.setWordWrap(True)
        lay.addWidget(label)

        row = QHBoxLayout()
        row.addStretch(1)
        yes = QPushButton("是")
        no = QPushButton("否")
        for b in (yes, no):
            b.setProperty("class", "primary")
            b.setFixedWidth(80)
        yes.clicked.connect(self.accept)
        no.clicked.connect(self.reject)
        row.addWidget(yes)
        row.addWidget(no)
        row.addStretch(1)
        lay.addLayout(row)

        self.setMinimumWidth(300)

    @staticmethod
    def ask(parent, message: str, title: str = "提示") -> bool:
        dlg = ConfirmDialog(message, title, parent)
        return dlg.exec() == FramelessDialog.Accepted
