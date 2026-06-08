"""List (table) view of profiles, matching the light list screenshot."""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QToolButton,
    QWidget,
    QVBoxLayout,
)

from app import icons
from app.util import format_date
from app.widgets.stars import StarRating

HEADERS = ["", "姓名", "就诊编号", "胶囊编号", "检查日期", "性别", "年龄",
           "申请人员", "当前状态", "星级", "操作"]

# column -> sort key (None = not sortable)
SORT_KEYS = {1: "name", 2: "visit_no", 3: "capsule_no", 4: "exam_date",
             5: "gender", 6: "age", 7: "applicant", 8: "status", 9: "rating"}

ROW_WHITE = "#ffffff"
ROW_GREY = "#e0e0e0"
SEL_ORANGE = "#ffcb97"
CLICK_ORANGE = "#ffe2c6"
CHECK_BG = "#cfe0f3"
TEXT = "#2b2b2b"


class ListView(QWidget):
    selection_changed = Signal()
    edit_requested = Signal(int)
    rating_changed = Signal(int, int)
    sort_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._profiles: list[dict] = []
        self._scale = 1.0
        self._current_row = 0
        self._user_clicked = False

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        self.table = QTableWidget()
        self.table.setColumnCount(len(HEADERS))
        self.table.setHorizontalHeaderLabels(HEADERS)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionMode(QAbstractItemView.NoSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.setShowGrid(True)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.cellClicked.connect(self._on_cell_clicked)
        self.table.horizontalHeader().sectionClicked.connect(self._on_header_clicked)
        lay.addWidget(self.table)
        self._apply_style()

    def _apply_style(self):
        # NOTE: deliberately no `QTableWidget::item` rule -- styling that
        # subcontrol would disable per-item setBackground() used for row colors.
        self.table.setStyleSheet(
            """
            QTableWidget { background:#ffffff; color:#2b2b2b; gridline-color:#cfcfcf;
                           border:none; outline:0; }
            QHeaderView::section { background:#b8b8b8; color:#333333; border:none;
                                   border-right:1px solid #a8a8a8; padding:6px; }
            """
        )

    # ---------- data ----------
    def set_profiles(self, profiles: list[dict]):
        self._profiles = profiles
        self._current_row = 0
        self._user_clicked = False
        self._rebuild()

    def set_scale(self, scale: float):
        self._scale = scale
        self._rebuild()

    def checked_ids(self) -> list[int]:
        ids = []
        for r in range(self.table.rowCount()):
            cb = self.table.cellWidget(r, 0)
            box = cb.findChild(QCheckBox) if cb else None
            if box and box.isChecked():
                ids.append(self._profiles[r]["id"])
        return ids

    # ---------- build ----------
    def _holder(self, widget=None, left=0):
        # Transparent holder: the row color is painted by the cell's item
        # background and shows through, so only glyphs/icons appear on top.
        holder = QWidget()
        holder.setStyleSheet("background: transparent;")
        hb = QHBoxLayout(holder)
        hb.setContentsMargins(left, 0, 0, 0)
        if left:
            hb.setAlignment(Qt.AlignVCenter)
        else:
            hb.setAlignment(Qt.AlignCenter)
        if widget is not None:
            hb.addWidget(widget)
            if left:
                hb.addStretch(1)
        return holder

    def _rebuild(self):
        self.table.setRowCount(0)
        row_h = int(28 * self._scale)
        font_px = max(11, int(12 * self._scale))
        self._apply_style()
        self.table.setStyleSheet(
            self.table.styleSheet() + f"\nQTableWidget{{font-size:{font_px}px;}}")
        self.table.setRowCount(len(self._profiles))
        star_px = max(12, int(14 * self._scale))
        for r, p in enumerate(self._profiles):
            self.table.setRowHeight(r, row_h)

            box = QCheckBox()
            box.stateChanged.connect(self._on_check)
            self.table.setCellWidget(r, 0, self._holder(box))

            self._set_text(r, 1, p.get("name", ""))
            self._set_text(r, 2, p.get("visit_no", ""))
            self._set_text(r, 3, p.get("capsule_no", ""))
            self._set_text(r, 4, format_date(p.get("exam_date")))

            g = p.get("gender", "")
            gname = "male" if g == "男" else ("female" if g == "女" else None)
            if gname:
                lbl = QLabel()
                lbl.setPixmap(icons.draw(gname, size=int(20 * self._scale)))
                self.table.setCellWidget(r, 5, self._holder(lbl))
            else:
                self.table.setCellWidget(r, 5, self._holder())

            self._set_text(r, 6, p.get("age", ""))
            self._set_text(r, 7, p.get("applicant", ""))

            status = QLabel("<span style='color:#e8743b'>\u25cf</span> 分配设备")
            self.table.setCellWidget(r, 8, self._holder(status, left=8))

            stars = StarRating(p.get("rating", 0), star_size=star_px, interactive=True)
            stars.changed.connect(
                lambda v, pid=p["id"]: self.rating_changed.emit(pid, v))
            self.table.setCellWidget(r, 9, self._holder(stars, left=8))

            link = QToolButton()
            link.setObjectName("ViewBtn")
            link.setIcon(icons.icon("link", "#2f6fb0", int(20 * self._scale)))
            link.setCursor(Qt.PointingHandCursor)
            link.clicked.connect(lambda _=False, pid=p["id"]: self.edit_requested.emit(pid))
            self.table.setCellWidget(r, 10, self._holder(link))

        self._resize_columns()
        self._repaint_rows()

    def _set_text(self, r, c, text):
        item = QTableWidgetItem(str(text))
        item.setForeground(QColor(TEXT))
        self.table.setItem(r, c, item)

    def _resize_columns(self):
        header = self.table.horizontalHeader()
        s = self._scale
        star_w = 5 * max(12, int(14 * s)) + 24
        if s <= 1.0:
            fixed = {0: 38, 5: 64, 6: 60, 9: star_w, 10: 64}
            for c in range(self.table.columnCount()):
                if c in fixed:
                    header.setSectionResizeMode(c, QHeaderView.Fixed)
                    self.table.setColumnWidth(c, fixed[c])
                else:
                    header.setSectionResizeMode(c, QHeaderView.Stretch)
        else:
            header.setSectionResizeMode(QHeaderView.Interactive)
            widths = {0: 38, 1: int(150 * s), 2: int(120 * s), 3: int(120 * s),
                      4: int(110 * s), 5: 64, 6: 60, 7: int(140 * s),
                      8: int(120 * s), 9: star_w, 10: 64}
            for c, w in widths.items():
                self.table.setColumnWidth(c, w)

    # ---------- interaction ----------
    def _on_cell_clicked(self, row, col):
        if col == 0:
            return
        self._current_row = row
        self._user_clicked = True
        self._repaint_rows()

    def _on_header_clicked(self, idx):
        key = SORT_KEYS.get(idx)
        if key:
            self.sort_requested.emit(key)

    def _on_check(self):
        self.selection_changed.emit()
        self._repaint_rows()

    def _repaint_rows(self):
        checked = set()
        for r in range(self.table.rowCount()):
            holder = self.table.cellWidget(r, 0)
            box = holder.findChild(QCheckBox) if holder else None
            if box and box.isChecked():
                checked.add(r)
        for r in range(self.table.rowCount()):
            if r == self._current_row:
                bg = CLICK_ORANGE if self._user_clicked else SEL_ORANGE
            elif r in checked:
                bg = CHECK_BG
            else:
                bg = ROW_WHITE if r % 2 == 0 else ROW_GREY
            color = QColor(bg)
            # Every column (including widget cells) gets a background item so the
            # whole row is one uniform color behind the transparent holders.
            for c in range(self.table.columnCount()):
                item = self.table.item(r, c)
                if item is None:
                    item = QTableWidgetItem("")
                    item.setFlags(Qt.ItemIsEnabled)
                    self.table.setItem(r, c, item)
                item.setBackground(color)
