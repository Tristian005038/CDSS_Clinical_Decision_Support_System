"""Create / edit profile popup with the 患者信息 form."""
from __future__ import annotations

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app import style
from app.dialogs.base import FramelessDialog
from app.dialogs.confirm_dialog import ConfirmDialog
from app.state import state

EXAM_ITEMS = ["请选择", "胃检查", "小肠检查", "结肠检查", "食道检查"]
GENDERS = ["请选择", "男", "女"]


class ProfileDialog(FramelessDialog):
    """If `profile` is provided the dialog is in edit mode."""

    def __init__(self, parent=None, profile: dict | None = None):
        title = "编辑患者" if profile else "新增患者"
        super().__init__(title, parent)
        self.editing = profile
        self.widgets: dict[str, QWidget] = {}
        self.req_keys = {
            "visit_no", "name", "capsule_no", "exam_item", "exam_date",
            "gender", "age", "applicant",
        }
        self.labels: dict[str, str] = {}

        root = QVBoxLayout(self.body)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ----- top form tabs -----
        tabs = QHBoxLayout()
        tabs.setContentsMargins(14, 10, 14, 0)
        tabs.setSpacing(2)
        t1 = QPushButton("患者信息")
        t1.setObjectName("FormTabActive")
        t2 = QPushButton("分配设备")
        t2.setObjectName("FormTabInactive")
        t2.setEnabled(False)
        tabs.addWidget(t1)
        tabs.addWidget(t2)
        tabs.addStretch(1)
        root.addLayout(tabs)

        panel = QWidget()
        panel.setObjectName("FormPanel")
        # scope the border to the panel so it doesn't cascade onto the labels/fields
        panel.setStyleSheet(
            "#FormPanel{ background:#ffffff; border:1px solid #c0c4c8; }")
        root.addWidget(panel, 1)
        grid = QGridLayout(panel)
        grid.setContentsMargins(18, 18, 18, 14)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(10)

        # 操作人员 / 申请人员 / 报告人员 dropdowns are driven by the
        # 用户名称 column of the 用户管理 table.
        user_names = state.user_names()

        # column 1
        self._field(grid, 0, 0, "就诊编号", "visit_no", "line")
        self._field(grid, 1, 0, "姓名", "name", "line")
        self._field(grid, 2, 0, "胶囊编号", "capsule_no", "line")
        self._field(grid, 3, 0, "检查项目", "exam_item", "fixed", options=EXAM_ITEMS)
        self._field(grid, 4, 0, "检查日期", "exam_date", "date")
        # column 2
        self._field(grid, 0, 2, "性别", "gender", "fixed", options=GENDERS)
        self._field(grid, 1, 2, "年龄", "age", "line")
        self._field(grid, 2, 2, "电话", "phone", "line")
        self._field(grid, 3, 2, "家庭住址", "home_addr", "line")
        self._field(grid, 4, 2, "科室/门诊", "dept", "combo")
        # column 3
        self._field(grid, 0, 4, "身高(cm)", "height", "line")
        self._field(grid, 1, 4, "体重(kg)", "weight", "line")
        self._field(grid, 2, 4, "操作人员", "operator", "combo", options=list(user_names))
        self._field(grid, 3, 4, "申请人员", "applicant", "combo", options=list(user_names))
        self._field(grid, 4, 4, "报告人员", "reporter", "combo", options=list(user_names))

        # multiline rows
        self._textarea(grid, 5, "主诉", "chief_complaint")
        self._textarea(grid, 6, "关键字描述", "keywords")

        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)
        grid.setColumnStretch(5, 1)

        # ----- bottom bar -----
        bottom = QHBoxLayout()
        bottom.setContentsMargins(16, 8, 16, 12)
        self.error_label = QLabel("")
        self.error_label.setProperty("class", "errortext")
        self.error_label.setStyleSheet(f"color:{style.ERROR_RED};")
        bottom.addWidget(self.error_label)
        bottom.addStretch(1)
        btn_cancel = QPushButton("取消")
        btn_next = QPushButton("下一步")
        btn_save = QPushButton("保存")
        for b in (btn_cancel, btn_next, btn_save):
            b.setProperty("class", "primary")
            b.setFixedWidth(80)
        btn_cancel.clicked.connect(self._on_cancel)
        btn_next.clicked.connect(self._on_next)
        btn_save.clicked.connect(self._on_save)
        bottom.addWidget(btn_cancel)
        bottom.addWidget(btn_next)
        bottom.addWidget(btn_save)
        root.addLayout(bottom)

        self.setMinimumWidth(620)
        if profile:
            self._load(profile)

    # ---------- field builders ----------
    def _mk_label(self, key: str, text: str) -> QLabel:
        self.labels[key] = text
        if key in self.req_keys:
            html = f'<span style="color:{style.ERROR_RED}">* </span>{text}'
        else:
            html = f'<span style="color:#ffffff">* </span>{text}'
        lb = QLabel(html)
        lb.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        return lb

    def _field(self, grid, row, col, text, key, kind, options=None):
        grid.addWidget(self._mk_label(key, text), row, col)
        if kind == "line":
            w = QLineEdit()
            w.setMaxLength(200)
        elif kind == "date":
            w = QDateEdit()
            w.setCalendarPopup(True)
            w.setDisplayFormat(state.settings["date_format"])
            w.setDate(QDate.currentDate())
        elif kind == "fixed":
            w = QComboBox()
            w.addItems(options or [])
        else:  # editable combo (dropdown + text input), blank to start
            w = QComboBox()
            w.setEditable(True)
            if options:
                w.addItems(options)
            w.setCurrentIndex(-1)
            w.setEditText("")
            if w.lineEdit():
                w.lineEdit().setMaxLength(200)
        self.widgets[key] = w
        grid.addWidget(w, row, col + 1)

    def _textarea(self, grid, row, text, key):
        grid.addWidget(self._mk_label(key, text), row, 0)
        w = QPlainTextEdit()
        w.setFixedHeight(54)

        def cap():
            t = w.toPlainText()
            if len(t) > 500:
                cur = w.textCursor()
                pos = cur.position()
                w.setPlainText(t[:500])
                cur.setPosition(min(pos, 500))
                w.setTextCursor(cur)

        w.textChanged.connect(cap)
        self.widgets[key] = w
        grid.addWidget(w, row, 1, 1, 5)

    # ---------- value helpers ----------
    def _value(self, key):
        w = self.widgets[key]
        if isinstance(w, QLineEdit):
            return w.text().strip()
        if isinstance(w, QPlainTextEdit):
            return w.toPlainText().strip()
        if isinstance(w, QDateEdit):
            return w.date()
        if isinstance(w, QComboBox):
            t = w.currentText().strip()
            return "" if t == "请选择" else t
        return ""

    def _set_invalid(self, key, invalid):
        w = self.widgets[key]
        w.setProperty("invalid", "true" if invalid else "false")
        w.style().unpolish(w)
        w.style().polish(w)

    def _clear_invalid(self):
        for key in self.widgets:
            self._set_invalid(key, False)
        self.error_label.setText("")

    def _load(self, p):
        for key, w in self.widgets.items():
            if key == "exam_date":
                d = p.get("exam_date")
                if isinstance(d, QDate):
                    w.setDate(d)
                continue
            val = p.get(key, "")
            if isinstance(w, QLineEdit):
                w.setText(str(val))
            elif isinstance(w, QPlainTextEdit):
                w.setPlainText(str(val))
            elif isinstance(w, QComboBox):
                if val:
                    idx = w.findText(str(val))
                    if idx >= 0:
                        w.setCurrentIndex(idx)
                    elif w.isEditable():
                        w.setEditText(str(val))

    # ---------- validation ----------
    def _first_missing(self):
        for key in ["visit_no", "name", "capsule_no", "exam_item", "exam_date",
                    "gender", "age", "applicant"]:
            v = self._value(key)
            if key == "exam_date":
                continue  # date always has a value
            if not v:
                return key
        return None

    def _validate_and_mark(self):
        self._clear_invalid()
        missing = []
        for key in self.req_keys:
            if key == "exam_date":
                continue
            if not self._value(key):
                missing.append(key)
                self._set_invalid(key, True)
        if missing:
            first = self._first_missing()
            self.error_label.setText(f"请正确输入{self.labels.get(first, '')}!")
            return False
        return True

    # ---------- buttons ----------
    def _on_cancel(self):
        if ConfirmDialog.ask(self, "取消后，未保存的信息不可恢复，是否需要关闭?"):
            self.reject()

    def _on_next(self):
        miss = self._first_missing()
        self._clear_invalid()
        if miss:
            self._set_invalid(miss, True)
            self.error_label.setText(f"请正确输入{self.labels.get(miss, '')}!")
        else:
            self.error_label.setText("")

    def _on_save(self):
        if not self._validate_and_mark():
            return
        self.accept()

    def collect(self) -> dict:
        data = {key: self._value(key) for key in self.widgets}
        return data
