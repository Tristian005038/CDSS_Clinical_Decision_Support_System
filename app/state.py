"""In-memory application state and signals.

All data lives only for the session (nothing is persisted to disk).
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

from PySide6.QtCore import QObject, Signal


class AppState(QObject):
    profiles_changed = Signal()
    selection_changed = Signal()
    doctors_changed = Signal()
    users_changed = Signal()
    settings_changed = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.profiles: list[dict] = []
        self._next_id = 1

        # selection holds profile ids currently selected (grid: single, list: many)
        self.selected_ids: set[int] = set()

        # users for the settings user-management table (starts empty)
        self.users: list[dict] = []

        # doctor names that feed the form dropdowns (申请人员 / 操作人员 / 报告人员)
        self.doctors: list[dict] = []  # {"name": str, "type": str, "signature": str|None}

        # hospital data
        self.hospital = {"name": "", "second_name": "", "phone": "", "logo": None}

        # application settings
        self.settings = {
            "data_path": r"C:\Case",
            "date_format": "yyyy/MM/dd",
            "input_date": "年份",
            "display_date": "年份",
            "marker_color": "#ffffff",
            "line_thickness": "------",
            "opt_patient_info": True,
            "opt_shutdown": False,
            "opt_delete_after": False,
            "opt_open_after": True,
        }

    # ----- profiles -----
    def add_profile(self, data: dict) -> dict:
        data = dict(data)
        data["id"] = self._next_id
        self._next_id += 1
        if "rating" not in data:
            data["rating"] = 0
        self.profiles.append(data)
        self.profiles_changed.emit()
        return data

    def update_profile(self, pid: int, data: dict) -> None:
        for i, p in enumerate(self.profiles):
            if p["id"] == pid:
                merged = dict(p)
                merged.update(data)
                merged["id"] = pid
                self.profiles[i] = merged
                break
        self.profiles_changed.emit()

    def delete_profiles(self, ids) -> None:
        ids = set(ids)
        self.profiles = [p for p in self.profiles if p["id"] not in ids]
        self.selected_ids -= ids
        self.profiles_changed.emit()
        self.selection_changed.emit()

    def get_profile(self, pid: int):
        for p in self.profiles:
            if p["id"] == pid:
                return p
        return None

    # ----- selection -----
    def set_selection(self, ids) -> None:
        self.selected_ids = set(ids)
        self.selection_changed.emit()

    def clear_selection(self) -> None:
        if self.selected_ids:
            self.selected_ids = set()
            self.selection_changed.emit()

    # ----- users -----
    def user_names(self) -> list[str]:
        """用户名称 values that drive 操作人员 / 申请人员 / 报告人员 dropdowns."""
        return [u["username"] for u in self.users if u.get("username")]

    # ----- doctors -----
    def doctor_names(self) -> list[str]:
        return [d["name"] for d in self.doctors]

    def add_doctor(self, name: str, dtype: str, signature=None) -> None:
        self.doctors.append({"name": name, "type": dtype, "signature": signature})
        self.doctors_changed.emit()

    def remove_doctor(self, index: int) -> None:
        if 0 <= index < len(self.doctors):
            del self.doctors[index]
            self.doctors_changed.emit()

    # ----- derived counts -----
    @property
    def total_profiles(self) -> int:
        return len(self.profiles)

    @property
    def ungenerated_reports(self) -> int:
        # No report-generation feature: every profile counts as one ungenerated report.
        return len(self.profiles)

    def disk_space(self):
        """Return (free_bytes, total_bytes) for the drive where the app lives."""
        try:
            base = Path(sys.argv[0]).resolve().anchor or Path.cwd().anchor
            usage = shutil.disk_usage(base or ".")
            return usage.free, usage.total
        except Exception:
            return 0, 0


state = AppState()
