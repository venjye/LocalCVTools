"""
颜色空间转换算子
"""
import cv2
import numpy as np
from core.operator import BaseOperator, Parameter


class ColorSpaceConverter(BaseOperator):
    """颜色空间转换算子"""
    
    def __init__(self):
        super().__init__("Color Space Converter")

    def _setup_parameters(self):
        """设置算子参数"""
        self.add_parameter(Parameter("conversion", str, "BGR2GRAY",
                                   options=["BGR2GRAY", "BGR2HSV", "BGR2LAB", "BGR2RGB", "GRAY2BGR"],
                                   description="颜色空间转换类型"))

    def _setup_ports(self):
        """设置输入输出端口"""
        self.input_ports = ["image"]
        self.output_ports = ["image"]

    def process(self, inputs):
        """处理函数"""
        image = inputs["image"]
        conversion = self.get_parameter("conversion")
        
        # 颜色空间转换映射
        conversion_map = {
            "BGR2GRAY": cv2.COLOR_BGR2GRAY,
            "BGR2HSV": cv2.COLOR_BGR2HSV,
            "BGR2LAB": cv2.COLOR_BGR2LAB,
            "BGR2RGB": cv2.COLOR_BGR2RGB,
            "GRAY2BGR": cv2.COLOR_GRAY2BGR,
        }
        
        if conversion in conversion_map:
            if conversion == "GRAY2BGR" and len(image.shape) == 3:
                # 如果输入已经是彩色图像，先转为灰度再转回彩色
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                result = cv2.cvtColor(gray, conversion_map[conversion])
            else:
                result = cv2.cvtColor(image, conversion_map[conversion])
        else:
            result = image.copy()
        
        return {"image": result}
