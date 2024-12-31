
from PyQt5.QtWidgets import (
    QMainWindow, 
    QWidget, QTabWidget,
    QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QLineEdit, QCheckBox, QGroupBox, 
    QFileDialog, QFormLayout
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class WatermarkApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Watermark Tool")
        self.setGeometry(100, 100, 1000, 600)

        # Main Layout
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        self.setCentralWidget(main_widget)

        # Left Panel (Red Area)
        self.left_panel = self.init_left_panel()
        main_layout.addWidget(self.left_panel)

        # Tab Area (Yellow Area)
        self.tabs = QTabWidget()        
        self.tabs.addTab(self.init_embed_tab(), "Embed Watermark") # Embed Watermark Tab
        self.tabs.addTab(self.init_read_tab(), "Read Watermark") # Read Watermark Tab
        self.tabs.currentChanged.connect(self.update_left_panel)  # Update left panel based on the active tab
        main_layout.addWidget(self.tabs)


    # fixed left panel.
    def init_left_panel(self):
        left_panel = QGroupBox("Info")
        layout = QVBoxLayout()

        # Preview Area
        self.preview_label = QLabel("Image Preview", self)
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("border: 1px solid grey;")
        layout.addWidget(self.preview_label)

        # Info Panel
        # exif_group = QGroupBox("Info")        TODO 改为Panel
        self.filename_label = QLabel("Filename: None")
        self.resolution_label = QLabel("Resolution: N/A")
        self.exif_label = QLineEdit("Exif Data Here")
        self.exif_label.setReadOnly(True)              # Default read-only
        layout.addWidget(self.filename_label)
        layout.addWidget(self.resolution_label)
        layout.addWidget(self.exif_label)

        # button Panel
        self.update_button = QPushButton("Reload") #重新加载Exif
        # TODO 图片Exif + Database的数据如何协调？
        self.save_button = QPushButton("Save") #保存到database + 图片Exif
        layout.addWidget(self.update_button)
        layout.addWidget(self.save_button)

        left_panel.setLayout(layout)
        return left_panel

    #Initialize the Embed Watermark tab/嵌入水印的tab
    def init_embed_tab(self):
        embed_tab = QWidget()
        layout = QVBoxLayout()

        # Image Processing Section/ 压缩
        preprocess_group = QGroupBox("Image Preprocessing")
        preprocess_layout = QFormLayout()
        preprocess_layout.checkbox=QCheckBox("Resize to 2500px")
        preprocess_layout.checkbox.setChecked(True)
        preprocess_layout.addWidget(preprocess_layout.checkbox)
        preprocess_group.setLayout(preprocess_layout)
        layout.addWidget(preprocess_group)

        # Watermark Embedding Section: visible/ 可视水印
        watermark_group = QGroupBox("Visible Watermark")
        watermark_layout = QVBoxLayout()
        #TODO 下拉选择
        watermark_layout.checkbox_watermark = QCheckBox("Add Watermark")
        watermark_layout.checkbox_watermark.setChecked(True)
        watermark_layout.addWidget(watermark_layout.checkbox_watermark)
        watermark_layout.addWidget(QCheckBox("Embed visible Watermark only"))
        watermark_group.setLayout(watermark_layout)
        layout.addWidget(watermark_group)


        #####################################################
        # Watermark Embedding Section: Steganography/ 不可视水印
        steg_group = QGroupBox("Steganographical Watermark")
        steg_layout = QVBoxLayout()

        #相关固定信息
        steg_cal_group = QGroupBox("嵌入算法信息")
        steg_cal_layout = QVBoxLayout()
        self.label_alpha = QLineEdit("0.2")  #DWT Alpha
        steg_cal_layout.addWidget(self.label_alpha)
        steg_cal_group.setLayout(steg_cal_layout)
        steg_layout.addWidget(steg_cal_group)

        #关键信息组
        steg_key_group = QGroupBox("核心信息")
        steg_key_layout = QVBoxLayout()
        self.label_basic = QLineEdit("版权基本信息")  #版权基本信息
        self.label_important = QLineEdit("关键信息")  #关键信息
        self.label_extra = QLineEdit("额外信息后缀")  #额外信息后缀
        self.label_full = QLineEdit("Label Preview")
        self.label_full.setReadOnly(True)              # Preview only - Default read-only
        self.text_key = QLineEdit("4321")  #加密密钥
        steg_key_layout.addWidget(self.label_basic)
        steg_key_layout.addWidget(self.label_important)
        steg_key_layout.addWidget(self.label_extra)
        steg_key_layout.addWidget(self.label_full)
        steg_key_layout.addWidget(self.text_key)
        steg_key_group.setLayout(steg_key_layout)
        steg_layout.addWidget(steg_key_group)

        #随机数组
        steg_sub_group = QGroupBox("辅助信息")
        steg_sub_layout = QVBoxLayout()
        self.text_seed = QLineEdit("1234")  #随机数seed
        steg_sub_layout.addWidget(QPushButton("伪随机数生成"))  #伪随机数生成按钮
        steg_sub_layout.addWidget(self.text_seed)
        steg_sub_group.setLayout(steg_sub_layout)
        steg_layout.addWidget(steg_sub_group)

        steg_group.setLayout(steg_layout)
        layout.addWidget(steg_group)
        #####################################################
        self.embed_button = QPushButton("embed watermark")  #嵌入可视+不可视水印
        layout.addWidget(self.embed_button)

        embed_tab.setLayout(layout)
        return embed_tab
    




    #Initialize the Read Watermark tab/读取水印的tab
    def init_read_tab(self):
        read_tab = QWidget()
        layout = QVBoxLayout()


        # QR Code Section
        qr_group = QGroupBox("QR Code")
        qr_layout = QVBoxLayout()
        self.qr_preview_pic = QLabel("QR Code Pic Preview")
        self.qr_preview_pic.setAlignment(Qt.AlignLeft)
        self.qr_decode_text = QLabel("QR Code decode Preview")
        self.button_qr_decode = QPushButton("Decode QR Code")  #解析
        #qr_layout.button_qr_decode.setAlignment(Qt.AlignRight)
        qr_layout.addWidget(self.qr_preview_pic)
        qr_layout.addWidget(self.qr_decode_text)
        qr_layout.addWidget(self.button_qr_decode)
        qr_group.setLayout(qr_layout)
        layout.addWidget(qr_group)

        # 文本水印
        watermark_text_group = QGroupBox("文本水印")
        watermark_text_layout = QVBoxLayout()
        self.text_preview = QLineEdit("加密文字内容")
        self.text_preview.setReadOnly(True)              # Preview only - Default read-only
        self.text_key = QLineEdit("4321")  #加密密钥 来自database
        watermark_text_layout.addWidget(self.text_key)
        watermark_text_layout.addWidget(self.text_preview)
        watermark_text_layout.addWidget(QPushButton("Extract Watermark"))
        watermark_text_group.setLayout(watermark_text_layout)
        layout.addWidget(watermark_text_group)

        # 辅助水印
        watermark_sub_group = QGroupBox("辅助水印")
        watermark_sub_layout = QVBoxLayout()
        self.random_preview = QLineEdit("伪随机数")
        self.random_preview.setReadOnly(True)              # Preview only - Default read-only
        self.random_seed = QLineEdit("4321")  #随机数seed 来自database
        self.random_seed.setReadOnly(True)              # Preview only - Default read-only
        watermark_sub_layout.addWidget(self.random_preview)
        watermark_sub_layout.addWidget(self.random_seed)
        watermark_sub_group.setLayout(watermark_sub_layout)
        layout.addWidget(watermark_sub_group)


        # Buttons
        self.button_reload = QPushButton("reload Databade")  #重新载入数据库内容
        self.button_decode = QPushButton("Decode Watermarks")  #水印读取
        layout.addWidget(self.button_reload)
        layout.addWidget(self.button_decode)

        read_tab.setLayout(layout)
        return read_tab


#Update the left panel content based on the active tab.
    def update_left_panel(self):
        current_tab = self.tabs.currentIndex()
        if current_tab == 0:  # Embed Watermark tab
            self.exif_label.setReadOnly(False)
            self.filename_label.setText("Filename: Embedding Mode")
        elif current_tab == 1:  # Read Watermark tab
            self.exif_label.setReadOnly(True)
            self.filename_label.setText("Filename: Reading Mode")

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