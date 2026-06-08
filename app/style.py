"""Shared colors and the global QSS stylesheet."""
import os
import tempfile

# palette sampled directly from the reference screenshots
TITLE_BLUE = "#124678"
TITLE_BLUE_DARK = "#0e3a66"
TOOLBAR_BG = "#ffffff"
WORK_AREA_BG = "#808080"
CARD_HEADER = "#ae471e"
CARD_HEADER_SEL = "#1f3a5f"
CARD_BODY = "#e0e0e0"
CARD_FOOTER = "#d1d1d1"
FOOTER_GREY = "#e0e0e0"
FOOTER_BLUE = "#133b76"
SIDEBAR_BLUE = "#133b76"
SETTINGS_BG = "#e6e8ea"
ACCENT_BLUE = "#15528c"
TABLE_HEADER = "#2c5f9e"
ERROR_RED = "#d0021b"
TURQUOISE = "#3fb6b6"

# near-black toolbar glyphs and the dark mini-button (查询/清除所有)
ACTIVE_ICON = "#272727"
DISABLED_ICON = "#bdbdbd"
DARK_BTN = "#2c2c2c"

_QSS_TEMPLATE = f"""
* {{
    font-family: "Microsoft YaHei", "微软雅黑", "Segoe UI", sans-serif;
    font-size: 12px;
    color: #2b2b2b;
}}

/* ---- title bar ---- */
#TitleBar {{
    background: {TITLE_BLUE};
}}
#TitleBar QLabel#AppTitle {{
    color: #ffffff;
    font-size: 13px;
}}
QToolButton#TitleBtn {{
    background: transparent;
    border: none;
    border-radius: 4px;
    padding: 3px;
}}
QToolButton#TitleBtn:hover {{
    background: rgba(255,255,255,0.18);
}}
QToolButton#CloseBtn:hover {{
    background: #d04545;
}}
QToolButton#TabBtn {{
    background: #ffffff;
    border: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}}

/* ---- toolbar ---- */
#Toolbar {{
    background: {TOOLBAR_BG};
    border-bottom: 1px solid #cfd2d5;
}}
/* header icon button: hover frame wraps the icon only */
QToolButton#IconBtn {{
    background: transparent;
    border: none;
    border-radius: 6px;
}}
QToolButton#IconBtn:hover:enabled {{
    background: #d0d2d4;
}}

QLineEdit#SearchBox {{
    background: #ffffff;
    border: 1px solid #b9bdc2;
    border-radius: 2px;
    padding: 3px 6px;
}}
QComboBox#FilterCombo {{
    background: #ffffff;
    border: 1px solid #b9bdc2;
    border-radius: 2px;
    padding: 2px 6px;
}}

/* ---- work area ---- */
#WorkArea {{
    background: {WORK_AREA_BG};
}}
QScrollArea {{ border: none; background: transparent; }}

/* ---- footers ---- */
#GreyFooter {{
    background: {FOOTER_GREY};
    border-top: 1px solid #d2d5d8;
}}
#BlueFooter {{
    background: {FOOTER_BLUE};
}}
#BlueFooter QLabel {{ color: #dfe6f0; }}
QToolButton#ViewBtn {{
    background: transparent; border: none; border-radius: 4px; padding: 3px;
}}
QToolButton#ViewBtn:hover {{ background: rgba(255,255,255,0.15); }}
QToolButton#ViewBtn:checked {{ background: rgba(255,255,255,0.28); }}

/* ---- generic buttons ---- */
QPushButton.primary {{
    background: {ACCENT_BLUE};
    color: #ffffff;
    border: none;
    border-radius: 2px;
    padding: 6px 16px;
}}
QPushButton.primary:hover {{ background: #2a5fa0; }}
QPushButton.primary:disabled {{ background: #9bb0c9; }}

/* dark mini button used by 清除所有 */
QPushButton.darkbtn {{
    background: {DARK_BTN};
    color: #ffffff;
    border: none;
    border-radius: 2px;
    padding: 3px 12px;
}}
QPushButton.darkbtn:hover {{ background: #3c3c3c; }}
QPushButton.darkbtn:disabled {{ background: #9a9a9a; }}

/* flat text control used by 查询 */
QPushButton.flatbtn {{
    background: transparent;
    color: #404040;
    border: none;
    padding: 2px 6px;
}}
QPushButton.flatbtn:hover {{ color: #111111; }}

/* ---- dialogs ---- */
#Dialog {{ background: #f0f1f3; border: 1px solid #b8bcc1; }}
#DialogHeader {{ background: {TITLE_BLUE}; }}
#DialogHeader QLabel {{ color: #ffffff; font-size: 13px; }}

QLineEdit, QComboBox, QPlainTextEdit, QDateEdit {{
    background: #ffffff;
    border: 1px solid #b9bdc2;
    border-radius: 2px;
    padding: 2px 4px;
}}
QLineEdit:focus, QComboBox:focus, QPlainTextEdit:focus, QDateEdit:focus {{
    border: 1px solid #4f86c6;
}}
QLineEdit[invalid="true"], QComboBox[invalid="true"], QDateEdit[invalid="true"] {{
    border: 1px solid {ERROR_RED};
}}

/* classic boxed dropdown button + triangle for combos and date fields */
QComboBox::drop-down, QDateEdit::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 17px;
    border-left: 1px solid #b9bdc2;
    background: #e6e8ea;
}}
QComboBox::drop-down:hover, QDateEdit::drop-down:hover {{
    background: #d6d9dc;
}}
QComboBox::down-arrow, QDateEdit::down-arrow {{
    image: url(__ARROW__);
    width: 9px;
    height: 9px;
}}
QComboBox::down-arrow:on {{ top: 1px; }}

QLabel.req {{ color: {ERROR_RED}; }}
QLabel.errortext {{ color: {ERROR_RED}; }}

/* form tabs at top of profile dialog */
QPushButton#FormTabActive {{
    background: {TITLE_BLUE};
    color: #ffffff;
    border: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    padding: 9px 34px;
    font-size: 13px;
}}
QPushButton#FormTabInactive {{
    background: #cfd3d8;
    color: #555;
    border: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    padding: 9px 34px;
    font-size: 13px;
}}

/* ---- settings ---- */
#Sidebar {{ background: {SIDEBAR_BLUE}; }}
#Sidebar QPushButton {{
    background: transparent; color: #cdd6e3; border: none;
    text-align: center; padding: 12px 0;
}}
#Sidebar QPushButton:hover {{ background: rgba(255,255,255,0.08); }}
#Sidebar QPushButton:checked {{ background: {SETTINGS_BG}; color: {SIDEBAR_BLUE}; }}
#SettingsArea {{ background: {SETTINGS_BG}; }}
#SettingsArea QLabel.h1 {{ color: {ACCENT_BLUE}; font-size: 15px; font-weight: bold; }}
#SettingsArea QLabel.h2 {{ color: {ACCENT_BLUE}; font-size: 13px; font-weight: bold; }}
#SettingsArea QLabel.sub {{ color: #8a8f95; }}

QTableWidget {{
    background: #ffffff;
    gridline-color: #d9dce0;
    border: 1px solid #c4c8cc;
}}
QHeaderView::section {{
    background: {TABLE_HEADER};
    color: #ffffff;
    border: none;
    padding: 4px;
}}
QTableWidget::item:selected {{ background: #cfe0f3; color: #2b2b2b; }}
"""


def _write_down_arrow() -> str:
    """Render the dropdown triangle to a temp PNG and return its url-safe path."""
    from PySide6.QtCore import QPointF, Qt
    from PySide6.QtGui import QColor, QPainter, QPixmap, QPolygonF

    path = os.path.join(tempfile.gettempdir(), "rcvue_down_arrow.png")
    pm = QPixmap(18, 18)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing, True)
    p.setPen(Qt.NoPen)
    p.setBrush(QColor("#3a3a3a"))
    p.drawPolygon(QPolygonF([QPointF(4, 6), QPointF(14, 6), QPointF(9, 12)]))
    p.end()
    pm.save(path)
    return path.replace("\\", "/")


def build_qss() -> str:
    """Return the full stylesheet (call after the QApplication exists)."""
    return _QSS_TEMPLATE.replace("__ARROW__", _write_down_arrow())

