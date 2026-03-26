import sys, os, ipaddress
from PySide6.QtWidgets import (QApplication, QMainWindow, QComboBox, QToolBar, QWidget,
                               QLabel, QSlider, QGridLayout, QHBoxLayout, QPushButton, 
                               QSpinBox, QFileDialog, QTextEdit, QLineEdit, QSizePolicy)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

class GlassTheme:
    @staticmethod
    def get_style(is_dark):
        base_dir = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
        font_family = "font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;"
        log_css = "QTextEdit { background-color: #050505; border: 1px solid #444; border-radius: 8px; color: #e2e8f0; padding: 12px; font-family: Consolas, monospace; font-size: 13px; }"
        
        if is_dark:
            slider_css = "QSlider { min-height: 30px; } QSlider::groove:horizontal { border: 1px solid #555; background: #333; height: 6px; border-radius: 3px; } QSlider::sub-page:horizontal { background: #007aff; height: 6px; border-radius: 3px; } QSlider::handle:horizontal { background: #ccc; border: 1px solid #222; width: 16px; height: 16px; margin: -6px 0; border-radius: 8px; } QSlider::handle:horizontal:hover { background: #007aff; border: 1px solid white; }"
            return f"""
                QMainWindow {{ background-color: #1e1e1e; {font_family} }}
                QLabel {{ color: #ffffff; font-weight: 500; font-size: 13px; background: transparent; }}
                QToolBar {{ background-color: #2b2b2b; border-bottom: 1px solid #444; padding: 8px; }}
                QPushButton {{ background-color: #333333; border: 1px solid #555555; border-radius: 4px; color: white; padding: 6px 14px; font-weight: 500; font-size: 13px; }}
                QPushButton:hover {{ background-color: #444446; border: 1px solid #007aff; color: #007aff; }}
                #PicArea {{ background-color: #2b2b2b; border: 1px solid #444; border-radius: 8px; }}
                QLineEdit, QSpinBox, QComboBox {{ background-color: #2b2b2b; border: 1px solid #555; border-radius: 4px; color: white; padding: 4px 8px; font-size: 13px; }}
                QLineEdit:hover, QSpinBox:hover, QComboBox:hover {{ border: 1px solid #007aff; background-color: #252525; }}
                QComboBox {{ padding-right: 24px; }}
                QComboBox::drop-down {{ subcontrol-origin: padding; subcontrol-position: top right; width: 24px; border-left: 1px solid #555; background: #333; border-top-right-radius: 3px; border-bottom-right-radius: 3px; }}
                QComboBox::drop-down:hover {{ background-color: #007aff; }}
                QComboBox::down-arrow {{ image: url("{base_dir}/white-down-arrow-svgrepo-com.svg"); width: 14px; height: 14px; }}
                QComboBox QAbstractItemView {{ background-color: #2b2b2b; color: white; selection-background-color: #007aff; selection-color: white; border: 1px solid #555; outline: none; }}
                QSpinBox {{ padding-right: 24px; }}
                QSpinBox::up-button, QSpinBox::down-button {{ subcontrol-origin: border; width: 22px; background: #333; border-left: 1px solid #555; }}
                QSpinBox::up-button:hover, QSpinBox::down-button:hover {{ background-color: #007aff; }}
                QSpinBox::up-button {{ subcontrol-position: top right; border-top-right-radius: 3px; }}
                QSpinBox::down-button {{ subcontrol-position: bottom right; border-bottom-right-radius: 3px; border-top: 1px solid #555; }}
                QSpinBox::up-arrow {{ image: url("{base_dir}/white-up-arrow-svgrepo-com.svg"); width: 12px; height: 12px; }}
                QSpinBox::down-arrow {{ image: url("{base_dir}/white-down-arrow-svgrepo-com.svg"); width: 12px; height: 12px; }}
                {slider_css} {log_css}
            """
        else:
            slider_css = "QSlider { min-height: 30px; } QSlider::groove:horizontal { border: 1px solid #ccc; background: #eee; height: 6px; border-radius: 3px; } QSlider::sub-page:horizontal { background: #007aff; height: 6px; border-radius: 3px; } QSlider::handle:horizontal { background: white; border: 1px solid #999; width: 16px; height: 16px; margin: -6px 0; border-radius: 8px; } QSlider::handle:horizontal:hover { background: #f0f8ff; border: 1px solid #007aff; }"
            return f"""
                QMainWindow {{ background-color: #f5f5f7; {font_family} }}
                QLabel {{ color: #1d1d1f; font-weight: 500; font-size: 13px; background: transparent; }}
                QToolBar {{ background-color: #ffffff; border-bottom: 1px solid #d1d1d6; padding: 8px; }}
                QPushButton {{ background-color: #ffffff; border: 1px solid #b0b0b0; border-radius: 4px; color: #1d1d1f; padding: 6px 14px; font-weight: 500; font-size: 13px; }}
                QPushButton:hover {{ background-color: #f2f2f7; border: 1px solid #007aff; color: #007aff; }}
                #PicArea {{ background-color: #ffffff; border: 1px solid #d1d1d6; border-radius: 8px; }}
                QLineEdit, QSpinBox, QComboBox {{ background-color: white; border: 1px solid #b0b0b0; border-radius: 4px; color: black; padding: 4px 8px; font-size: 13px; }}
                QLineEdit:hover, QSpinBox:hover, QComboBox:hover {{ border: 1px solid #007aff; background-color: #fafafa; }}
                QComboBox {{ padding-right: 24px; }}
                QComboBox::drop-down {{ subcontrol-origin: padding; subcontrol-position: top right; width: 24px; border-left: 1px solid #b0b0b0; background: #f0f0f0; border-top-right-radius: 3px; border-bottom-right-radius: 3px; }}
                QComboBox::drop-down:hover {{ background-color: #007aff; }}
                QComboBox::down-arrow {{ image: url("{base_dir}/down-arrow-svgrepo-com.svg"); width: 14px; height: 14px; }}
                QComboBox QAbstractItemView {{ background-color: white; color: black; selection-background-color: #007aff; selection-color: white; border: 1px solid #b0b0b0; outline: none; }}
                QSpinBox {{ padding-right: 24px; }}
                QSpinBox::up-button, QSpinBox::down-button {{ subcontrol-origin: border; width: 22px; background: #f0f0f0; border-left: 1px solid #b0b0b0; }}
                QSpinBox::up-button:hover, QSpinBox::down-button:hover {{ background-color: #007aff; }}
                QSpinBox::up-button {{ subcontrol-position: top right; border-top-right-radius: 3px; }}
                QSpinBox::down-button {{ subcontrol-position: bottom right; border-bottom-right-radius: 3px; border-top: 1px solid #b0b0b0; }}
                QSpinBox::up-arrow {{ image: url("{base_dir}/up-arrow-svgrepo-com.svg"); width: 12px; height: 12px; }}
                QSpinBox::down-arrow {{ image: url("{base_dir}/down-arrow-svgrepo-com.svg"); width: 12px; height: 12px; }}
                {slider_css} {log_css}
            """

class UIBuilder:
    def __init__(self, main_window):
        self.mw = main_window
        self.build_toolbar()
        self.build_central_area()

    def build_toolbar(self):
        self.toolbar = QToolBar("Settings")
        self.toolbar.setMovable(False)
        self.mw.addToolBar(self.toolbar)
        self.protocol_combo = QComboBox()
        self.protocol_combo.addItems(["UDP", "TCP", "RUDP"])
        self.protocol_combo.setMinimumWidth(80)
        self.toolbar.addWidget(QLabel(" Transport Protocol: "))
        self.toolbar.addWidget(self.protocol_combo)
        spacer = QWidget()
        spacer.setFixedWidth(40)
        self.toolbar.addWidget(spacer)
        self.toolbar.addWidget(QLabel(" Chance of Corruption: "))
        self.corruption_slider = QSlider(Qt.Orientation.Horizontal)
        self.corruption_slider.setRange(0, 100)
        self.corruption_slider.setValue(5)
        self.corruption_slider.setFixedWidth(150)
        self.toolbar.addWidget(self.corruption_slider)
        self.corruption_label = QLabel(" 5%")
        self.corruption_label.setFixedWidth(45)
        self.toolbar.addWidget(self.corruption_label)
        expanding_spacer = QWidget()
        expanding_spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.toolbar.addWidget(expanding_spacer)
        self.theme_btn = QPushButton("Dark Mode")
        self.theme_btn.setFixedHeight(30)
        self.toolbar.addWidget(self.theme_btn)

    def build_central_area(self):
        central_widget = QWidget()
        self.mw.setCentralWidget(central_widget)
        self.grid = QGridLayout(central_widget)
        self.grid.setSpacing(15)
        self.grid.setContentsMargins(20, 20, 20, 20)
        self.pic_left = QLabel()
        self.pic_left.setObjectName("PicArea")
        self.pic_left.setMinimumHeight(280)
        self.pic_left.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        self.pic_right = QLabel()
        self.pic_right.setObjectName("PicArea")
        self.pic_right.setMinimumHeight(280)
        self.pic_right.setAlignment(Qt.AlignmentFlag.AlignCenter)

        left_port_container = QWidget()
        left_port_layout = QHBoxLayout(left_port_container)
        left_port_layout.addStretch() 
        self.ip_label = QLabel("IP Address:")
        self.ip_input = QLineEdit("127.0.0.1")
        self.ip_input.setFixedWidth(120)
        self.port_spacer = QLabel("  ")
        self.sender_port_input = QSpinBox()
        self.sender_port_input.setRange(1, 65535)
        self.sender_port_input.setValue(512)
        self.sender_port_input.setFixedWidth(90)
        
        for w in [self.ip_label, self.ip_input, self.port_spacer, QLabel("Port Number:"), self.sender_port_input]:
            left_port_layout.addWidget(w)
        left_port_layout.addStretch() 

        right_port_container = QWidget()
        right_port_layout = QHBoxLayout(right_port_container)
        right_port_layout.addStretch()
        self.rec_ip_label = QLabel("IP Address:")
        self.rec_ip_input = QLineEdit("127.0.0.1")
        self.rec_ip_input.setFixedWidth(120)
        self.rec_port_spacer = QLabel("  ")
        self.receiver_port_input = QSpinBox()
        self.receiver_port_input.setRange(1, 65535)
        self.receiver_port_input.setValue(123)
        self.receiver_port_input.setFixedWidth(90)
        
        for w in [self.rec_ip_label, self.rec_ip_input, self.rec_port_spacer, QLabel("Port Number:"), self.receiver_port_input]:
            right_port_layout.addWidget(w)
        right_port_layout.addStretch()

        self.ip_widgets = [self.ip_label, self.ip_input, self.port_spacer, self.rec_ip_label, self.rec_ip_input, self.rec_port_spacer]

        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.addStretch()
        self.select_file_btn = QPushButton("Select File")
        self.send_file_btn = QPushButton("Send File")
        buttons_layout.addWidget(self.select_file_btn)
        buttons_layout.addWidget(self.send_file_btn)
        buttons_layout.addStretch()

        self.log_left = QTextEdit()
        self.log_left.setReadOnly(True)
        self.log_left.setMinimumHeight(120)
        self.log_left.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)
        self.log_right = QTextEdit()
        self.log_right.setReadOnly(True)
        self.log_right.setMinimumHeight(120)
        self.log_right.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)

        self.grid.addWidget(self.pic_left, 0, 0)
        self.grid.addWidget(self.pic_right, 0, 1)
        self.grid.addWidget(left_port_container, 1, 0)
        self.grid.addWidget(right_port_container, 1, 1)
        self.grid.addWidget(buttons_container, 2, 0)
        self.grid.addWidget(self.log_left, 3, 0)
        self.grid.addWidget(self.log_right, 3, 1)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Network Transport Simulation")
        self.resize(900, 700)
        self.ui = UIBuilder(self)
        self.is_dark_mode = False
        self.selected_file_path = None 
        self.connect_signals()
        self.apply_theme() 
        self.toggle_ip_fields(self.ui.protocol_combo.currentText())

    def connect_signals(self):
        self.ui.theme_btn.clicked.connect(self.toggle_theme)
        self.ui.protocol_combo.currentTextChanged.connect(self.toggle_ip_fields)
        self.ui.corruption_slider.valueChanged.connect(self.update_corruption_label)
        self.ui.select_file_btn.clicked.connect(self.open_file)
        self.ui.send_file_btn.clicked.connect(self.simulate_send)

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.apply_theme()

    def apply_theme(self):
        self.setStyleSheet(GlassTheme.get_style(self.is_dark_mode))
        self.ui.theme_btn.setText("Light Mode" if self.is_dark_mode else "Dark Mode")

    def reset_logs(self):
        for log in (self.ui.log_left, self.ui.log_right):
            log.setText("<span style='color: white; font-weight: bold;'>Logs:</span>")
            log.setMinimumHeight(120)

    def append_log(self, widget, text, color="white"):
        widget.append(f"<span style='color: {color};'>{text}</span>")
        QApplication.processEvents()
        doc_height = int(widget.document().size().height()) + 25
        if doc_height > widget.minimumHeight():
            widget.setMinimumHeight(doc_height)

    def toggle_ip_fields(self, protocol_name):
        self.reset_logs()
        self.append_log(self.ui.log_left, f"~ Protocol switched to {protocol_name}", "#38bdf8")
        show_ip = protocol_name in ("UDP", "TCP", "RUDP")
        for w in self.ui.ip_widgets:
            w.setVisible(show_ip)

    def update_corruption_label(self, value):
        self.ui.corruption_label.setText(f" {value}%")

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            self.selected_file_path = file_path
            pixmap = QPixmap(file_path).scaled(
                self.ui.pic_left.width(), self.ui.pic_left.height(), 
                Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
            self.ui.pic_left.setPixmap(pixmap)
            self.reset_logs()
            self.append_log(self.ui.log_left, f"~ Image loaded: {os.path.basename(file_path)}", "#4ade80")

    def simulate_send(self):
        self.reset_logs()
        protocol = self.ui.protocol_combo.currentText()
        if not self.selected_file_path:
            self.append_log(self.ui.log_left, "~ ERROR: Please select an image first.", "#f87171")
            return

        if protocol in ("UDP", "TCP", "RUDP"):
            ip_text = self.ui.ip_input.text().strip()
            try:
                valid_ip = ipaddress.ip_address(ip_text)
                self.append_log(self.ui.log_left, f"~ IP Validated: {valid_ip}", "#4ade80")
            except ValueError:
                self.append_log(self.ui.log_left, f"~ ERROR: '{ip_text}' is not a valid IP Address.", "#f87171")
                return 

        self.append_log(self.ui.log_left, f"~ Starting {protocol} transmission to Port {self.ui.sender_port_input.value()}...", "#fbbf24")
        for i in range(1, 8):
            self.append_log(self.ui.log_left, f"~ Constructing packet sequence [{i}/7]...", "#94a3b8")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion") 
    window = MainWindow()
    window.show()
    sys.exit(app.exec())