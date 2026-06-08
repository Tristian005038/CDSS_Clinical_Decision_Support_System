"""Add-user popup for the settings user-management tab."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from app import style
from app.dialogs.base import FramelessDialog


class AddUserDialog(FramelessDialog):
    def __init__(self, parent=None, user: dict | None = None):
        super().__init__("编辑用户" if user else "添加用户", parent)
        root = QVBoxLayout(self.body)
        root.setContentsMargins(20, 20, 20, 14)
        root.setSpacing(16)

        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(14)

        def req(text):
            return QLabel(f'{text} <span style="color:{style.ERROR_RED}">*</span>')

        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.realname = QLineEdit()
        self.confirm = QLineEdit()
        self.confirm.setEchoMode(QLineEdit.Password)
        self.dept = QLineEdit()
        for w in (self.username, self.password, self.realname, self.confirm, self.dept):
            w.setFixedWidth(150)

        grid.addWidget(req("用户名称"), 0, 0)
        grid.addWidget(self.username, 0, 1)
        grid.addWidget(req("密码"), 0, 2)
        grid.addWidget(self.password, 0, 3)
        hint = QLabel("用户名称不区分大小写")
        hint.setStyleSheet("color:#8a8f95;")
        grid.addWidget(hint, 1, 1)
        grid.addWidget(req("真实姓名"), 2, 0)
        grid.addWidget(self.realname, 2, 1)
        grid.addWidget(req("密码确认"), 2, 2)
        grid.addWidget(self.confirm, 2, 3)
        grid.addWidget(QLabel("部门"), 3, 0)
        grid.addWidget(self.dept, 3, 1)
        root.addLayout(grid)

        trow = QHBoxLayout()
        trow.addWidget(QLabel("用户类型"))
        self.cb_admin = QCheckBox("管理员")
        self.cb_doctor = QCheckBox("医生")
        self.cb_readonly = QCheckBox("只读")
        for cb in (self.cb_admin, self.cb_doctor, self.cb_readonly):
            trow.addWidget(cb)
        trow.addStretch(1)
        root.addLayout(trow)

        self.error = QLabel("")
        self.error.setStyleSheet(f"color:{style.ERROR_RED};")
        root.addWidget(self.error)

        brow = QHBoxLayout()
        brow.addStretch(1)
        save = QPushButton("保存")
        cancel = QPushButton("取消")
        for b in (save, cancel):
            b.setProperty("class", "primary")
            b.setFixedWidth(80)
        save.clicked.connect(self._on_save)
        cancel.clicked.connect(self.reject)
        brow.addWidget(save)
        brow.addWidget(cancel)
        root.addLayout(brow)

        self.setMinimumWidth(460)
        if user:
            self.username.setText(user.get("username", ""))
            self.realname.setText(user.get("realname", ""))
            self.dept.setText(user.get("dept", ""))

    def _type_text(self):
        types = []
        if self.cb_admin.isChecked():
            types.append("管理员")
        if self.cb_doctor.isChecked():
            types.append("医生")
        if self.cb_readonly.isChecked():
            types.append("只读")
        return "/".join(types)

    def _on_save(self):
        if not self.username.text().strip() or not self.realname.text().strip():
            self.error.setText("请填写必填项!")
            return
        if self.password.text() != self.confirm.text():
            self.error.setText("两次输入的密码不一致!")
            return
        self.accept()

    def collect(self) -> dict:
        return {
            "username": self.username.text().strip(),
            "realname": self.realname.text().strip(),
            "dept": self.dept.text().strip(),
            "type": self._type_text() or "医生",
        }
