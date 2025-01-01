
from PyQt5.QtWidgets import (
    QMainWindow, 
    QWidget, QTabWidget,
    QVBoxLayout, QHBoxLayout, QGridLayout,
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

        # 调整宽度比例
        main_layout.setStretch(0, 2)  # 左侧面板的宽度占比为2
        main_layout.setStretch(1, 5)  # 右侧标签页的宽度占比为5


#####################################################################################
#####################################################################################      
    # fixed left panel.
    def init_left_panel(self):
        left_panel = QGroupBox("Info")
        layout = QVBoxLayout()

        # Preview Area
        self.preview_label = QLabel("Image Preview", self)
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("border: 1px solid grey;")
        self.tab_label = QLabel("Filename: Embedding Mode")
        layout.addWidget(self.preview_label)
        layout.addWidget(self.tab_label)

        # Info Panel
        exif_group = QGroupBox("Info")
        exif_layout = QFormLayout()

        self.exif_label_filename = QLineEdit("None")
        self.exif_label_documenttitle = QLineEdit("None")
        self.exif_label_resolution = QLabel("N/A")
        self.exif_label_compression = QLabel("N/A")
        self.exif_label_size = QLabel("N/A")
        self.exif_label_colordepth = QLabel("N/A")
        self.exif_label_createtime = QLabel("N/A")
        self.exif_label_comment = QLineEdit("Extra Comment")
        
        exif_layout.addRow("file name:", self.exif_label_filename)
        exif_layout.addRow("document title:", self.exif_label_documenttitle)
        exif_layout.addRow("Resolution:", self.exif_label_resolution)
        exif_layout.addRow("Compression:", self.exif_label_compression)
        exif_layout.addRow("Size (Pixel):", self.exif_label_size)
        exif_layout.addRow("Color Depth:", self.exif_label_colordepth)
        exif_layout.addRow("Create Time:", self.exif_label_createtime)
        exif_layout.addRow("Comment:", self.exif_label_comment)

        exif_group.setLayout(exif_layout)
        layout.addWidget(exif_group)



        # button Panel
        self.update_button = QPushButton("Reload") #重新加载Exif
        # TODO 图片Exif + Database的数据如何协调？
        self.save_button = QPushButton("Save") #保存到database + 图片Exif
        layout.addWidget(self.update_button)
        layout.addWidget(self.save_button)

        left_panel.setLayout(layout)
        return left_panel


#####################################################################################
#####################################################################################
    #Initialize the Embed Watermark tab/嵌入水印的tab
    def init_embed_tab(self):
        embed_tab = QWidget()
        layout = QVBoxLayout()

        # Image Processing Section/ 压缩
        preprocess_group = QGroupBox("Image Preprocessing")
        preprocess_layout = QVBoxLayout()
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
        steg_cal_layout = QFormLayout()
        self.label_alpha = QLineEdit("0.2")  #DWT Alpha
        steg_cal_layout.addRow("Alpha:", self.label_alpha)
        steg_cal_group.setLayout(steg_cal_layout)
        steg_layout.addWidget(steg_cal_group)

        #关键信息组
        steg_key_group = QGroupBox("核心信息")
        steg_key_layout = QFormLayout()
        self.label_basic = QLineEdit("版权基本信息")  #版权基本信息
        self.label_important = QLineEdit("关键信息")  #关键信息
        self.label_extra = QLineEdit("额外信息后缀")  #额外信息后缀
        self.label_full = QLabel("Label Preview")
        self.text_key = QLineEdit("4321")  #加密密钥
        self.label_full_encrypted = QLabel("Encrypted Label Preview")
        steg_key_layout.addRow("版权基本信息:", self.label_basic)
        steg_key_layout.addRow("关键信息:", self.label_important)
        steg_key_layout.addRow("额外信息后缀:", self.label_extra)
        steg_key_layout.addRow("完整水印预览:", self.label_full)
        steg_key_layout.addRow("加密密钥:", self.text_key)
        steg_key_layout.addRow("加密水印预览:", self.label_full_encrypted)
        steg_key_group.setLayout(steg_key_layout)
        steg_layout.addWidget(steg_key_group)

        #随机数组
        steg_sub_group = QGroupBox("辅助信息")
        steg_sub_layout = QFormLayout()
        self.text_seed = QLineEdit("1234")  #随机数seed
        self.text_lenght = QLineEdit("10")  #随机数长度
        steg_sub_layout.random_text = QLabel("N/A")
        steg_sub_layout.checkbox_random_text = QCheckBox()
        steg_sub_layout.checkbox_random_text.setChecked(True)        
        steg_sub_layout.addRow("随机数seed:", self.text_seed)
        steg_sub_layout.addRow("随机数长度:", self.text_lenght)
        steg_sub_layout.addRow("随机数:", steg_sub_layout.random_text)
        steg_sub_layout.addRow("自动生成随机数", steg_sub_layout.checkbox_random_text)
        steg_sub_layout.addWidget(QPushButton("伪随机数生成"))  #伪随机数生成按钮
        steg_sub_group.setLayout(steg_sub_layout)
        steg_layout.addWidget(steg_sub_group)

        steg_group.setLayout(steg_layout)
        layout.addWidget(steg_group)
        #####################################################
        self.embed_button = QPushButton("embed watermark")  #嵌入可视+不可视水印
        layout.addWidget(self.embed_button)

        embed_tab.setLayout(layout)
        return embed_tab
    



#####################################################################################
#####################################################################################
    #Initialize the Read Watermark tab/读取水印的tab
    def init_read_tab(self):
        read_tab = QWidget()
        layout = QVBoxLayout()


        # QR Code Section
        qr_group = QGroupBox("QR Code")
        qr_layout = QGridLayout()
            # 左侧：二维码图片预览框
        self.qr_preview_pic = QLabel("QR Code Pic Preview")
        self.qr_preview_pic.setAlignment(Qt.AlignCenter)
        self.qr_preview_pic.setStyleSheet("border: 1px solid grey;")
        qr_layout.addWidget(self.qr_preview_pic, 0, 0, 3, 1)  # 第一行，第一列，至第3行，第1列（起始坐标x,y, rowspan, colspan）
            # 右侧：二维码内容预览
        qr_layout.qr_decode_title = QLabel("QR Code decode Preview:")
        self.qr_decode_text = QLabel("N/A")
        qr_layout.addWidget(qr_layout.qr_decode_title, 0, 1)   # 第一行，第2列
        qr_layout.addWidget(self.qr_decode_text, 1, 1)   # 第2行，第2列
            # 右侧：解码按钮
        self.button_qr_decode = QPushButton("Decode QR Code")  #解析
        qr_layout.addWidget(self.button_qr_decode, 2, 1)   # 第3行，第2列
            # 调整行列拉伸因子、排列
        #qr_layout.setRowStretch(0, 1)
        #qr_layout.setRowStretch(1, 1)
        #qr_layout.setRowStretch(2, 5)

        qr_group.setLayout(qr_layout)
        layout.addWidget(qr_group)
        layout.setStretch(0, 3)


        # 文本水印
        watermark_text_group = QGroupBox("文本水印")
        watermark_text_layout = QFormLayout()
        self.text_preview = QLabel("N/A")
        self.text_key = QLineEdit("4321")  #加密密钥 来自database
        watermark_text_layout.addRow("加密密钥:", self.text_key)
        watermark_text_layout.addRow("加密文字内容:", self.text_preview)
        #watermark_text_layout.addWidget(QPushButton("Extract Watermark"))
        watermark_text_group.setLayout(watermark_text_layout)
        layout.addWidget(watermark_text_group)
        layout.setStretch(1, 1)


        # 辅助水印
        watermark_sub_group = QGroupBox("辅助水印")
        watermark_sub_layout = QFormLayout()
        self.random_preview = QLabel("N/A")
        self.random_seed = QLabel("4321")  #随机数seed 来自database
        watermark_sub_layout.addRow("随机数seed:", self.random_seed)
        watermark_sub_layout.addRow("伪随机数:", self.random_preview)
        watermark_sub_group.setLayout(watermark_sub_layout)
        layout.addWidget(watermark_sub_group)
        layout.setStretch(2, 1)


        # Buttons
        self.button_reload = QPushButton("reload Databade")  #重新载入数据库内容
        self.button_decode = QPushButton("Decode Watermarks")  #水印读取
        layout.addWidget(self.button_reload)
        layout.addWidget(self.button_decode)
        layout.setStretch(3, 1) 

        read_tab.setLayout(layout)
        return read_tab


#Update the left panel content based on the active tab.
    def update_left_panel(self):
        current_tab = self.tabs.currentIndex()
        if current_tab == 0:  # Embed Watermark tab
            #self.tab_label.setReadOnly(False)
            self.tab_label.setText("Filename: Embedding Mode")
        elif current_tab == 1:  # Read Watermark tab
            #self.tab_label.setReadOnly(True)
            self.tab_label.setText("Filename: Reading Mode")

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