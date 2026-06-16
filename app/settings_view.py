"""Settings interface: left sidebar + stacked tab pages."""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView,
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app import icons, style
from app.dialogs.add_user_dialog import AddUserDialog
from app.dialogs.confirm_dialog import ConfirmDialog
from app.dialogs.manage_doctor_dialog import ManageDoctorDialog
from app.state import state

DATE_FORMATS = {
    "年/月/日": "yyyy/MM/dd",
    "月/日/年": "MM/dd/yyyy",
    "日/月/年": "dd/MM/yyyy",
}
PRESET_COLORS = [
    "#000000", "#5a5a5a", "#8a8a8a", "#b5651d", "#a01818", "#d61f8f", "#7a1fd6",
    "#2b2b2b", "#ffffff", "#f2e000", "#9acd32", "#3fbf3f", "#3aa0e6",
]


def _h1(text):
    lb = QLabel(text)
    lb.setProperty("class", "h1")
    return lb


def _h2(text):
    lb = QLabel(text)
    lb.setProperty("class", "h2")
    return lb


def _sub(text):
    lb = QLabel(text)
    lb.setProperty("class", "sub")
    return lb


def _primary(text, width=None):
    b = QPushButton(text)
    b.setProperty("class", "primary")
    if width:
        b.setFixedWidth(width)
    return b


class SettingsView(QWidget):
    back_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        h = QHBoxLayout(self)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(0)

        h.addWidget(self._build_sidebar())
        self.stack = QStackedWidget()
        self.stack.setObjectName("SettingsArea")
        h.addWidget(self.stack, 1)

        self.stack.addWidget(self._page_users())
        self.stack.addWidget(self._page_hospital())
        self.stack.addWidget(self._page_data())
        self.stack.addWidget(self._page_pacs())
        self.stack.addWidget(self._page_custom())
        self.stack.addWidget(self._page_about())
        self.stack.addWidget(self._page_logout())

        self.nav_buttons[0].setChecked(True)
        self.stack.setCurrentIndex(0)
        state.users_changed.connect(self._reload_users)
        state.current_user_changed.connect(self._refresh_current_user)

    # ---------------- sidebar ----------------
    def _build_sidebar(self):
        side = QWidget()
        side.setObjectName("Sidebar")
        side.setAttribute(Qt.WA_StyledBackground, True)
        side.setFixedWidth(96)
        v = QVBoxLayout(side)
        v.setContentsMargins(0, 8, 0, 8)
        v.setSpacing(0)

        back = QPushButton()
        back.setIcon(icons.icon("arrow_left", "#cdd6e3", 24))
        back.setStyleSheet("padding:10px;")
        back.clicked.connect(self.back_requested.emit)
        v.addWidget(back)
        v.addSpacing(10)

        names = ["用户管理", "医院数据", "数据管理", "PACS", "自定义", "关于", "退出登录"]
        self.nav_buttons = []
        grp = QButtonGroup(self)
        grp.setExclusive(True)
        for i, n in enumerate(names):
            b = QPushButton(n)
            b.setCheckable(True)
            b.clicked.connect(lambda _=False, idx=i: self._nav(idx))
            grp.addButton(b)
            v.addWidget(b)
            self.nav_buttons.append(b)
        v.addStretch(1)
        return side

    def _nav(self, idx):
        if idx == 6:  # 退出登录
            self.stack.setCurrentIndex(6)
        else:
            self.stack.setCurrentIndex(idx)

    def _scroll_page(self, inner: QWidget) -> QWidget:
        return inner

    # ---------------- page: users ----------------
    def _page_users(self):
        page = QWidget()
        v = QVBoxLayout(page)
        v.setContentsMargins(30, 24, 30, 24)
        v.setSpacing(8)
        v.addWidget(_h1("用户管理"))
        self.lbl_current_user = _sub("")
        self._refresh_current_user()
        v.addWidget(self.lbl_current_user)
        v.addSpacing(8)
        v.addWidget(_h2("修改密码"))

        form = QGridLayout()
        form.setHorizontalSpacing(10)
        form.setVerticalSpacing(8)
        self.old_pw = QLineEdit(); self.old_pw.setEchoMode(QLineEdit.Password)
        self.new_pw = QLineEdit(); self.new_pw.setEchoMode(QLineEdit.Password)
        self.conf_pw = QLineEdit(); self.conf_pw.setEchoMode(QLineEdit.Password)
        for w in (self.old_pw, self.new_pw, self.conf_pw):
            w.setFixedWidth(170)
        form.addWidget(QLabel("原始密码"), 0, 0); form.addWidget(self.old_pw, 0, 1)
        form.addWidget(QLabel("新密码"), 1, 0); form.addWidget(self.new_pw, 1, 1)
        form.addWidget(QLabel("密码确认"), 2, 0); form.addWidget(self.conf_pw, 2, 1)
        save = _primary("保存", 90)
        form.addWidget(save, 3, 1)
        wrap = QHBoxLayout(); wrap.addLayout(form); wrap.addStretch(1)
        v.addLayout(wrap)
        v.addSpacing(14)

        self.users_table = QTableWidget(0, 4)
        self.users_table.setHorizontalHeaderLabels(["用户名称", "真实姓名", "部门", "用户类型"])
        self.users_table.verticalHeader().setVisible(False)
        self.users_table.setAlternatingRowColors(True)
        self.users_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.users_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.users_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.users_table.setFocusPolicy(Qt.NoFocus)
        self.users_table.setStyleSheet(
            "QTableWidget{ background:#ffffff; alternate-background-color:#eef0f2;"
            " outline:0; }"
            "QTableWidget::item{ border:none; }"
            "QTableWidget::item:hover{ background:transparent; }"
            "QTableWidget::item:selected{ background:#cfe0f3; color:#2b2b2b; }")
        self.users_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.users_table.setFixedHeight(200)
        v.addWidget(self.users_table)

        brow = QHBoxLayout()
        add = _primary("添加用户", 100)
        edit = _primary("编辑用户", 100)
        rem = _primary("删除用户", 100)
        add.clicked.connect(self._add_user)
        edit.clicked.connect(self._edit_user)
        rem.clicked.connect(self._delete_user)
        for b in (add, edit, rem):
            brow.addWidget(b)
        brow.addStretch(1)
        v.addLayout(brow)
        v.addStretch(1)
        self._reload_users()
        return page

    def _refresh_current_user(self):
        name = state.current_user or "Admin"
        self.lbl_current_user.setText(f"当前登录用户为 '{name}'")

    def _reload_users(self):
        t = self.users_table
        t.setRowCount(len(state.users))
        for r, u in enumerate(state.users):
            t.setItem(r, 0, QTableWidgetItem(u.get("username", "")))
            t.setItem(r, 1, QTableWidgetItem(u.get("realname", "")))
            t.setItem(r, 2, QTableWidgetItem(u.get("dept", "")))
            t.setItem(r, 3, QTableWidgetItem(u.get("type", "")))

    def _add_user(self):
        dlg = AddUserDialog(self.window())
        dlg._center_on(self.window())
        if dlg.exec() == AddUserDialog.Accepted:
            state.users.append(dlg.collect())
            state.users_changed.emit()

    def _edit_user(self):
        row = self.users_table.currentRow()
        if row < 0:
            return
        dlg = AddUserDialog(self.window(), user=state.users[row])
        dlg._center_on(self.window())
        if dlg.exec() == AddUserDialog.Accepted:
            state.users[row] = dlg.collect()
            state.users_changed.emit()

    def _delete_user(self):
        row = self.users_table.currentRow()
        if row < 0:
            return
        if ConfirmDialog.ask(self.window(), "确定删除选中的用户?"):
            del state.users[row]
            state.users_changed.emit()

    # ---------------- page: hospital ----------------
    def _page_hospital(self):
        page = QWidget()
        v = QVBoxLayout(page)
        v.setContentsMargins(30, 24, 30, 24)
        v.setSpacing(8)
        v.addWidget(_h1("医院数据"))
        v.addWidget(_sub("导入、编辑医院信息"))
        v.addSpacing(6)
        v.addWidget(_h2("基本信息"))

        form = QGridLayout()
        form.setHorizontalSpacing(10)
        form.setVerticalSpacing(10)
        self.h_name = QLineEdit(); self.h_name.setFixedWidth(300)
        self.h_second = QLineEdit(); self.h_second.setFixedWidth(300)
        self.h_phone = QLineEdit(); self.h_phone.setFixedWidth(160)
        form.addWidget(QLabel("医院名称"), 0, 0); form.addWidget(self.h_name, 0, 1)
        form.addWidget(QLabel("二级名称"), 1, 0); form.addWidget(self.h_second, 1, 1)
        form.addWidget(QLabel("医院电话"), 2, 0); form.addWidget(self.h_phone, 2, 1)
        wrap = QHBoxLayout(); wrap.addLayout(form); wrap.addStretch(1)
        v.addLayout(wrap)

        brow = QHBoxLayout()
        clear = _primary("确定", 90)
        save = _primary("保存", 90)
        manage = _primary("科室与医生管理", 130)
        clear.clicked.connect(self._hospital_clear)
        save.clicked.connect(self._hospital_save)
        manage.clicked.connect(self._open_manage)
        for b in (clear, save, manage):
            brow.addWidget(b)
        brow.addStretch(1)
        v.addLayout(brow)
        v.addSpacing(10)

        line = QFrame(); line.setFrameShape(QFrame.HLine); line.setStyleSheet("color:#c8ccd0;")
        v.addWidget(line)
        v.addWidget(_h2("医院Logo"))
        v.addWidget(_sub("导入图片类型为jpg、png、gif或bmp。"))
        self.logo_box = QLabel()
        self.logo_box.setFixedSize(150, 120)
        self.logo_box.setStyleSheet("background:#ffffff; border:1px solid #c0c4c8;")
        self.logo_box.setAlignment(Qt.AlignCenter)
        v.addWidget(self.logo_box)
        lrow = QHBoxLayout()
        imp = _primary("导入", 80)
        dele = _primary("删除", 80)
        imp.clicked.connect(self._import_logo)
        dele.clicked.connect(self._delete_logo)
        lrow.addWidget(imp); lrow.addWidget(dele); lrow.addStretch(1)
        v.addLayout(lrow)
        v.addStretch(1)
        return page

    def _hospital_save(self):
        state.hospital.update(
            name=self.h_name.text(), second_name=self.h_second.text(),
            phone=self.h_phone.text())

    def _hospital_clear(self):
        self.h_name.clear(); self.h_second.clear(); self.h_phone.clear()

    def _open_manage(self):
        dlg = ManageDoctorDialog(self.window())
        dlg._center_on(self.window())
        dlg.exec()

    def _import_logo(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择Logo", "", "图片 (*.png *.jpg *.jpeg *.gif *.bmp)")
        if path:
            pm = QPixmap(path).scaled(
                self.logo_box.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.logo_box.setPixmap(pm)
            state.hospital["logo"] = path

    def _delete_logo(self):
        self.logo_box.clear()
        state.hospital["logo"] = None

    # ---------------- page: data ----------------
    def _page_data(self):
        page = QWidget()
        v = QVBoxLayout(page)
        v.setContentsMargins(30, 24, 30, 24)
        v.setSpacing(10)
        v.addWidget(_h1("数据管理"))
        v.addWidget(_sub("设置软件全局系统参数"))

        v.addWidget(QLabel("请选择数据保存路径"))
        prow = QHBoxLayout()
        self.path_edit = QLineEdit(state.settings["data_path"])
        choose = _primary("选择路径", 90)
        apply_path = _primary("应用", 70)
        choose.clicked.connect(self._choose_path)
        apply_path.clicked.connect(
            lambda: state.settings.update(data_path=self.path_edit.text()))
        prow.addWidget(self.path_edit, 1)
        prow.addWidget(choose)
        prow.addWidget(apply_path)
        v.addLayout(prow)

        drow = QGridLayout()
        drow.setHorizontalSpacing(10)
        drow.setVerticalSpacing(8)
        self.date_combo = QComboBox(); self.date_combo.addItems(list(DATE_FORMATS.keys()))
        self.input_combo = QComboBox(); self.input_combo.addItems(["年份", "月份", "日"])
        self.display_combo = QComboBox(); self.display_combo.addItems(["年份", "月份", "日"])
        for w in (self.date_combo, self.input_combo, self.display_combo):
            w.setFixedWidth(120)
        drow.addWidget(QLabel("日期格式"), 0, 0); drow.addWidget(self.date_combo, 0, 1)
        drow.addWidget(QLabel("输入日期为"), 1, 0); drow.addWidget(self.input_combo, 1, 1)
        drow.addWidget(QLabel("显示日期为"), 2, 0); drow.addWidget(self.display_combo, 2, 1)
        dwrap = QHBoxLayout(); dwrap.addLayout(drow); dwrap.addStretch(1)
        v.addLayout(dwrap)
        apply_date = _primary("应用", 70)
        apply_date.clicked.connect(self._apply_date)
        v.addWidget(apply_date)

        crow = QHBoxLayout()
        cleft = QVBoxLayout()
        cleft.addWidget(QLabel("标记颜色:"))
        cbox = QHBoxLayout()
        self.selected_color = QLabel()
        self.selected_color.setFixedSize(54, 54)
        self._set_color(state.settings["marker_color"])
        cbox.addWidget(self.selected_color)
        grid = QGridLayout()
        grid.setSpacing(3)
        for i, col in enumerate(PRESET_COLORS):
            sw = QPushButton()
            sw.setFixedSize(20, 20)
            sw.setStyleSheet(f"background:{col}; border:1px solid #999;")
            sw.clicked.connect(lambda _=False, c=col: self._set_color(c))
            grid.addWidget(sw, i // 7, i % 7)
        cbox.addLayout(grid)
        cbox.addStretch(1)
        cleft.addLayout(cbox)
        crow.addLayout(cleft)

        cright = QVBoxLayout()
        cright.addWidget(QLabel("线条粗细:"))
        self.line_combo = QComboBox()
        self.line_combo.addItems(["——", "———", "————"])
        self.line_combo.setFixedWidth(120)
        cright.addWidget(self.line_combo)
        cright.addStretch(1)
        crow.addSpacing(40)
        crow.addLayout(cright)
        crow.addStretch(1)
        v.addLayout(crow)

        self.cb1 = QCheckBox("报告及导出图片和AVI视频的医院患者信息"); self.cb1.setChecked(True)
        self.cb2 = QCheckBox("下载完成后自动关机")
        self.cb3 = QCheckBox("下载完成后删除数据")
        self.cb4 = QCheckBox("数据下载后自动归类病灶"); self.cb4.setChecked(True)
        for cb in (self.cb1, self.cb2, self.cb3, self.cb4):
            v.addWidget(cb)
        v.addStretch(1)
        return page

    def _choose_path(self):
        d = QFileDialog.getExistingDirectory(self, "选择路径", self.path_edit.text())
        if d:
            self.path_edit.setText(d)

    def _apply_date(self):
        fmt = DATE_FORMATS[self.date_combo.currentText()]
        state.settings["date_format"] = fmt
        state.settings_changed.emit()

    def _set_color(self, color):
        state.settings["marker_color"] = color
        self.selected_color.setStyleSheet(f"background:{color}; border:1px solid #777;")

    # ---------------- page: pacs ----------------
    def _page_pacs(self):
        page = QWidget()
        v = QVBoxLayout(page)
        v.setContentsMargins(30, 24, 30, 24)
        v.setSpacing(6)
        v.addWidget(_h1("PACS"))

        def section(title, rows, extra=None):
            v.addSpacing(6)
            v.addWidget(_h2(title))
            g = QGridLayout(); g.setHorizontalSpacing(10); g.setVerticalSpacing(8)
            for i, label in enumerate(rows):
                g.addWidget(QLabel(label), i, 0)
                le = QLineEdit(); le.setFixedWidth(170)
                g.addWidget(le, i, 1)
                if extra and label in extra:
                    g.addWidget(QLabel(extra[label]), i, 2)
            wrap = QHBoxLayout(); wrap.addLayout(g); wrap.addStretch(1)
            v.addLayout(wrap)
            v.addWidget(_primary("更新", 70))

        section("Caller", ["标题", "模式", "端口"])
        section("Worklist Server", ["IP地址", "端口", "标题", "显示范围"],
                extra={"显示范围": "天"})
        section("Image Storage Server", ["IP地址", "端口", "标题"])
        v.addStretch(1)
        return page

    # ---------------- page: custom ----------------
    def _page_custom(self):
        page = QWidget()
        v = QVBoxLayout(page)
        v.setContentsMargins(30, 24, 30, 24)
        v.setSpacing(8)
        v.addWidget(_h1("自定义"))
        v.addWidget(_sub("阅片模板、图片描述、短语自定义"))
        trow = QHBoxLayout()
        for name in ("阅片模板", "图片描述", "短语"):
            lb = QLabel(name)
            lb.setStyleSheet(f"color:{style.ACCENT_BLUE}; font-weight:bold;")
            trow.addWidget(lb)
            trow.addSpacing(10)
        trow.addStretch(1)
        v.addLayout(trow)
        v.addWidget(_primary("添加阅片模板", 110))
        lst = QListWidget()
        lst.addItems(["小肠检查模板", "胃检查模板", "胃+小肠检查模板"])
        lst.setFixedHeight(260)
        lst.setAlternatingRowColors(True)
        lst.setFocusPolicy(Qt.NoFocus)
        lst.setStyleSheet(
            "QListWidget{ background:#ffffff; alternate-background-color:#eef0f2;"
            " outline:0; border:1px solid #c4c8cc; }"
            "QListWidget::item{ padding:5px; border:none; }"
            "QListWidget::item:hover{ background:transparent; }"
            "QListWidget::item:selected{ background:#cfe0f3; color:#2b2b2b; }")
        v.addWidget(lst)
        v.addStretch(1)
        return page

    def _page_about(self):
        page = QWidget()
        v = QVBoxLayout(page)
        v.setContentsMargins(30, 24, 30, 24)
        v.setSpacing(10)
        v.addWidget(_h1("关于"))

        info = QLabel(
            "软件名称：基于改进FPN的内镜息肉识别临床决策系统\n"
            "软件发布版本号：V1.0.0\n"
            "制作人：陶鑫 田思远"
        )
        info.setStyleSheet("font-size:13px; color:#8a8f95;")
        v.addWidget(info)
        v.addSpacing(8)

        org = QLabel("陆军军医大学附属第二医院")
        org.setStyleSheet("font-size:13px; color:#8a8f95;")
        v.addWidget(org)

        v.addStretch(1)
        return page

    def _page_logout(self):
        page = QWidget()
        v = QVBoxLayout(page)
        v.setContentsMargins(30, 24, 30, 24)
        v.addWidget(_h1("退出登录"))
        v.addStretch(1)
        return page
