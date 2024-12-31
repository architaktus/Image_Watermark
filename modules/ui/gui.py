from PyQt5.QtWidgets import QMainWindow, QPushButton, QFileDialog, QMessageBox

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Watermark System")
        
        # 按钮：选择图片
        btn_select = QPushButton("选择图片", self)
        btn_select.clicked.connect(self.select_image)
        btn_select.setGeometry(50, 50, 100, 30)
        
        # 其他按钮
        # ...
    
    def select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择图片", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            QMessageBox.information(self, "选中图片", f"文件: {file_path}")
            # 后续调用数据库插入、EXIF读取等