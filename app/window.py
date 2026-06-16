"""Frameless main window with a custom title bar.

On Windows we re-attach the native window styles (resize border, min/max box)
and strip the non-client frame via WM_NCCALCSIZE, so dragging, snapping,
minimize / maximize / restore and edge-resize all behave natively while the
title bar stays fully custom.
"""
from __future__ import annotations

import sys

from PySide6.QtCore import QPoint, Qt
from PySide6.QtWidgets import (
    QAbstractButton,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QStackedWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from app import icons
from app.settings_view import SettingsView
from app.working_view import WorkingView

BORDER = 6
TITLE_H = 40

# win32 constants
GWL_STYLE = -16
WS_CAPTION = 0x00C00000
WS_THICKFRAME = 0x00040000
WS_MINIMIZEBOX = 0x00020000
WS_MAXIMIZEBOX = 0x00010000
WM_NCCALCSIZE = 0x0083
WM_NCHITTEST = 0x0084
# hit-test results
HTCLIENT = 1
HTCAPTION = 2
HTLEFT = 10
HTRIGHT = 11
HTTOP = 12
HTTOPLEFT = 13
HTTOPRIGHT = 14
HTBOTTOM = 15
HTBOTTOMLEFT = 16
HTBOTTOMRIGHT = 17


class TitleBar(QWidget):
    def __init__(self, win: "MainWindow"):
        super().__init__(win)
        self.win = win
        self.setObjectName("TitleBar")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setFixedHeight(TITLE_H)
        self._drag = None

        h = QHBoxLayout(self)
        h.setContentsMargins(8, 0, 6, 0)
        h.setSpacing(8)

        self.gear = QToolButton()
        self.gear.setObjectName("TitleBtn")
        self.gear.setIcon(icons.icon("gear", "#ffffff", 22))
        self.gear.setIconSize(self.gear.sizeHint())
        self.gear.setToolTip("设置")
        self.gear.clicked.connect(win.show_settings)
        h.addWidget(self.gear)

        self.tab = QToolButton()
        self.tab.setObjectName("TabBtn")
        self.tab.setIcon(icons.icon("tab", "#124678", 24))
        self.tab.setFixedSize(64, 30)
        self.tab.clicked.connect(win.show_working)
        h.addWidget(self.tab, 0, Qt.AlignBottom)

        h.addStretch(1)
        title = QLabel("基于改进FPN的内镜息肉识别临床决策系统")
        title.setObjectName("AppTitle")
        h.addWidget(title)
        h.addStretch(1)

        self.btn_min = QToolButton()
        self.btn_min.setObjectName("TitleBtn")
        self.btn_min.setIcon(icons.icon("min", "#ffffff", 24))
        self.btn_min.clicked.connect(win.showMinimized)
        self.btn_max = QToolButton()
        self.btn_max.setObjectName("TitleBtn")
        self.btn_max.setIcon(icons.icon("max", "#ffffff", 24))
        self.btn_max.clicked.connect(win.toggle_max)
        self.btn_close = QToolButton()
        self.btn_close.setObjectName("CloseBtn")
        self.btn_close.setIcon(icons.icon("close", "#ffffff", 24))
        self.btn_close.clicked.connect(win.close)
        for b in (self.btn_min, self.btn_max, self.btn_close):
            b.setFixedSize(40, 28)
            h.addWidget(b)

    def update_max_icon(self):
        name = "restore" if self.win.isMaximized() else "max"
        self.btn_max.setIcon(icons.icon(name, "#ffffff", 24))

    def child_is_button(self, pos: QPoint) -> bool:
        child = self.childAt(pos)
        while child is not None and child is not self:
            if isinstance(child, QAbstractButton):
                return True
            child = child.parentWidget()
        return False

    # Fallback drag for non-Windows platforms (Windows uses native HTCAPTION).
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._drag = e.globalPosition().toPoint() - self.win.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if self._drag is not None and e.buttons() & Qt.LeftButton and not self.win.isMaximized():
            self.win.move(e.globalPosition().toPoint() - self._drag)

    def mouseReleaseEvent(self, e):
        self._drag = None

    def mouseDoubleClickEvent(self, e):
        self.win.toggle_max()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("基于改进FPN的内镜息肉识别临床决策系统")
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self._native_ready = False

        central = QWidget()
        self.setCentralWidget(central)
        v = QVBoxLayout(central)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)

        self.title_bar = TitleBar(self)
        v.addWidget(self.title_bar)

        self.stack = QStackedWidget()
        v.addWidget(self.stack, 1)

        self.working = WorkingView()
        self.settings = SettingsView()
        self.settings.back_requested.connect(self.show_working)
        self.stack.addWidget(self.working)
        self.stack.addWidget(self.settings)
        self.stack.setCurrentWidget(self.working)

        # Items are allowed to just touch (gap=0) at minimum width — no visual
        # overlap, but as compact as possible.
        header_min = self.working.header.minimum_width(min_gap=0)
        min_w = max(1024, header_min)
        self.setMinimumSize(min_w, 600)
        self.resize(max(1200, min_w + 40), 740)

    def show_settings(self):
        self.stack.setCurrentWidget(self.settings)

    def show_working(self):
        self.stack.setCurrentWidget(self.working)

    def toggle_max(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
        self.title_bar.update_max_icon()

    def changeEvent(self, e):
        super().changeEvent(e)
        if hasattr(self, "title_bar"):
            self.title_bar.update_max_icon()

    def showEvent(self, e):
        super().showEvent(e)
        if sys.platform == "win32" and not self._native_ready:
            self._native_ready = True
            self._enable_native_window()

    def _enable_native_window(self):
        try:
            import ctypes

            hwnd = int(self.winId())
            user32 = ctypes.windll.user32
            get_long = getattr(user32, "GetWindowLongPtrW", user32.GetWindowLongW)
            set_long = getattr(user32, "SetWindowLongPtrW", user32.SetWindowLongW)
            style = get_long(hwnd, GWL_STYLE)
            style |= WS_CAPTION | WS_THICKFRAME | WS_MINIMIZEBOX | WS_MAXIMIZEBOX
            set_long(hwnd, GWL_STYLE, style)
            # SWP_NOMOVE|SWP_NOSIZE|SWP_NOZORDER|SWP_FRAMECHANGED
            user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, 0x0027)
        except Exception:
            pass

    def nativeEvent(self, event_type, message):
        if sys.platform == "win32" and event_type == b"windows_generic_MSG":
            try:
                import ctypes
                from ctypes import wintypes

                msg = wintypes.MSG.from_address(int(message))
                if msg.message == WM_NCCALCSIZE and msg.wParam:
                    # client area fills the whole window (no native frame)
                    return True, 0
                if msg.message == WM_NCHITTEST:
                    gx = ctypes.c_short(msg.lParam & 0xFFFF).value
                    gy = ctypes.c_short((msg.lParam >> 16) & 0xFFFF).value
                    pt = self.mapFromGlobal(QPoint(gx, gy))
                    x, y = pt.x(), pt.y()
                    w, h = self.width(), self.height()
                    if not self.isMaximized():
                        left, right = x < BORDER, x > w - BORDER
                        top, bottom = y < BORDER, y > h - BORDER
                        if top and left:
                            return True, HTTOPLEFT
                        if top and right:
                            return True, HTTOPRIGHT
                        if bottom and left:
                            return True, HTBOTTOMLEFT
                        if bottom and right:
                            return True, HTBOTTOMRIGHT
                        if left:
                            return True, HTLEFT
                        if right:
                            return True, HTRIGHT
                        if top:
                            return True, HTTOP
                        if bottom:
                            return True, HTBOTTOM
                    if 0 <= y < TITLE_H:
                        tb_pt = self.title_bar.mapFrom(self, pt)
                        if not self.title_bar.child_is_button(tb_pt):
                            return True, HTCAPTION
                    return True, HTCLIENT
            except Exception:
                pass
        return super().nativeEvent(event_type, message)
