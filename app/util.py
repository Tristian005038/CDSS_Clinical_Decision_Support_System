"""Small shared helpers."""
from __future__ import annotations

from PySide6.QtCore import QDate

from app.state import state


def format_date(value) -> str:
    if isinstance(value, QDate):
        return value.toString(state.settings["date_format"])
    if value:
        return str(value)
    return ""


def human_size(num_bytes: int) -> str:
    if num_bytes <= 0:
        return "0G"
    gb = num_bytes / (1024 ** 3)
    if gb >= 1:
        return f"{gb:.0f}G"
    mb = num_bytes / (1024 ** 2)
    return f"{mb:.0f}M"
