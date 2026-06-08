"""RCVue desktop clone - application entry point."""
from __future__ import annotations

import sys

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from app.style import build_qss
from app.window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setStyleSheet(build_qss())
    app.setFont(QFont("Microsoft YaHei", 9))

    win = MainWindow()
    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
