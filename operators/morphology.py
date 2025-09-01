"""
形态学操作算子实现
"""
import cv2
import numpy as np
from core.operator import BaseOperator, Parameter


class ErosionOperator(BaseOperator):
    """腐蚀算子"""
    
    def __init__(self):
        super().__init__("Erosion")

    def _setup_parameters(self):
        self.add_parameter(Parameter("kernel_size", int, 5, 1, 25, "核大小"))
        self.add_parameter(Parameter("kernel_shape", str, "MORPH_RECT",
                                   options=["MORPH_RECT", "MORPH_ELLIPSE", "MORPH_CROSS"],
                                   description="核形状"))
        self.add_parameter(Parameter("iterations", int, 1, 1, 10, "迭代次数"))

    def _setup_ports(self):
        self.input_ports = ["image"]
        self.output_ports = ["image"]

    def process(self, inputs):
        image = inputs["image"]
        kernel_size = self.get_parameter("kernel_size")
        kernel_shape = self.get_parameter("kernel_shape")
        iterations = self.get_parameter("iterations")
        
        shape_dict = {
            "MORPH_RECT": cv2.MORPH_RECT,
            "MORPH_ELLIPSE": cv2.MORPH_ELLIPSE,
            "MORPH_CROSS": cv2.MORPH_CROSS
        }
        
        kernel = cv2.getStructuringElement(shape_dict[kernel_shape], 
                                         (kernel_size, kernel_size))
        result = cv2.erode(image, kernel, iterations=iterations)
        
        return {"image": result}


class DilationOperator(BaseOperator):
    """膨胀算子"""
    
    def __init__(self):
        super().__init__("Dilation")

    def _setup_parameters(self):
        self.add_parameter(Parameter("kernel_size", int, 5, 1, 25, "核大小"))
        self.add_parameter(Parameter("kernel_shape", str, "MORPH_RECT",
                                   options=["MORPH_RECT", "MORPH_ELLIPSE", "MORPH_CROSS"],
                                   description="核形状"))
        self.add_parameter(Parameter("iterations", int, 1, 1, 10, "迭代次数"))

    def _setup_ports(self):
        self.input_ports = ["image"]
        self.output_ports = ["image"]

    def process(self, inputs):
        image = inputs["image"]
        kernel_size = self.get_parameter("kernel_size")
        kernel_shape = self.get_parameter("kernel_shape")
        iterations = self.get_parameter("iterations")
        
        shape_dict = {
            "MORPH_RECT": cv2.MORPH_RECT,
            "MORPH_ELLIPSE": cv2.MORPH_ELLIPSE,
            "MORPH_CROSS": cv2.MORPH_CROSS
        }
        
        kernel = cv2.getStructuringElement(shape_dict[kernel_shape], 
                                         (kernel_size, kernel_size))
        result = cv2.dilate(image, kernel, iterations=iterations)
        
        return {"image": result}


class OpeningOperator(BaseOperator):
    """开运算算子"""
    
    def __init__(self):
        super().__init__("Opening")

    def _setup_parameters(self):
        self.add_parameter(Parameter("kernel_size", int, 5, 1, 25, "核大小"))
        self.add_parameter(Parameter("kernel_shape", str, "MORPH_RECT",
                                   options=["MORPH_RECT", "MORPH_ELLIPSE", "MORPH_CROSS"],
                                   description="核形状"))

    def _setup_ports(self):
        self.input_ports = ["image"]
        self.output_ports = ["image"]

    def process(self, inputs):
        image = inputs["image"]
        kernel_size = self.get_parameter("kernel_size")
        kernel_shape = self.get_parameter("kernel_shape")
        
        shape_dict = {
            "MORPH_RECT": cv2.MORPH_RECT,
            "MORPH_ELLIPSE": cv2.MORPH_ELLIPSE,
            "MORPH_CROSS": cv2.MORPH_CROSS
        }
        
        kernel = cv2.getStructuringElement(shape_dict[kernel_shape], 
                                         (kernel_size, kernel_size))
        result = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
        
        return {"image": result}


class ClosingOperator(BaseOperator):
    """闭运算算子"""
    
    def __init__(self):
        super().__init__("Closing")

    def _setup_parameters(self):
        self.add_parameter(Parameter("kernel_size", int, 5, 1, 25, "核大小"))
        self.add_parameter(Parameter("kernel_shape", str, "MORPH_RECT",
                                   options=["MORPH_RECT", "MORPH_ELLIPSE", "MORPH_CROSS"],
                                   description="核形状"))

    def _setup_ports(self):
        self.input_ports = ["image"]
        self.output_ports = ["image"]

    def process(self, inputs):
        image = inputs["image"]
        kernel_size = self.get_parameter("kernel_size")
        kernel_shape = self.get_parameter("kernel_shape")
        
        shape_dict = {
            "MORPH_RECT": cv2.MORPH_RECT,
            "MORPH_ELLIPSE": cv2.MORPH_ELLIPSE,
            "MORPH_CROSS": cv2.MORPH_CROSS
        }
        
        kernel = cv2.getStructuringElement(shape_dict[kernel_shape], 
                                         (kernel_size, kernel_size))
        result = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
        
        return {"image": result}


class GradientOperator(BaseOperator):
    """形态学梯度算子"""
    
    def __init__(self):
        super().__init__("Morphological Gradient")

    def _setup_parameters(self):
        self.add_parameter(Parameter("kernel_size", int, 5, 1, 25, "核大小"))
        self.add_parameter(Parameter("kernel_shape", str, "MORPH_RECT",
                                   options=["MORPH_RECT", "MORPH_ELLIPSE", "MORPH_CROSS"],
                                   description="核形状"))

    def _setup_ports(self):
        self.input_ports = ["image"]
        self.output_ports = ["image"]

    def process(self, inputs):
        image = inputs["image"]
        kernel_size = self.get_parameter("kernel_size")
        kernel_shape = self.get_parameter("kernel_shape")
        
        shape_dict = {
            "MORPH_RECT": cv2.MORPH_RECT,
            "MORPH_ELLIPSE": cv2.MORPH_ELLIPSE,
            "MORPH_CROSS": cv2.MORPH_CROSS
        }
        
        kernel = cv2.getStructuringElement(shape_dict[kernel_shape], 
                                         (kernel_size, kernel_size))
        result = cv2.morphologyEx(image, cv2.MORPH_GRADIENT, kernel)
        
        return {"image": result}


class TopHatOperator(BaseOperator):
    """顶帽算子"""
    
    def __init__(self):
        super().__init__("Top Hat")

    def _setup_parameters(self):
        self.add_parameter(Parameter("kernel_size", int, 5, 1, 25, "核大小"))
        self.add_parameter(Parameter("kernel_shape", str, "MORPH_RECT",
                                   options=["MORPH_RECT", "MORPH_ELLIPSE", "MORPH_CROSS"],
                                   description="核形状"))

    def _setup_ports(self):
        self.input_ports = ["image"]
        self.output_ports = ["image"]

    def process(self, inputs):
        image = inputs["image"]
        kernel_size = self.get_parameter("kernel_size")
        kernel_shape = self.get_parameter("kernel_shape")
        
        shape_dict = {
            "MORPH_RECT": cv2.MORPH_RECT,
            "MORPH_ELLIPSE": cv2.MORPH_ELLIPSE,
            "MORPH_CROSS": cv2.MORPH_CROSS
        }
        
        kernel = cv2.getStructuringElement(shape_dict[kernel_shape], 
                                         (kernel_size, kernel_size))
        result = cv2.morphologyEx(image, cv2.MORPH_TOPHAT, kernel)
        
        return {"image": result}


class BlackHatOperator(BaseOperator):
    """黑帽算子"""
    
    def __init__(self):
        super().__init__("Black Hat")

    def _setup_parameters(self):
        self.add_parameter(Parameter("kernel_size", int, 5, 1, 25, "核大小"))
        self.add_parameter(Parameter("kernel_shape", str, "MORPH_RECT",
                                   options=["MORPH_RECT", "MORPH_ELLIPSE", "MORPH_CROSS"],
                                   description="核形状"))

    def _setup_ports(self):
        self.input_ports = ["image"]
        self.output_ports = ["image"]

    def process(self, inputs):
        image = inputs["image"]
        kernel_size = self.get_parameter("kernel_size")
        kernel_shape = self.get_parameter("kernel_shape")
        
        shape_dict = {
            "MORPH_RECT": cv2.MORPH_RECT,
            "MORPH_ELLIPSE": cv2.MORPH_ELLIPSE,
            "MORPH_CROSS": cv2.MORPH_CROSS
        }
        
        kernel = cv2.getStructuringElement(shape_dict[kernel_shape], 
                                         (kernel_size, kernel_size))
        result = cv2.morphologyEx(image, cv2.MORPH_BLACKHAT, kernel)
        
        return {"image": result}


class ThresholdOperator(BaseOperator):
    """阈值化算子"""
    
    def __init__(self):
        super().__init__("Threshold")

    def _setup_parameters(self):
        self.add_parameter(Parameter("threshold", int, 127, 0, 255, "阈值"))
        self.add_parameter(Parameter("max_value", int, 255, 0, 255, "最大值"))
        self.add_parameter(Parameter("threshold_type", str, "THRESH_BINARY",
                                   options=["THRESH_BINARY", "THRESH_BINARY_INV", 
                                          "THRESH_TRUNC", "THRESH_TOZERO", "THRESH_TOZERO_INV"],
                                   description="阈值类型"))

    def _setup_ports(self):
        self.input_ports = ["image"]
        self.output_ports = ["image"]

    def process(self, inputs):
        image = inputs["image"]
        threshold = self.get_parameter("threshold")
        max_value = self.get_parameter("max_value")
        threshold_type = self.get_parameter("threshold_type")
        
        # 转换为灰度图
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        type_dict = {
            "THRESH_BINARY": cv2.THRESH_BINARY,
            "THRESH_BINARY_INV": cv2.THRESH_BINARY_INV,
            "THRESH_TRUNC": cv2.THRESH_TRUNC,
            "THRESH_TOZERO": cv2.THRESH_TOZERO,
            "THRESH_TOZERO_INV": cv2.THRESH_TOZERO_INV
        }
        
        _, result = cv2.threshold(gray, threshold, max_value, type_dict[threshold_type])
        
        # 如果输入是彩色图像，转换回彩色
        if len(image.shape) == 3:
            result = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)
        
        return {"image": result}
