"""
边缘检测算子实现
"""
import cv2
import numpy as np
from core.operator import BaseOperator, Parameter


class CannyOperator(BaseOperator):
    """Canny边缘检测算子"""
    
    def __init__(self):
        super().__init__("Canny Edge Detection")

    def _setup_parameters(self):
        self.add_parameter(Parameter("low_threshold", float, 50.0, 0.0, 255.0, "低阈值"))
        self.add_parameter(Parameter("high_threshold", float, 150.0, 0.0, 255.0, "高阈值"))
        self.add_parameter(Parameter("aperture_size", int, 3, 3, 7, "Sobel核大小"))
        self.add_parameter(Parameter("l2_gradient", bool, False, description="使用L2梯度"))

    def _setup_ports(self):
        self.input_ports = ["image"]
        self.output_ports = ["image"]

    def process(self, inputs):
        image = inputs["image"]
        low_threshold = self.get_parameter("low_threshold")
        high_threshold = self.get_parameter("high_threshold")
        aperture_size = self.get_parameter("aperture_size")
        l2_gradient = self.get_parameter("l2_gradient")
        
        # 转换为灰度图
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # 确保aperture_size为奇数
        if aperture_size % 2 == 0:
            aperture_size += 1
        
        result = cv2.Canny(gray, low_threshold, high_threshold, 
                          apertureSize=aperture_size, L2gradient=l2_gradient)
        
        # 转换回彩色图像格式
        if len(image.shape) == 3:
            result = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)
        
        return {"image": result}


class HoughLinesOperator(BaseOperator):
    """霍夫直线检测算子"""
    
    def __init__(self):
        super().__init__("Hough Lines")

    def _setup_parameters(self):
        self.add_parameter(Parameter("rho", float, 1.0, 0.1, 10.0, "距离分辨率"))
        self.add_parameter(Parameter("theta", float, np.pi/180, 0.001, 0.1, "角度分辨率"))
        self.add_parameter(Parameter("threshold", int, 100, 1, 500, "累加器阈值"))
        self.add_parameter(Parameter("min_line_length", int, 50, 1, 500, "最小线段长度"))
        self.add_parameter(Parameter("max_line_gap", int, 10, 1, 100, "最大线段间隙"))

    def _setup_ports(self):
        self.input_ports = ["image"]
        self.output_ports = ["image"]

    def process(self, inputs):
        image = inputs["image"]
        rho = self.get_parameter("rho")
        theta = self.get_parameter("theta")
        threshold = self.get_parameter("threshold")
        min_line_length = self.get_parameter("min_line_length")
        max_line_gap = self.get_parameter("max_line_gap")
        
        # 转换为灰度图
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # 先进行边缘检测
        edges = cv2.Canny(gray, 50, 150)
        
        # 霍夫直线检测
        lines = cv2.HoughLinesP(edges, rho, theta, threshold, 
                               minLineLength=min_line_length, maxLineGap=max_line_gap)
        
        # 在原图上绘制直线
        result = image.copy()
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                cv2.line(result, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        return {"image": result}


class HoughCirclesOperator(BaseOperator):
    """霍夫圆检测算子"""
    
    def __init__(self):
        super().__init__("Hough Circles")

    def _setup_parameters(self):
        self.add_parameter(Parameter("dp", float, 1.0, 0.1, 10.0, "累加器分辨率"))
        self.add_parameter(Parameter("min_dist", int, 50, 1, 500, "圆心最小距离"))
        self.add_parameter(Parameter("param1", float, 50.0, 1.0, 300.0, "Canny高阈值"))
        self.add_parameter(Parameter("param2", float, 30.0, 1.0, 300.0, "累加器阈值"))
        self.add_parameter(Parameter("min_radius", int, 0, 0, 500, "最小半径"))
        self.add_parameter(Parameter("max_radius", int, 0, 0, 500, "最大半径"))

    def _setup_ports(self):
        self.input_ports = ["image"]
        self.output_ports = ["image"]

    def process(self, inputs):
        image = inputs["image"]
        dp = self.get_parameter("dp")
        min_dist = self.get_parameter("min_dist")
        param1 = self.get_parameter("param1")
        param2 = self.get_parameter("param2")
        min_radius = self.get_parameter("min_radius")
        max_radius = self.get_parameter("max_radius")
        
        # 转换为灰度图
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # 霍夫圆检测
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp, min_dist,
                                  param1=param1, param2=param2,
                                  minRadius=min_radius, maxRadius=max_radius)
        
        # 在原图上绘制圆
        result = image.copy()
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            for (x, y, r) in circles:
                cv2.circle(result, (x, y), r, (0, 255, 0), 2)
                cv2.circle(result, (x, y), 2, (0, 0, 255), 3)
        
        return {"image": result}


class ContourDetectionOperator(BaseOperator):
    """轮廓检测算子"""
    
    def __init__(self):
        super().__init__("Contour Detection")

    def _setup_parameters(self):
        self.add_parameter(Parameter("threshold", int, 127, 0, 255, "二值化阈值"))
        self.add_parameter(Parameter("mode", str, "RETR_EXTERNAL", 
                                   options=["RETR_EXTERNAL", "RETR_LIST", "RETR_CCOMP", "RETR_TREE"],
                                   description="轮廓检索模式"))
        self.add_parameter(Parameter("method", str, "CHAIN_APPROX_SIMPLE",
                                   options=["CHAIN_APPROX_NONE", "CHAIN_APPROX_SIMPLE"],
                                   description="轮廓近似方法"))
        self.add_parameter(Parameter("min_area", int, 100, 0, 10000, "最小轮廓面积"))

    def _setup_ports(self):
        self.input_ports = ["image"]
        self.output_ports = ["image"]

    def process(self, inputs):
        image = inputs["image"]
        threshold_val = self.get_parameter("threshold")
        mode = self.get_parameter("mode")
        method = self.get_parameter("method")
        min_area = self.get_parameter("min_area")
        
        # 转换为灰度图
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # 二值化
        _, binary = cv2.threshold(gray, threshold_val, 255, cv2.THRESH_BINARY)
        
        # 轮廓检测
        mode_dict = {
            "RETR_EXTERNAL": cv2.RETR_EXTERNAL,
            "RETR_LIST": cv2.RETR_LIST,
            "RETR_CCOMP": cv2.RETR_CCOMP,
            "RETR_TREE": cv2.RETR_TREE
        }
        
        method_dict = {
            "CHAIN_APPROX_NONE": cv2.CHAIN_APPROX_NONE,
            "CHAIN_APPROX_SIMPLE": cv2.CHAIN_APPROX_SIMPLE
        }
        
        contours, _ = cv2.findContours(binary, mode_dict[mode], method_dict[method])
        
        # 过滤小轮廓
        filtered_contours = [cnt for cnt in contours if cv2.contourArea(cnt) >= min_area]
        
        # 在原图上绘制轮廓
        result = image.copy()
        cv2.drawContours(result, filtered_contours, -1, (0, 255, 0), 2)
        
        return {"image": result}
