"""A single profile card shown in the grid view."""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app import style
from app.widgets.stars import StarRating

# base (100% zoom) geometry, tuned to the original screenshot proportions
BASE_W = 158
HEADER_H = 26
FOOTER_H = 24
ROW_H = 22
N_ROWS = 5
BASE_H = HEADER_H + ROW_H * N_ROWS + FOOTER_H

ROW_LINE = "#c9c9c9"
LABEL_COLOR = "#8a8f95"


class ProfileCard(QFrame):
    clicked = Signal(int)
    rating_changed = Signal(int, int)

    def __init__(self, profile: dict, date_text: str, scale: float = 1.0,
                 selected: bool = False, parent=None):
        super().__init__(parent)
        self.profile = profile
        self._selected = selected
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self._lay = QVBoxLayout(self)
        self._lay.setContentsMargins(0, 0, 0, 0)
        self._lay.setSpacing(0)

        self.header = QLabel(str(profile.get("name", "")))
        self.header.setAlignment(Qt.AlignCenter)
        self.header.setWordWrap(False)

        # ---- body: each value sits in its own row with a separator line ----
        self.body = QFrame()
        self.body_lay = QVBoxLayout(self.body)
        self.body_lay.setContentsMargins(0, 0, 0, 0)
        self.body_lay.setSpacing(0)

        self.l_visit = QLabel(str(profile.get("visit_no", "")))
        self.l_date = QLabel(date_text)
        self.l_capsule = QLabel(str(profile.get("capsule_no", "")))
        self.l_extra = QLabel(str(profile.get("exam_item", "")))
        self._value_labels = [self.l_visit, self.l_date, self.l_capsule, self.l_extra]

        self.stars = StarRating(profile.get("rating", 0), star_size=14, interactive=True)
        self.stars.changed.connect(
            lambda v: self.rating_changed.emit(self.profile["id"], v))

        self._rows: list[QFrame] = []
        for content in (self.l_visit, self.l_date, self.l_capsule, self.stars, self.l_extra):
            self.body_lay.addWidget(self._make_row(content))

        self.footer = QLabel("分配设备")
        self.footer.setAlignment(Qt.AlignCenter)

        self._lay.addWidget(self.header)
        self._lay.addWidget(self.body, 1)
        self._lay.addWidget(self.footer)

        self._header_fs = 11
        self._value_fs = 11
        self.apply_scale(scale)

    def _make_row(self, content: QWidget) -> QFrame:
        row = QFrame()
        row.setObjectName("CardRow")
        hl = QHBoxLayout(row)
        hl.setContentsMargins(8, 0, 6, 0)
        hl.setSpacing(0)
        hl.addWidget(content)
        hl.addStretch(1)
        self._rows.append(row)
        return row

    def set_selected(self, sel: bool) -> None:
        if sel != self._selected:
            self._selected = sel
            self._restyle()

    def apply_scale(self, scale: float) -> None:
        self.setFixedSize(int(BASE_W * scale), int(BASE_H * scale))
        self.header.setFixedHeight(int(HEADER_H * scale))
        self.footer.setFixedHeight(int(FOOTER_H * scale))
        rh = max(18, int(ROW_H * scale))
        for row in self._rows:
            row.setFixedHeight(rh)
        self._header_fs = max(11, int(12 * scale))
        self._value_fs = max(10, int(11 * scale))
        self.stars.setStarSize(max(12, int(14 * scale)))
        self._restyle()

    def _restyle(self) -> None:
        header_bg = style.CARD_HEADER_SEL if self._selected else style.CARD_HEADER
        border = "2px solid #1f3a5f" if self._selected else "1px solid #b9b9b9"
        self.setStyleSheet(
            f"ProfileCard {{ background:{style.CARD_BODY}; border:{border}; }}"
        )
        self.header.setStyleSheet(
            f"font-size:{self._header_fs}px; font-weight:bold;"
            f"background:{header_bg}; color:#ffffff;"
        )
        self.body.setStyleSheet(f"background:{style.CARD_BODY};")
        for row in self._rows:
            row.setStyleSheet(
                f"QFrame#CardRow {{ background:{style.CARD_BODY};"
                f" border-bottom:1px solid {ROW_LINE}; }}"
            )
        for lb in self._value_labels:
            lb.setStyleSheet(
                f"background:transparent; color:{LABEL_COLOR};"
                f" font-size:{self._value_fs}px; border:none;"
            )
        self.footer.setStyleSheet(
            f"background:{style.CARD_FOOTER}; color:#555; font-size:{self._value_fs}px;"
        )

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.clicked.emit(self.profile["id"])
        super().mousePressEvent(e)
