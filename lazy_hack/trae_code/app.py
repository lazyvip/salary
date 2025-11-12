import os
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QMainWindow, QWidget, QTabWidget, QHBoxLayout, QSpinBox, QComboBox, QPlainTextEdit
from PyQt6.QtCore import Qt
from license_manager import LicenseManager, get_data_path, write_cached_uuid, read_cached_uuid

class LicenseDialog(QDialog):
    def __init__(self, manager: LicenseManager):
        super().__init__()
        self.manager = manager
        self.setWindowTitle("授权验证")
        layout = QVBoxLayout()
        self.machine_label = QLabel(f"机器码: {self.manager.machine_id[:16]}...")
        self.machine_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.input = QLineEdit()
        self.input.setPlaceholderText("输入授权码")
        self.btn_validate = QPushButton("验证")
        self.btn_activate = QPushButton("激活")
        layout.addWidget(self.machine_label)
        layout.addWidget(self.input)
        layout.addWidget(self.btn_validate)
        layout.addWidget(self.btn_activate)
        self.setLayout(layout)
        self.btn_validate.clicked.connect(self.on_validate)
        self.btn_activate.clicked.connect(self.on_activate)

    def on_validate(self):
        status, data = self.manager.validate()
        if status == "valid":
            uuid = self.manager.machine_id
            write_cached_uuid(uuid)
            QMessageBox.information(self, "成功", "授权有效")
            self.accept()
        elif status == "not_activated":
            QMessageBox.warning(self, "未激活", str(data.get("message", "未激活")))
        else:
            QMessageBox.warning(self, "错误", str(data.get("message", "验证失败")))

    def on_activate(self):
        key = self.input.text().strip()
        ok, res = self.manager.activate(key)
        if ok:
            QMessageBox.information(self, "成功", str(res if isinstance(res, str) else res.get("message", "激活成功")))
        else:
            msg = res if isinstance(res, str) else res.get("message", "激活失败")
            QMessageBox.warning(self, "失败", str(msg))

class MainWindow(QMainWindow):
    def __init__(self, status_data: dict | None = None, machine_id: str | None = None):
        super().__init__()
        self.setWindowTitle("AI批量生图工具")
        tabs = QTabWidget()
        gen = QWidget()
        gen_layout = QVBoxLayout()
        self.prompt = QLineEdit()
        self.prompt.setPlaceholderText("输入提示词")
        ctrl_row = QWidget()
        ctrl_layout = QHBoxLayout()
        self.count = QSpinBox()
        self.count.setRange(1, 999)
        self.count.setValue(4)
        self.w = QSpinBox(); self.w.setRange(64, 4096); self.w.setValue(512)
        self.h = QSpinBox(); self.h.setRange(64, 4096); self.h.setValue(512)
        self.model = QComboBox(); self.model.addItems(["默认模型", "模型A", "模型B"])
        self.start_btn = QPushButton("开始生成")
        ctrl_layout.addWidget(QLabel("数量")); ctrl_layout.addWidget(self.count)
        ctrl_layout.addWidget(QLabel("宽")); ctrl_layout.addWidget(self.w)
        ctrl_layout.addWidget(QLabel("高")); ctrl_layout.addWidget(self.h)
        ctrl_layout.addWidget(QLabel("模型")); ctrl_layout.addWidget(self.model)
        ctrl_layout.addWidget(self.start_btn)
        ctrl_row.setLayout(ctrl_layout)
        self.log = QPlainTextEdit(); self.log.setReadOnly(True)
        gen_layout.addWidget(self.prompt)
        gen_layout.addWidget(ctrl_row)
        gen_layout.addWidget(self.log)
        gen.setLayout(gen_layout)
        settings = QWidget()
        set_layout = QVBoxLayout()
        self.lic_label = QLabel("授权信息")
        if status_data and isinstance(status_data, dict) and status_data.get("expires_at"):
            self.lic_label.setText(f"授权有效至: {status_data.get('expires_at')}")
        elif machine_id:
            self.lic_label.setText(f"机器码: {machine_id}")
        set_layout.addWidget(self.lic_label)
        settings.setLayout(set_layout)
        tabs.addTab(gen, "批量生图")
        tabs.addTab(settings, "设置")
        self.setCentralWidget(tabs)
        self.start_btn.clicked.connect(self.on_start)

    def on_start(self):
        p = self.prompt.text().strip()
        c = self.count.value()
        w = self.w.value()
        h = self.h.value()
        m = self.model.currentText()
        self.log.appendPlainText(f"生成任务: 提示='{p}', 数量={c}, 分辨率={w}x{h}, 模型={m}")

def main():
    app = QApplication(sys.argv)
    manager = LicenseManager()
    cached = read_cached_uuid()
    if cached:
        status, data = manager.validate()
        if status == "valid":
            w = MainWindow(status_data=data, machine_id=manager.machine_id)
            w.resize(640, 360)
            w.show()
            sys.exit(app.exec())
    dlg = LicenseDialog(manager)
    if dlg.exec() == QDialog.DialogCode.Accepted:
        status, data = manager.validate()
        w = MainWindow(status_data=data if status == "valid" else None, machine_id=manager.machine_id)
        w.resize(640, 360)
        w.show()
        sys.exit(app.exec())

if __name__ == "__main__":
    main()
