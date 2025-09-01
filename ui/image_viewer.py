"""
图像查看器组件
"""
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import numpy as np
import cv2


class ImageViewer(QLabel):
    """图像查看器"""
    
    def __init__(self):
        super().__init__()
        
        # 设置基本属性
        self.setMinimumSize(400, 300)
        self.setStyleSheet("border: 1px solid gray;")
        self.setAlignment(Qt.AlignCenter)
        self.setText("No Image")
        
        # 图像数据
        self.original_image = None
        self.current_pixmap = None
        self.scale_factor = 1.0
        
        # 鼠标交互
        self.setMouseTracking(True)
        self.last_pan_point = QPoint()
        self.dragging = False
        
        # 显示信息
        self.show_info = True
        self.mouse_pos = QPoint()
        
    def set_image(self, image: np.ndarray):
        """设置要显示的图像"""
        if image is None:
            self.clear_image()
            return
        
        self.original_image = image.copy()
        self._update_display()
    
    def clear_image(self):
        """清除图像"""
        self.original_image = None
        self.current_pixmap = None
        self.setText("No Image")
        self.update()
    
    def _numpy_to_qpixmap(self, image: np.ndarray) -> QPixmap:
        """将numpy数组转换为QPixmap"""
        if len(image.shape) == 3:
            # 彩色图像
            if image.shape[2] == 3:
                # BGR to RGB
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            elif image.shape[2] == 4:
                # BGRA to RGBA
                rgba_image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGBA)
                h, w, ch = rgba_image.shape
                bytes_per_line = ch * w
                qt_image = QImage(rgba_image.data, w, h, bytes_per_line, QImage.Format_RGBA8888)
            else:
                raise ValueError("Unsupported image format")
        else:
            # 灰度图像
            h, w = image.shape
            bytes_per_line = w
            qt_image = QImage(image.data, w, h, bytes_per_line, QImage.Format_Grayscale8)
        
        return QPixmap.fromImage(qt_image)
    
    def _update_display(self):
        """更新显示"""
        if self.original_image is None:
            return
        
        # 转换为QPixmap
        pixmap = self._numpy_to_qpixmap(self.original_image)
        
        # 缩放到合适大小
        widget_size = self.size()
        scaled_pixmap = pixmap.scaled(widget_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        self.current_pixmap = scaled_pixmap
        self.setPixmap(scaled_pixmap)
    
    def resizeEvent(self, event):
        """窗口大小改变事件"""
        super().resizeEvent(event)
        if self.original_image is not None:
            self._update_display()
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            self.last_pan_point = event.pos()
            self.dragging = True
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        self.mouse_pos = event.pos()
        
        if self.dragging and event.buttons() == Qt.LeftButton:
            # 拖拽功能（暂时不实现，保留接口）
            pass
        
        self.update()  # 触发重绘以显示鼠标位置信息
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            self.dragging = False
    
    def wheelEvent(self, event):
        """鼠标滚轮缩放事件"""
        if self.original_image is None:
            return
        
        # 缩放因子
        factor = 1.25 if event.angleDelta().y() > 0 else 0.8
        self.scale_factor *= factor
        
        # 限制缩放范围
        self.scale_factor = max(0.1, min(5.0, self.scale_factor))
        
        # 重新缩放图像
        if self.current_pixmap:
            original_pixmap = self._numpy_to_qpixmap(self.original_image)
            new_size = original_pixmap.size() * self.scale_factor
            scaled_pixmap = original_pixmap.scaled(new_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.setPixmap(scaled_pixmap)
    
    def paintEvent(self, event):
        """绘制事件"""
        super().paintEvent(event)
        
        if self.show_info and self.original_image is not None:
            painter = QPainter(self)
            painter.setPen(QPen(QColor(255, 255, 0), 2))
            
            # 显示图像信息
            info_text = f"Size: {self.original_image.shape[1]}x{self.original_image.shape[0]}"
            if len(self.original_image.shape) == 3:
                info_text += f"x{self.original_image.shape[2]}"
            info_text += f" | Scale: {self.scale_factor:.2f}"
            
            # 显示鼠标位置的像素值
            if self.current_pixmap and not self.current_pixmap.isNull():
                pixmap_rect = self.current_pixmap.rect()
                widget_rect = self.rect()
                
                # 计算图像在widget中的位置
                x_offset = (widget_rect.width() - pixmap_rect.width()) // 2
                y_offset = (widget_rect.height() - pixmap_rect.height()) // 2
                
                # 鼠标在图像中的相对位置
                rel_x = self.mouse_pos.x() - x_offset
                rel_y = self.mouse_pos.y() - y_offset
                
                if (0 <= rel_x < pixmap_rect.width() and 
                    0 <= rel_y < pixmap_rect.height()):
                    
                    # 计算在原图中的坐标
                    scale_x = self.original_image.shape[1] / pixmap_rect.width()
                    scale_y = self.original_image.shape[0] / pixmap_rect.height()
                    
                    orig_x = int(rel_x * scale_x)
                    orig_y = int(rel_y * scale_y)
                    
                    if (0 <= orig_x < self.original_image.shape[1] and 
                        0 <= orig_y < self.original_image.shape[0]):
                        
                        pixel_value = self.original_image[orig_y, orig_x]
                        if len(self.original_image.shape) == 3:
                            info_text += f" | Pos: ({orig_x}, {orig_y}) | BGR: {pixel_value}"
                        else:
                            info_text += f" | Pos: ({orig_x}, {orig_y}) | Gray: {pixel_value}"
            
            # 绘制信息文本
            painter.drawText(10, 20, info_text)
    
    def save_image(self, filepath: str):
        """保存当前图像"""
        if self.original_image is not None:
            cv2.imwrite(filepath, self.original_image)
    
    def get_image_info(self) -> dict:
        """获取图像信息"""
        if self.original_image is None:
            return {}
        
        info = {
            'shape': self.original_image.shape,
            'dtype': str(self.original_image.dtype),
            'min_value': float(self.original_image.min()),
            'max_value': float(self.original_image.max()),
            'mean_value': float(self.original_image.mean())
        }
        
        return info


class ImageComparisonViewer(QWidget):
    """图像对比查看器"""
    
    def __init__(self):
        super().__init__()
        
        # 创建布局
        layout = QHBoxLayout()
        
        # 创建两个图像查看器
        self.left_viewer = ImageViewer()
        self.right_viewer = ImageViewer()
        
        # 添加标签
        left_group = QGroupBox("Original")
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.left_viewer)
        left_group.setLayout(left_layout)
        
        right_group = QGroupBox("Processed")
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.right_viewer)
        right_group.setLayout(right_layout)
        
        layout.addWidget(left_group)
        layout.addWidget(right_group)
        
        self.setLayout(layout)
    
    def set_images(self, original: np.ndarray, processed: np.ndarray):
        """设置对比图像"""
        self.left_viewer.set_image(original)
        self.right_viewer.set_image(processed)
    
    def set_left_image(self, image: np.ndarray):
        """设置左侧图像"""
        self.left_viewer.set_image(image)
    
    def set_right_image(self, image: np.ndarray):
        """设置右侧图像"""
        self.right_viewer.set_image(image)
    
    def clear_images(self):
        """清除所有图像"""
        self.left_viewer.clear_image()
        self.right_viewer.clear_image()
