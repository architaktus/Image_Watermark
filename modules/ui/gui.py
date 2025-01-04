
from PyQt5.QtWidgets import (
    QMainWindow, 
    QWidget, QTabWidget, QListWidget,
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QLineEdit, QTextEdit,
    QCheckBox, QGroupBox, 
    QFileDialog, QFormLayout
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer
import os
from modules.utils import (utils, image_manager, watermark_steganography)
from modules import config

class WatermarkApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Watermark Tool")
        self.setGeometry(100, 100, 1500, 750)
        # 一些实例变量
        self._dir_img_to_process = None

        # Main Layout
        main_widget = QWidget()
        main_layout = QGridLayout(main_widget)
        self.setCentralWidget(main_widget)

        # Left Panel
        self.left_panel = self.init_left_panel()
        main_layout.addWidget(self.left_panel, 0, 0)  # 第一行，第一列，至第2行，第1列（起始坐标x,y, rowspan, colspan）        

        # Top-right Panel: Metadata
        self.metadata_panel = self.init_metadata_panel()
        main_layout.addWidget(self.metadata_panel, 0, 1)    # 第1行，第2列

        # Tab Area (Yellow Area)
        self.tabs = QTabWidget()        
        self.tabs.addTab(self.init_embed_tab(), "Embed Watermark") # Embed Watermark Tab
        self.tabs.addTab(self.init_read_tab(), "Read Watermark") # Read Watermark Tab
        self.tabs.currentChanged.connect(self.update_left_panel)  # Update left panel based on the active tab
        main_layout.addWidget(self.tabs, 0, 2)

        # 调整宽度比例
        main_layout.setColumnStretch(0, 1)  # 左侧面板的宽度占比为2
        main_layout.setColumnStretch(1, 1)  # 右侧标签页的宽度占比为2
        main_layout.setColumnStretch(2, 1)  # 右侧标签页的宽度占比为2
        main_layout.setRowStretch(0, 1)

#####################################################################################
#####################################################################################      
    #utils

    # 图片预览框随窗口变化而变化
    def resizeEvent(self, event):
        # 获取左侧面板的大小
        panel_width = self.left_panel.width()
        panel_height = self.left_panel.height()

        # 确保预览框始终为正方形（取较小的边长）
        square_size = min(panel_width, panel_height) - 25  # 留出边距
        #self.preview_label.setFixedSize(square_size, square_size)
        self.preview_label.setMinimumHeight(square_size)
        self.preview_label.setMaximumHeight(square_size)


        # 延迟刷新布局
        QTimer.singleShot(10, self.left_panel.layout().update)

        super().resizeEvent(event)


    # 加载图片列表
    def load_images(self):
        """
        从 'to_process' 文件夹加载图片并更新列表控件。
        """
        self._dir_img_to_process = config.IMAGE_TO_PROCESS_DIR
        print(self._dir_img_to_process)          
        images = image_manager.get_image_list(self._dir_img_to_process)
        #print (images)
        self.list_image_to_process.addItems(images)

    # 选取图片时
    def on_image_selected(self, item):        
        self.selected_image = item.text()    # 获取选中的图片文件名
        #self.label_zustand.setText(f"Selected Image: {selected_image}")     #设置当前状态
        self.selected_image_path = os.path.join(self._dir_img_to_process, self.selected_image)
        #self.process_button.setEnabled(True)
        image_manager.read_image(self.selected_image_path)

        # 使用 QPixmap 加载图片
        pixmap = QPixmap(self.selected_image_path)
        self.preview_label.setPixmap(pixmap.scaled(self.preview_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

        # 读取metadata
        metadata = image_manager.extract_metadata(self.selected_image_path)
        # 显示metadata
        self.exif_label_filename_old.setText(metadata['title'])
        self.exif_label_resolution.setText(f"{metadata['compression']['dpi']}")
        self.exif_label_compression.setText(f"{metadata['compression']['compression_format']}") #TODO quality compression level。。。
        self.exif_label_size.setText(f"{metadata['size']['width']} x {metadata['size']['height']}")
        #self.exif_label_colordepth.setText(metadata['title']) # TODO
        #self.exif_label_createtime.setText(metadata['title']) # TODO

        if metadata['exif']:
            meta_exif = metadata['exif']
            if 'ImageTitle' in meta_exif:
                self.img_label_documenttitle_old_exif.setText(meta_exif['ImageTitle'])
            if 'Artist' in meta_exif:
                self.img_label_author_old_exif.setText(metadata['Artist'])
            if 'Copyright' in meta_exif:
                self.img_label_copyright_old_exif.setText(metadata['Copyright'])
            if 'UserComment' in meta_exif:
                self.img_label_comment_old_exif.setText(metadata['UserComment'])        
        if metadata['iptc']:
            meta_iptc = metadata['iptc']
            if 'Document title' in meta_iptc:
                self.img_label_documenttitle_old_iptc.setText(metadata['Document title'])
            if 'Creator' in meta_iptc:
                self.img_label_author_old_iptc.setText(metadata['Creator'])
            if 'CopyrightNotice' in meta_iptc:
                self.img_label_copyright_old_iptc.setText(metadata['CopyrightNotice'])

#    def draw_image(self):
        #file_path, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        #if file_path:
#        pixmap = QPixmap(self.selected_image_path)
        # 使用 QPixmap 加载图片
        # 将图片设置到 QLabel
#        self.preview_label.setPixmap(pixmap.scaled(self.preview_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))


    # 加水印
    def to_embed_watermark(self):
        # TODO 图片改名、加入数据库
        if self.selected_image:
            output_path = os.path.join(config.IMAGE_WATERMARKED_DIR, self.selected_image)
            print(f">>>EMBEDDING WATERMARK...")
            watermark_steganography.stega_embed(self.selected_image_path, output_path, 2) # TODO Alpha
        #else:
            # TODO 提示选择图片
    # 读取水印
    def to_extract_watermark(self):
        input_origin = config.TEST_ORIGINAL_DIR
        input_wm = config.TEST_WATERMARKED_DIR
        #output_wm_set = watermark_steganography.stega_extract(input_wm, input_origin)
        print(f">>>EXTRACTING WATERMARK...")
        watermark_steganography.stega_extract(input_wm, input_origin, 2)
        #output_wm_ll = output_wm_set[0]
        #output_wm_hl = output_wm_set[1]
        # 使用 QPixmap 加载图片
        #pixmap = QPixmap(self.selected_image_path)
        #self.preview_label.setPixmap(pixmap.scaled(self.preview_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))


#####################################################################################
#####################################################################################      
    # fixed left panel.
    def init_left_panel(self):
        left_panel = QGroupBox("Image")
        layout = QVBoxLayout()

        # Preview Area：预览、选择图片
        self.preview_label = QLabel("Image Preview: No Image Loaded", self)
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("border: 1px solid grey;")
        #self.preview_label.setScaledContents(True)  # 允许内容随大小变化
        layout.addWidget(self.preview_label)
        layout.addWidget(QLabel("Image List"))

        # Image selection 
            # path Panel
        self.list_image_to_process = QListWidget()
        self.refresh_button = QPushButton("Refresh")
#        self.load_image_button = QPushButton("Load Image")
        self.refresh_button.clicked.connect(self.load_images)
#        self.load_image_button.clicked.connect(self.draw_image)
        layout.addWidget(self.list_image_to_process)
        layout.addWidget(self.refresh_button)
#        layout.addWidget(self.load_image_button)
        self.load_images()

            # 信号绑定
        self.list_image_to_process.itemClicked.connect(self.on_image_selected)
        #self.confirm_button.clicked.connect(self.process_selected_image)


        left_panel.setLayout(layout)
        return left_panel


#####################################################################################
#####################################################################################
    # middle Panel: Metadata
    def init_metadata_panel(self):
        metadata_panel = QGroupBox("Info: Embedding Mode")
        layout = QVBoxLayout()

        #####################################################
        # Info Panel
        exif_group = QGroupBox("Info")
        exif_layout = QFormLayout()

        self.exif_label_filename_old = QLabel("")
        self.exif_label_filename_new = QLineEdit("")
        self.exif_label_resolution = QLabel("N/A")
        self.exif_label_compression = QLabel("N/A")
        self.exif_label_size = QLabel("N/A")
        self.exif_label_colordepth = QLabel("N/A")
        self.exif_label_createtime = QLabel("N/A")
        
        #exif_layout.addWidget(QLabel("file name"))
        exif_layout.addRow("file name(original):", self.exif_label_filename_old)
#        exif_layout.addRow("file name(new):", self.exif_label_filename_new)
        exif_layout.addRow("Resolution:", self.exif_label_resolution)
        exif_layout.addRow("Compression:", self.exif_label_compression)
        exif_layout.addRow("Size (Pixel):", self.exif_label_size)
        exif_layout.addRow("Color Depth:", self.exif_label_colordepth)
        exif_layout.addRow("Create Time:", self.exif_label_createtime)

        exif_group.setLayout(exif_layout)
        layout.addWidget(exif_group)


        #####################################################
        # meta-panel
        metadata_group = QGroupBox("Metadata")
        metadata_layout = QFormLayout()

        # Title
        self.img_label_documenttitle_old_exif = QLabel("")
        #self.img_label_documenttitle_old_exif = QLineEdit("")
        #self.img_label_documenttitle_old_exif.setReadOnly(True)
        self.img_label_documenttitle_old_iptc = QLabel("")
        self.img_label_documenttitle_new = QLineEdit("")
        metadata_layout.addRow(QLabel("标题"))
        metadata_layout.addRow("     EXIF - ImageTitle:", self.img_label_documenttitle_old_exif)
        metadata_layout.addRow("     IPTC - Document title:", self.img_label_documenttitle_old_iptc)
#        metadata_layout.addRow("     EXIF & IPTC - 新标题:", self.img_label_documenttitle_new)

        # Author
        self.img_label_author_old_exif = QLabel("")
        self.img_label_author_old_iptc = QLabel("")
        self.img_label_author_new = QLineEdit("")
        metadata_layout.addRow(QLabel("作者"))
        metadata_layout.addRow("     EXIF - Artist:", self.img_label_author_old_exif)
        metadata_layout.addRow("     IPTC - Creator:", self.img_label_author_old_iptc)
#        metadata_layout.addRow("     EXIF & IPTC - 新作者:", self.img_label_author_new)

        # Copyright
        self.img_label_copyright_old_exif = QLabel("")
        self.img_label_copyright_old_iptc = QLabel("")
        self.img_label_copyright_new = QLabel(config.COPYRIGHT_LONG)
        self.img_label_copyright_new.setWordWrap(True)
        metadata_layout.addRow(QLabel("版权"))
        metadata_layout.addRow("     EXIF - Copyright:", self.img_label_copyright_old_exif)
        metadata_layout.addRow("     IPTC - Copyright:", self.img_label_copyright_old_iptc)
        metadata_layout.addRow("     EXIF & IPTC - 新版权:", self.img_label_copyright_new)

        # Comment
        self.img_label_comment_old_exif = QLabel("")
        self.img_label_comment_new = QLineEdit("")
        metadata_layout.addRow(QLabel("备注"))
        metadata_layout.addRow("     EXIF - Comment:", self.img_label_comment_old_exif)
#        metadata_layout.addRow("     EXIF - 新备注:", self.img_label_comment_new)
        
        metadata_group.setLayout(metadata_layout)
        layout.addWidget(metadata_group)


        #####################################################
        # copyright-panel
        copyright_group = QGroupBox("Copyright")
        copyright_layout = QFormLayout()
        self.copyright_basic = QLineEdit(config.COPYRIGHT_SHORT)  #版权基本信息
        self.copyright_year = QLineEdit(config.COPYRIGHT_YEAR)  #年份信息
        self.copyright_extra = QTextEdit(config.RIGHTS_USAGE_TERMS)  #额外信息后缀
        self.copyright_full = QLabel(config.COPYRIGHT_LONG)
        self.copyright_full.setWordWrap(True)
        copyright_layout.addRow("版权基本信息:", self.copyright_basic)
        copyright_layout.addRow("年份:", self.copyright_year)
        copyright_layout.addRow("额外信息后缀:", self.copyright_extra)
        copyright_layout.addRow("完整水印预览:", self.copyright_full)
        copyright_group.setLayout(copyright_layout)
        layout.addWidget(copyright_group)


        #####################################################
        # button Panel
        self.update_button = QPushButton("Reload") #重新加载Exif
        # TODO 图片Exif + Database的数据如何协调？
        self.save_button = QPushButton("Save") #保存到database + 图片Exif
        layout.addWidget(self.update_button)
        layout.addWidget(self.save_button)


        metadata_panel.setLayout(layout)

        # TODO 添加按钮：一键删除所有EXIF信息
        return metadata_panel
    



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
        self.text_key = QLineEdit("4321")  #加密密钥
        self.label_full_encrypted = QLabel("Encrypted Label Preview")
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
        self.embed_button.clicked.connect(self.to_embed_watermark)
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
        self.button_decode.clicked.connect(self.to_extract_watermark)
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
            self.metadata_panel.setTitle("Info: Embedding Mode")
        elif current_tab == 1:  # Read Watermark tab
            #self.tab_label.setReadOnly(True)
            self.metadata_panel.setTitle("Info: Reading Mode")

    def open_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg *.jpeg)")
        if file_name:
            pixmap = QPixmap(file_name)
            self.preview_label.setPixmap(pixmap.scaled(self.preview_label.size(), Qt.KeepAspectRatio))


    def open_image_read(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg *.jpeg)")
        if file_name:
            pixmap = QPixmap(file_name)
            self.read_preview_label.setPixmap(pixmap.scaled(self.read_preview_label.size(), Qt.KeepAspectRatio))

    def read_watermark(self):
        print("Reading watermark...")
        # Placeholder for reading logic
        self.read_info_label.setText("Detected Watermark: Example Watermark")