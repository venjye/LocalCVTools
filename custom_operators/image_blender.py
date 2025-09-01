"""
图像混合算子
"""
import cv2
import numpy as np
from core.operator import BaseOperator, Parameter


class ImageBlender(BaseOperator):
    """图像混合算子"""
    
    def __init__(self):
        super().__init__("Image Blender")

    def _setup_parameters(self):
        """设置算子参数"""
        self.add_parameter(Parameter("alpha", float, 0.5, 0.0, 1.0, "第一张图像的权重"))
        self.add_parameter(Parameter("beta", float, 0.5, 0.0, 1.0, "第二张图像的权重"))
        self.add_parameter(Parameter("gamma", float, 0.0, -100.0, 100.0, "亮度调整"))

    def _setup_ports(self):
        """设置输入输出端口"""
        self.input_ports = ["image1", "image2"]
        self.output_ports = ["image"]

    def process(self, inputs):
        """处理函数"""
        image1 = inputs.get("image1")
        image2 = inputs.get("image2")
        
        if image1 is None or image2 is None:
            # 如果只有一张图像，直接返回
            return {"image": image1 if image1 is not None else image2}
        
        alpha = self.get_parameter("alpha")
        beta = self.get_parameter("beta")
        gamma = self.get_parameter("gamma")
        
        # 确保两张图像尺寸相同
        h1, w1 = image1.shape[:2]
        h2, w2 = image2.shape[:2]
        
        if h1 != h2 or w1 != w2:
            # 调整第二张图像的尺寸
            image2 = cv2.resize(image2, (w1, h1))
        
        # 图像混合
        result = cv2.addWeighted(image1, alpha, image2, beta, gamma)
        
        return {"image": result}
