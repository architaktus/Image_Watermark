
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QCheckBox, QTabWidget,
    QFileDialog, QGroupBox
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class WatermarkApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Watermark Tool")
        self.setGeometry(100, 100, 800, 600)

        # Main Layout
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Embed Watermark Tab
        self.embed_tab = QWidget()
        self.tabs.addTab(self.embed_tab, "Embed Watermark")

        # Read Watermark Tab
        self.read_tab = QWidget()
        self.tabs.addTab(self.read_tab, "Read Watermark")

        # Initialize Tabs
        self.init_embed_tab()
        self.init_read_tab()

    # 嵌入水印
    def init_embed_tab(self):
        layout = QVBoxLayout()

        # Preview Area
        self.preview_label = QLabel("Image Preview", self)
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("border: 1px solid red;")
        layout.addWidget(self.preview_label)

        # Options Section
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout()

        self.text_input = QLineEdit("Default Watermark Text")
        options_layout.addWidget(QLabel("Watermark Text:"))
        options_layout.addWidget(self.text_input)

        self.opacity_checkbox = QCheckBox("Transparent Watermark")
        options_layout.addWidget(self.opacity_checkbox)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Buttons Section
        button_layout = QHBoxLayout()
        self.open_button = QPushButton("Open Image")
        self.save_button = QPushButton("Save Image")
        self.embed_button = QPushButton("Embed Watermark")

        button_layout.addWidget(self.open_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.embed_button)

        layout.addLayout(button_layout)
        self.embed_tab.setLayout(layout)

        # Button Functionality
        self.open_button.clicked.connect(self.open_image)
        self.embed_button.clicked.connect(self.embed_watermark)

    # 读取水印
    def init_read_tab(self):
        layout = QVBoxLayout()

        # Preview Area
        self.read_preview_label = QLabel("Image Preview", self)
        self.read_preview_label.setAlignment(Qt.AlignCenter)
        self.read_preview_label.setStyleSheet("border: 1px solid red;")
        layout.addWidget(self.read_preview_label)

        # Read-only Information Section
        self.read_info_label = QLabel("Detected Watermark: None")
        self.read_info_label.setStyleSheet("border: 1px solid gray;")
        layout.addWidget(self.read_info_label)

        # Buttons Section
        button_layout = QHBoxLayout()
        self.open_read_button = QPushButton("Open Image")
        self.read_watermark_button = QPushButton("Read Watermark")

        button_layout.addWidget(self.open_read_button)
        button_layout.addWidget(self.read_watermark_button)

        layout.addLayout(button_layout)
        self.read_tab.setLayout(layout)

        # Button Functionality
        self.open_read_button.clicked.connect(self.open_image_read)
        self.read_watermark_button.clicked.connect(self.read_watermark)

    def open_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg *.jpeg)")
        if file_name:
            pixmap = QPixmap(file_name)
            self.preview_label.setPixmap(pixmap.scaled(self.preview_label.size(), Qt.KeepAspectRatio))

    def embed_watermark(self):
        watermark_text = self.text_input.text()
        print(f"Embedding watermark: {watermark_text}")
        # Placeholder for embedding logic

    def open_image_read(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg *.jpeg)")
        if file_name:
            pixmap = QPixmap(file_name)
            self.read_preview_label.setPixmap(pixmap.scaled(self.read_preview_label.size(), Qt.KeepAspectRatio))

    def read_watermark(self):
        print("Reading watermark...")
        # Placeholder for reading logic
        self.read_info_label.setText("Detected Watermark: Example Watermark")