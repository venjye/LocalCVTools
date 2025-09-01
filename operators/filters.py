"""
滤波算子实现
"""
import cv2
import numpy as np
from core.operator import BaseOperator, Parameter


class GaussianBlurOperator(BaseOperator):
    """高斯模糊算子"""
    
    def __init__(self):
        super().__init__("Gaussian Blur")

    def _setup_parameters(self):
        self.add_parameter(Parameter("kernel_size", int, 5, 1, 99, "核大小（必须为奇数）"))
        self.add_parameter(Parameter("sigma_x", float, 1.0, 0.1, 10.0, "X方向标准差"))
        self.add_parameter(Parameter("sigma_y", float, 1.0, 0.1, 10.0, "Y方向标准差"))

    def _setup_ports(self):
        self.input_ports = ["image"]
        self.output_ports = ["image"]

    def process(self, inputs):
        image = inputs["image"]
        kernel_size = self.get_parameter("kernel_size")
        sigma_x = self.get_parameter("sigma_x")
        sigma_y = self.get_parameter("sigma_y")
        
        # 确保kernel_size为奇数
        if kernel_size % 2 == 0:
            kernel_size += 1
        
        result = cv2.GaussianBlur(image, (kernel_size, kernel_size), sigma_x, sigmaY=sigma_y)
        return {"image": result}


class MedianBlurOperator(BaseOperator):
    """中值滤波算子"""
    
    def __init__(self):
        super().__init__("Median Blur")

    def _setup_parameters(self):
        self.add_parameter(Parameter("kernel_size", int, 5, 1, 99, "核大小（必须为奇数）"))

    def _setup_ports(self):
        self.input_ports = ["image"]
        self.output_ports = ["image"]

    def process(self, inputs):
        image = inputs["image"]
        kernel_size = self.get_parameter("kernel_size")
        
        # 确保kernel_size为奇数
        if kernel_size % 2 == 0:
            kernel_size += 1
        
        result = cv2.medianBlur(image, kernel_size)
        return {"image": result}


class BilateralFilterOperator(BaseOperator):
    """双边滤波算子"""
    
    def __init__(self):
        super().__init__("Bilateral Filter")

    def _setup_parameters(self):
        self.add_parameter(Parameter("d", int, 9, 1, 50, "像素邻域直径"))
        self.add_parameter(Parameter("sigma_color", float, 75.0, 1.0, 200.0, "颜色空间标准差"))
        self.add_parameter(Parameter("sigma_space", float, 75.0, 1.0, 200.0, "坐标空间标准差"))

    def _setup_ports(self):
        self.input_ports = ["image"]
        self.output_ports = ["image"]

    def process(self, inputs):
        image = inputs["image"]
        d = self.get_parameter("d")
        sigma_color = self.get_parameter("sigma_color")
        sigma_space = self.get_parameter("sigma_space")
        
        result = cv2.bilateralFilter(image, d, sigma_color, sigma_space)
        return {"image": result}


class BoxFilterOperator(BaseOperator):
    """方框滤波算子"""
    
    def __init__(self):
        super().__init__("Box Filter")

    def _setup_parameters(self):
        self.add_parameter(Parameter("kernel_size", int, 5, 1, 99, "核大小"))
        self.add_parameter(Parameter("normalize", bool, True, description="是否归一化"))

    def _setup_ports(self):
        self.input_ports = ["image"]
        self.output_ports = ["image"]

    def process(self, inputs):
        image = inputs["image"]
        kernel_size = self.get_parameter("kernel_size")
        normalize = self.get_parameter("normalize")
        
        result = cv2.boxFilter(image, -1, (kernel_size, kernel_size), normalize=normalize)
        return {"image": result}


class LaplacianOperator(BaseOperator):
    """拉普拉斯算子"""
    
    def __init__(self):
        super().__init__("Laplacian")

    def _setup_parameters(self):
        self.add_parameter(Parameter("kernel_size", int, 1, 1, 31, "核大小（必须为奇数）"))
        self.add_parameter(Parameter("scale", float, 1.0, 0.1, 10.0, "缩放因子"))
        self.add_parameter(Parameter("delta", float, 0.0, -100.0, 100.0, "偏移值"))

    def _setup_ports(self):
        self.input_ports = ["image"]
        self.output_ports = ["image"]

    def process(self, inputs):
        image = inputs["image"]
        kernel_size = self.get_parameter("kernel_size")
        scale = self.get_parameter("scale")
        delta = self.get_parameter("delta")
        
        # 确保kernel_size为奇数
        if kernel_size % 2 == 0:
            kernel_size += 1
        
        # 转换为灰度图
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        result = cv2.Laplacian(gray, cv2.CV_64F, ksize=kernel_size, scale=scale, delta=delta)
        result = np.uint8(np.absolute(result))
        
        # 如果输入是彩色图像，转换回彩色
        if len(image.shape) == 3:
            result = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)
        
        return {"image": result}


class SobelOperator(BaseOperator):
    """Sobel算子"""
    
    def __init__(self):
        super().__init__("Sobel")

    def _setup_parameters(self):
        self.add_parameter(Parameter("dx", int, 1, 0, 2, "X方向导数阶数"))
        self.add_parameter(Parameter("dy", int, 0, 0, 2, "Y方向导数阶数"))
        self.add_parameter(Parameter("kernel_size", int, 3, 1, 31, "核大小（必须为奇数）"))
        self.add_parameter(Parameter("scale", float, 1.0, 0.1, 10.0, "缩放因子"))
        self.add_parameter(Parameter("delta", float, 0.0, -100.0, 100.0, "偏移值"))

    def _setup_ports(self):
        self.input_ports = ["image"]
        self.output_ports = ["image"]

    def process(self, inputs):
        image = inputs["image"]
        dx = self.get_parameter("dx")
        dy = self.get_parameter("dy")
        kernel_size = self.get_parameter("kernel_size")
        scale = self.get_parameter("scale")
        delta = self.get_parameter("delta")
        
        # 确保kernel_size为奇数
        if kernel_size % 2 == 0:
            kernel_size += 1
        
        # 转换为灰度图
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        result = cv2.Sobel(gray, cv2.CV_64F, dx, dy, ksize=kernel_size, scale=scale, delta=delta)
        result = np.uint8(np.absolute(result))
        
        # 如果输入是彩色图像，转换回彩色
        if len(image.shape) == 3:
            result = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)
        
        return {"image": result}
