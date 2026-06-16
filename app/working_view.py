"""The working tab: toolbar, grid/list area, and the two footer bars."""
from __future__ import annotations

import math

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSlider,
    QStackedWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from app import icons, style
from app.dialogs.confirm_dialog import ConfirmDialog
from app.dialogs.profile_dialog import ProfileDialog
from app.state import state
from app.util import format_date, human_size
from app.widgets.flow_layout import FlowLayout
from app.widgets.list_view import ListView
from app.widgets.percent_header import PercentHeader
from app.widgets.profile_card import ProfileCard
from app.widgets.stars import StarRating


# 50 % scale-up from the original 26/34/9 px values
_ICON_SZ = 39   # icon pixmap size  (26 * 1.5)
_BTN_SZ  = 51   # QToolButton fixed size (34 * 1.5)
_LBL_PX  = 14   # caption font size in px (9 * 1.5 → 13.5 → 14)


class HeaderIconButton(QWidget):
    """An icon button with a caption below it.

    The hover frame wraps only the icon (not the caption text).
    """

    def __init__(self, name, text, enabled=True, parent=None):
        super().__init__(parent)
        self.name = name
        v = QVBoxLayout(self)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(2)
        self.button = QToolButton()
        self.button.setObjectName("IconBtn")
        self.button.setIconSize(QSize(_ICON_SZ, _ICON_SZ))
        self.button.setFixedSize(_BTN_SZ, _BTN_SZ)
        self.text_label = QLabel(text)
        self.text_label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        v.addWidget(self.button, 0, Qt.AlignHCenter)
        v.addWidget(self.text_label, 0, Qt.AlignHCenter)
        self.clicked = self.button.clicked
        self.set_enabled_state(enabled)

    def set_enabled_state(self, enabled):
        color = style.ACTIVE_ICON if enabled else style.DISABLED_ICON
        self.button.setIcon(icons.icon(self.name, color, _ICON_SZ))
        self.button.setEnabled(enabled)
        self.button.setCursor(Qt.PointingHandCursor if enabled else Qt.ArrowCursor)
        self.text_label.setStyleSheet(
            f'font-family:"SimHei","黑体"; font-size:{_LBL_PX}px; font-weight:bold;'
            f" color:{'#4a4a4a' if enabled else '#b6babf'};")


class WorkingView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.zoom = 1.0
        self.per_page = 50
        self.page = 1
        self.view_mode = "grid"
        self.star_filter = 0
        self.sort_key = None
        self.sort_desc = False

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_toolbar())
        root.addWidget(self._build_center(), 1)
        root.addWidget(self._build_grey_footer())
        root.addWidget(self._build_blue_footer())

        state.profiles_changed.connect(self.refresh)
        state.selection_changed.connect(self._update_selection_ui)
        state.settings_changed.connect(self.refresh)

        self.refresh()

    # ---------------- toolbar ----------------
    def _build_toolbar(self):
        # item_height = button(51) + spacing(2) + label(~18) = 71 → use 74 for breathing room
        bar = PercentHeader(height=90, item_height=74)
        bar.setObjectName("Toolbar")

        self.btn_create = HeaderIconButton("add_patient", "新增患者", True)
        self.btn_edit = HeaderIconButton("edit", "编辑", False)
        self.btn_delete = HeaderIconButton("delete", "删除", False)
        self.btn_live = HeaderIconButton("camera", "实时查看", True)
        self.btn_create.clicked.connect(self.create_profile)
        self.btn_edit.clicked.connect(self.edit_selected)
        self.btn_delete.clicked.connect(self.delete_selected)

        # [按日期查询 / 查询]
        date_pair = self._pair(QLabel("按日期查询"), self._mini_button("查询", "flatbtn"))

        # [请选择 dropdown / search]
        self.filter_combo = QComboBox()
        self.filter_combo.setObjectName("FilterCombo")
        self.filter_combo.addItems(["请选择", "按姓名", "按编号"])
        self.filter_combo.setFixedSize(159, 33)
        self.filter_combo.setStyleSheet(
            f'font-family:"SimHei","黑体"; font-size:{_LBL_PX}px; font-weight:bold;')
        self.search = QLineEdit()
        self.search.setObjectName("SearchBox")
        self.search.setFixedSize(159, 33)
        self.search.setStyleSheet(
            f'font-family:"SimHei","黑体"; font-size:{_LBL_PX}px; font-weight:bold;')
        self.search.textChanged.connect(self._on_search)
        ds_pair = self._pair(self.filter_combo, self.search, center=False)

        # [按评分查询 / 合计]
        self.total_label = QLabel("合计: 1")
        rating_pair = self._pair(QLabel("按评分查询"), self.total_label, center=False)

        # [stars frame / 清除所有]
        self.star_filter_stars = StarRating(
            0, 20, interactive=True,
            fill_color="#ffffff", hover_color="#3a3a3a",
            empty_color="#808080", active_empty_color="#ffffff")
        self.star_filter_stars.setFixedSize(20 * 5, 20)
        self.star_filter_stars.changed.connect(self._on_star_filter)
        self.star_frame = QFrame()
        self.star_frame.setObjectName("StarFilterFrame")
        sfl = QHBoxLayout(self.star_frame)
        sfl.setContentsMargins(3, 3, 3, 3)
        sfl.addWidget(self.star_filter_stars)
        self._update_star_frame()
        self.btn_clear = self._mini_button("清除所有", "clearbtn")
        self.btn_clear.clicked.connect(self._clear_all)
        sc_pair = self._pair(self.star_frame, self.btn_clear)

        all_patients = HeaderIconButton("person", "所有患者", True)
        imp = HeaderIconButton("import", "导入", True)
        self.btn_export = HeaderIconButton("export", "导出", False)
        conv = HeaderIconButton("convert", "数据转换", True)
        cest = HeaderIconButton("cest", "CEST", True)
        btn_scan = HeaderIconButton("scan", "扫描", True)

        # Positions are a uniform 1.207× scale of the original layout so that
        # relative spacing is identical but the larger (50%-bigger) widgets fit
        # without driving minimum_width above ~1400 px.  scan lands at 0.970
        # (near the right edge at minimum width).
        spec = [
            (self.btn_create, 0.026),
            (self.btn_edit, 0.071),
            (self.btn_delete, 0.115),
            (self._vline_item(), 0.148),
            (self.btn_live, 0.183),
            (self._vline_item(), 0.218),
            (date_pair, 0.264),
            (ds_pair, 0.379),
            (rating_pair, 0.488),
            (sc_pair, 0.580),
            (all_patients, 0.671),
            (self._vline_item(), 0.705),
            (imp, 0.743),
            (self.btn_export, 0.796),
            (conv, 0.852),
            (cest, 0.910),
            (btn_scan, 0.970),
        ]
        for widget, pct in spec:
            bar.add(widget, pct)
        self.header = bar
        return bar

    def _pair(self, top, bottom, center=True):
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(4)
        for lb in (top, bottom):
            if isinstance(lb, QLabel):
                lb.setStyleSheet(
                    f'font-family:"SimHei","黑体"; font-size:{_LBL_PX}px; font-weight:bold; color:#3a3a3a;')
        align = (Qt.AlignHCenter if center else Qt.AlignLeft) | Qt.AlignVCenter
        v.addWidget(top, 0, align)
        v.addWidget(bottom, 0, align)
        return w

    def _mini_button(self, text, kind="darkbtn"):
        b = QPushButton(text)
        b.setProperty("class", kind)
        b.setFixedHeight(33)
        b.setStyleSheet(
            f'font-family:"SimHei","黑体"; font-size:{_LBL_PX}px; font-weight:bold;')
        if kind != "flatbtn":
            b.setMinimumWidth(87)
        return b

    def _vline_item(self):
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFixedWidth(2)
        line.setStyleSheet("color:#c8ccd0;")
        return line

    def _update_star_frame(self):
        """Black bg when a rating filter is active; clear-button grey otherwise."""
        active = self.star_filter > 0
        bg = "#000000" if active else style.CLEAR_BTN_BG
        border = "#000000" if active else "#9aa0a6"
        self.star_frame.setStyleSheet(
            f"QFrame#StarFilterFrame{{ border:1px solid {border};"
            f" border-radius:8px; background:{bg}; }}"
        )

    # ---------------- center ----------------
    def _build_center(self):
        self.stack = QStackedWidget()

        self.grid_scroll = QScrollArea()
        self.grid_scroll.setWidgetResizable(True)
        self.grid_scroll.setObjectName("WorkArea")
        self.grid_container = QWidget()
        self.grid_container.setObjectName("WorkArea")
        self.grid_container.setAttribute(Qt.WA_StyledBackground, True)
        self.flow = FlowLayout(self.grid_container, margin=14, spacing=12)
        self.grid_scroll.setWidget(self.grid_container)

        self.list_view = ListView()
        self.list_view.selection_changed.connect(self._on_list_selection)
        self.list_view.edit_requested.connect(self._edit_one)
        self.list_view.rating_changed.connect(self._set_rating)
        self.list_view.sort_requested.connect(self._on_sort)

        self.stack.addWidget(self.grid_scroll)
        self.stack.addWidget(self.list_view)
        self.stack.setStyleSheet(f"background:{style.WORK_AREA_BG};")
        return self.stack

    # ---------------- grey footer ----------------
    def _build_grey_footer(self):
        bar = QWidget()
        bar.setObjectName("GreyFooter")
        bar.setAttribute(Qt.WA_StyledBackground, True)
        bar.setFixedHeight(30)
        h = QHBoxLayout(bar)
        h.setContentsMargins(10, 2, 10, 2)
        h.addStretch(1)

        h.addWidget(QLabel("\u2014"))
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setRange(100, 200)
        self.zoom_slider.setValue(100)
        self.zoom_slider.setFixedWidth(160)
        self.zoom_slider.valueChanged.connect(self._on_zoom)
        h.addWidget(self.zoom_slider)
        h.addWidget(QLabel("+"))
        self.zoom_label = QLabel("100%")
        self.zoom_label.setFixedWidth(40)
        h.addWidget(self.zoom_label)

        h.addSpacing(20)
        self.btn_first = QToolButton(); self.btn_first.setText("|<")
        self.btn_prev = QToolButton(); self.btn_prev.setText("<")
        self.btn_next = QToolButton(); self.btn_next.setText(">")
        self.btn_last = QToolButton(); self.btn_last.setText(">|")
        for b in (self.btn_first, self.btn_prev, self.btn_next, self.btn_last):
            b.setObjectName("ViewBtn")
            b.setStyleSheet("QToolButton{border:none;padding:2px 6px;}")
        self.btn_first.clicked.connect(lambda: self._go_page(1))
        self.btn_prev.clicked.connect(lambda: self._go_page(self.page - 1))
        self.btn_next.clicked.connect(lambda: self._go_page(self.page + 1))
        self.btn_last.clicked.connect(lambda: self._go_page(self._last_page()))

        self.page_edit = QLineEdit("1")
        self.page_edit.setFixedWidth(40)
        self.page_edit.setAlignment(Qt.AlignCenter)
        self.page_edit.setValidator(QIntValidator(1, 999999))
        self.page_edit.editingFinished.connect(self._on_page_edit)
        self.page_total = QLabel("/1")

        h.addWidget(self.btn_first)
        h.addWidget(self.btn_prev)
        h.addWidget(self.page_edit)
        h.addWidget(self.page_total)
        h.addWidget(self.btn_next)
        h.addWidget(self.btn_last)

        self.perpage_combo = QComboBox()
        self.perpage_combo.addItems(["每页显示50条", "每页显示75条", "每页显示100条"])
        self.perpage_combo.currentIndexChanged.connect(self._on_perpage)
        h.addWidget(self.perpage_combo)
        return bar

    # ---------------- blue footer ----------------
    def _build_blue_footer(self):
        bar = QWidget()
        bar.setObjectName("BlueFooter")
        bar.setAttribute(Qt.WA_StyledBackground, True)
        bar.setFixedHeight(26)
        h = QHBoxLayout(bar)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(0)

        def vline():
            line = QFrame()
            line.setFrameShape(QFrame.VLine)
            line.setStyleSheet("color: rgba(255,255,255,0.22);")
            return line

        def cell(left_margin=12):
            w = QWidget()
            lay = QHBoxLayout(w)
            lay.setContentsMargins(left_margin, 0, 10, 0)
            lay.setSpacing(6)
            return w, lay

        # cell 1: view toggles
        c1w, c1 = cell(10)
        self.btn_grid = QToolButton()
        self.btn_grid.setObjectName("ViewBtn")
        self.btn_grid.setIcon(icons.icon("grid", "#cdd6e3", 22))
        self.btn_grid.setCheckable(True)
        self.btn_grid.setChecked(True)
        self.btn_list = QToolButton()
        self.btn_list.setObjectName("ViewBtn")
        self.btn_list.setIcon(icons.icon("list", "#cdd6e3", 22))
        self.btn_list.setCheckable(True)
        grp = QButtonGroup(self)
        grp.setExclusive(True)
        grp.addButton(self.btn_grid)
        grp.addButton(self.btn_list)
        self.btn_grid.clicked.connect(lambda: self._set_view("grid"))
        self.btn_list.clicked.connect(lambda: self._set_view("list"))
        c1.addWidget(self.btn_grid)
        c1.addWidget(self.btn_list)
        c1.addStretch(1)

        # cell 2: total
        c2w, c2 = cell()
        self.lbl_total = QLabel("病例总数: 0")
        c2.addWidget(self.lbl_total)
        c2.addStretch(1)

        # cell 3: ungenerated reports
        c3w, c3 = cell()
        self.lbl_reports = QLabel("未生成报告条数: 0")
        c3.addWidget(self.lbl_reports)
        c3.addStretch(1)

        # cell 4: disk space
        c4w, c4 = cell()
        self.lbl_disk = QLabel("可用存储空间: -")
        c4.addWidget(self.lbl_disk)
        c4.addStretch(1)

        for w in (c1w, c2w, c3w, c4w):
            h.addWidget(vline())
            h.addWidget(w, 1)
        h.addWidget(vline())
        h.addStretch(2)  # empty space on the right
        return bar

    # ---------------- logic ----------------
    def _filtered(self):
        text = self.search.text().strip().lower()
        data = list(state.profiles)
        if text:
            data = [
                p for p in data
                if text in " ".join(
                    str(p.get(k, "")) for k in ("name", "visit_no", "capsule_no")).lower()
            ]
        if self.star_filter:
            data = [p for p in data if int(p.get("rating", 0)) == self.star_filter]
        if self.sort_key:
            data.sort(key=lambda p: self._sort_value(p, self.sort_key),
                      reverse=self.sort_desc)
        return data

    def _sort_value(self, p, key):
        if key == "exam_date":
            d = p.get("exam_date")
            try:
                return d.toJulianDay()
            except AttributeError:
                return 0
        if key in ("age", "rating"):
            try:
                return (0, int(p.get(key, 0)))
            except (TypeError, ValueError):
                return (1, str(p.get(key, "")))
        if key == "status":
            return "分配设备"
        return str(p.get(key, "")).lower()

    def _on_sort(self, key):
        if self.sort_key == key:
            self.sort_desc = not self.sort_desc
        else:
            self.sort_key = key
            self.sort_desc = False
        self.page = 1
        self.refresh()

    def _on_star_filter(self, value):
        if value == self.star_filter:
            self.star_filter = 0
            self.star_filter_stars.setValue(0)
        else:
            self.star_filter = value
            self.star_filter_stars.setValue(value)
        self._update_star_frame()
        self.page = 1
        self.refresh()

    def _last_page(self):
        n = len(self._filtered())
        return max(1, math.ceil(n / self.per_page))

    def _go_page(self, page):
        last = self._last_page()
        self.page = max(1, min(page, last))
        self.refresh()

    def _on_page_edit(self):
        try:
            val = int(self.page_edit.text())
        except ValueError:
            val = 1
        self._go_page(val)

    def _on_perpage(self, idx):
        self.per_page = [50, 75, 100][idx]
        self.page = 1
        self.refresh()

    def _on_zoom(self, val):
        self.zoom = val / 100.0
        self.zoom_label.setText(f"{val}%")
        self._populate()

    def _on_search(self):
        self.page = 1
        self.refresh()

    def _clear_all(self):
        """清除所有: clear search text, the rating filter and the sort dropdown."""
        self.search.blockSignals(True)
        self.search.clear()
        self.search.blockSignals(False)
        self.star_filter = 0
        self.star_filter_stars.setValue(0)
        self._update_star_frame()
        self.filter_combo.setCurrentIndex(0)
        self.page = 1
        self.refresh()

    def _set_view(self, mode):
        self.view_mode = mode
        self.stack.setCurrentIndex(0 if mode == "grid" else 1)
        state.clear_selection()
        self.refresh()

    def refresh(self):
        last = self._last_page()
        if self.page > last:
            self.page = last
        self.page_total.setText(f"/{last}")
        self.page_edit.setText(str(self.page))
        self._populate()
        self._update_counts()
        self._update_selection_ui()

    def _page_slice(self):
        data = self._filtered()
        start = (self.page - 1) * self.per_page
        return data[start:start + self.per_page]

    def _populate(self):
        page = self._page_slice()
        if self.view_mode == "grid":
            self._clear_flow()
            for p in page:
                card = ProfileCard(
                    p, format_date(p.get("exam_date")), self.zoom,
                    selected=p["id"] in state.selected_ids,
                )
                card.clicked.connect(self._select_single)
                card.rating_changed.connect(self._set_rating)
                self.flow.addWidget(card)
        else:
            self.list_view.set_scale(self.zoom)
            self.list_view.set_profiles(page)

    def _clear_flow(self):
        while self.flow.count():
            item = self.flow.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    def _update_counts(self):
        total = state.total_profiles
        # 导出 is only available when at least one profile exists
        self.btn_export.set_enabled_state(total > 0)
        self.total_label.setText(f"合计: 1")
        self.lbl_total.setText(f"病例总数: {total}")
        self.lbl_reports.setText(f"未生成报告条数: {state.ungenerated_reports}")
        free, tot = state.disk_space()
        self.lbl_disk.setText(f"可用存储空间: {human_size(free)}/{human_size(tot)}")

    # ---------------- selection ----------------
    def _select_single(self, pid):
        if state.selected_ids == {pid}:
            state.clear_selection()
        else:
            state.set_selection({pid})
        # restyle cards
        for i in range(self.flow.count()):
            w = self.flow.itemAt(i).widget()
            if isinstance(w, ProfileCard):
                w.set_selected(w.profile["id"] in state.selected_ids)

    def _set_rating(self, pid, value):
        p = state.get_profile(pid)
        if p is not None:
            p["rating"] = value

    def _on_list_selection(self):
        state.set_selection(self.list_view.checked_ids())

    def _update_selection_ui(self):
        n = len(state.selected_ids)
        self.btn_edit.set_enabled_state(n == 1)
        self.btn_delete.set_enabled_state(n >= 1)

    # ---------------- CRUD ----------------
    def create_profile(self):
        dlg = ProfileDialog(self.window())
        dlg._center_on(self.window())
        if dlg.exec() == ProfileDialog.Accepted:
            data = dlg.collect()
            data["rating"] = 0
            state.add_profile(data)

    def edit_selected(self):
        if len(state.selected_ids) != 1:
            return
        self._edit_one(next(iter(state.selected_ids)))

    def _edit_one(self, pid):
        p = state.get_profile(pid)
        if not p:
            return
        dlg = ProfileDialog(self.window(), profile=p)
        dlg._center_on(self.window())
        if dlg.exec() == ProfileDialog.Accepted:
            state.update_profile(pid, dlg.collect())

    def delete_selected(self):
        if not state.selected_ids:
            return
        if ConfirmDialog.ask(self.window(), "删除病例后将无法恢复，是否确定删除?", "删除病例"):
            state.delete_profiles(set(state.selected_ids))
