"""Login window shown at startup.

Any credentials are accepted. 登录 signs in with the typed username; 快速登录
ignores the inputs and signs in as Admin/Admin. Either way the account is
written to the in-memory user table and becomes the current user. A globe
button in the header switches the window language.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLineEdit,
    QMenu,
    QPushButton,
    QToolButton,
    QVBoxLayout,
)

from app import icons
from app.dialogs.base import FramelessDialog
from app.state import state

# per-language strings for the login window
TR = {
    "zh": {
        "code": "简", "user": "用户名", "pw": "密码",
        "login": "登录", "quick": "快速登录",
        "remember": "记住密码", "auto": "自动登录",
    },
    "zh_TW": {
        "code": "繁", "user": "使用者名稱", "pw": "密碼",
        "login": "登入", "quick": "快速登入",
        "remember": "記住密碼", "auto": "自動登入",
    },
    "en": {
        "code": "EN", "user": "Username", "pw": "Password",
        "login": "Login", "quick": "Quick Login",
        "remember": "Remember password", "auto": "Auto login",
    },
}


class LoginDialog(FramelessDialog):
    def __init__(self, parent=None):
        super().__init__("", parent)
        self.lang = "zh"

        # ----- header: globe / language switcher on the left -----
        self.lang_btn = QToolButton()
        self.lang_btn.setObjectName("LangBtn")
        self.lang_btn.setIcon(icons.icon("globe", "#ffffff", 22))
        self.lang_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.lang_btn.setCursor(Qt.PointingHandCursor)
        self.lang_btn.setPopupMode(QToolButton.InstantPopup)
        menu = QMenu(self.lang_btn)
        for code, label in (("zh", "简体中文"), ("zh_TW", "繁體中文"), ("en", "English")):
            act = menu.addAction(label)
            act.triggered.connect(lambda _=False, c=code: self._set_lang(c))
        self.lang_btn.setMenu(menu)
        self.header.layout().insertWidget(0, self.lang_btn)

        # ----- body -----
        self.body.setObjectName("LoginBody")
        self.body.setAttribute(Qt.WA_StyledBackground, True)
        root = QVBoxLayout(self.body)
        root.setContentsMargins(26, 24, 26, 20)
        root.setSpacing(14)

        self.user_edit = QLineEdit()
        self.user_edit.setFixedHeight(36)
        self.user_edit.addAction(
            icons.icon("user_caret", "#1a1a1a", 22), QLineEdit.TrailingPosition)

        self.pw_edit = QLineEdit()
        self.pw_edit.setFixedHeight(36)
        self.pw_edit.setEchoMode(QLineEdit.Password)
        self.pw_edit.addAction(
            icons.icon("lock", "#1a1a1a", 22), QLineEdit.TrailingPosition)

        root.addWidget(self.user_edit)
        root.addWidget(self.pw_edit)
        root.addSpacing(4)

        brow = QHBoxLayout()
        brow.setSpacing(18)
        self.btn_login = QPushButton()
        self.btn_quick = QPushButton()
        for b in (self.btn_login, self.btn_quick):
            b.setProperty("class", "loginbtn")
            b.setFixedHeight(36)
            b.setMinimumWidth(132)
            b.setCursor(Qt.PointingHandCursor)
            brow.addWidget(b)
        self.btn_login.clicked.connect(self._do_login)
        self.btn_quick.clicked.connect(self._do_quick)
        root.addLayout(brow)
        root.addSpacing(2)

        self.cb_remember = QCheckBox()
        self.cb_auto = QCheckBox()
        root.addWidget(self.cb_remember)
        root.addWidget(self.cb_auto)

        self.setFixedWidth(372)
        self._retranslate()

    # ----- language -----
    def _set_lang(self, code: str) -> None:
        self.lang = code
        self._retranslate()

    def _retranslate(self) -> None:
        t = TR[self.lang]
        self.lang_btn.setText(t["code"])
        self.user_edit.setPlaceholderText(t["user"])
        self.pw_edit.setPlaceholderText(t["pw"])
        self.btn_login.setText(t["login"])
        self.btn_quick.setText(t["quick"])
        self.cb_remember.setText(t["remember"])
        self.cb_auto.setText(t["auto"])

    # ----- actions -----
    def _do_login(self) -> None:
        state.login(self.user_edit.text(), self.pw_edit.text())
        self.accept()

    def _do_quick(self) -> None:
        # ignore typed credentials; always sign in as Admin/Admin
        state.login("Admin", "Admin")
        self.accept()

    # center on screen the first time it is shown
    def showEvent(self, e):
        super().showEvent(e)
        if not getattr(self, "_centered", False):
            self._centered = True
            self.adjustSize()
            scr = QGuiApplication.primaryScreen().availableGeometry()
            self.move(scr.center().x() - self.width() // 2,
                      scr.center().y() - self.height() // 2)
