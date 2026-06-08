"""科室与医生管理 popup: manage doctor names that feed the form dropdowns."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
)

from app import style
from app.dialogs.base import FramelessDialog
from app.dialogs.confirm_dialog import ConfirmDialog
from app.state import state


class SignatureBox(QLabel):
    """Double-click to pick an image, scaled to fit the box."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 70)
        self.setAlignment(Qt.AlignCenter)
        self.setText("双击选择医生签名")
        self.setStyleSheet("background:#2b2b2b; color:#ffffff; border:1px solid #555;")
        self._path = None

    def mouseDoubleClickEvent(self, e):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择签名图片", "", "图片 (*.png *.jpg *.jpeg *.gif *.bmp)")
        if path:
            self._path = path
            pm = QPixmap(path).scaled(
                self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.setPixmap(pm)


class ManageDoctorDialog(FramelessDialog):
    def __init__(self, parent=None):
        super().__init__("科室与医生管理", parent)
        root = QVBoxLayout(self.body)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(10)

        title = QLabel("科室与医生管理")
        title.setStyleSheet(f"color:{style.ACCENT_BLUE}; font-weight:bold;")
        root.addWidget(title)
        sub = QLabel("添加/或删除科室和科室医生")
        sub.setStyleSheet("color:#8a8f95;")
        root.addWidget(sub)

        add_lbl = QLabel("添加 医生")
        add_lbl.setStyleSheet(f"color:{style.ACCENT_BLUE}; font-weight:bold;")
        root.addWidget(add_lbl)

        form = QHBoxLayout()
        left = QVBoxLayout()
        r1 = QHBoxLayout()
        r1.addWidget(QLabel("选择项"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["医生", "操作人员", "申请人员", "报告人员"])
        self.type_combo.setFixedWidth(140)
        r1.addWidget(self.type_combo)
        r1.addStretch(1)
        left.addLayout(r1)
        r2 = QHBoxLayout()
        r2.addWidget(QLabel("医生 名称"))
        self.name_edit = QLineEdit()
        self.name_edit.setFixedWidth(160)
        r2.addWidget(self.name_edit)
        r2.addStretch(1)
        left.addLayout(r2)
        save = QPushButton("保存")
        save.setProperty("class", "primary")
        save.setFixedWidth(80)
        save.clicked.connect(self._add)
        left.addWidget(save)
        left.addStretch(1)
        form.addLayout(left, 1)

        right = QVBoxLayout()
        hint = QLabel("建议导入大小为200*70px，类型为jpg、png、gif、bmp的图片")
        hint.setStyleSheet("color:#8a8f95;")
        hint.setWordWrap(True)
        right.addWidget(hint)
        self.sig_box = SignatureBox()
        right.addWidget(self.sig_box)
        right.addStretch(1)
        form.addLayout(right, 1)
        root.addLayout(form)

        list_title = QLabel("医生 名称")
        list_title.setAlignment(Qt.AlignCenter)
        list_title.setStyleSheet("background:#6b7886; color:#ffffff; padding:4px;")
        root.addWidget(list_title)
        self.list = QListWidget()
        self.list.setFixedHeight(150)
        self.list.itemClicked.connect(self._on_select)
        root.addWidget(self.list)

        self.del_btn = QPushButton("删除")
        self.del_btn.setFixedWidth(70)
        self.del_btn.clicked.connect(self._delete)
        root.addWidget(self.del_btn)

        self.setMinimumWidth(560)
        self._reload()

    def _reload(self):
        self.list.clear()
        for d in state.doctors:
            self.list.addItem(QListWidgetItem(d["name"]))

    def _add(self):
        name = self.name_edit.text().strip()
        if not name:
            return
        state.add_doctor(name, self.type_combo.currentText(), self.sig_box._path)
        self.name_edit.clear()
        self._reload()

    def _on_select(self, item):
        for i in range(self.list.count()):
            self.list.item(i).setBackground(QColor("white"))
        item.setBackground(QColor(style.TURQUOISE))

    def _delete(self):
        row = self.list.currentRow()
        if row < 0:
            return
        if ConfirmDialog.ask(self, "确定删除选中的医生?", "提示"):
            state.remove_doctor(row)
            self._reload()
