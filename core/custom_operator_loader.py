"""
自定义算子加载器
"""
import os
import sys
import importlib.util
import inspect
from typing import Dict, List, Type
from core.operator import BaseOperator


class CustomOperatorLoader:
    """自定义算子加载器"""
    
    def __init__(self, custom_operators_dir: str = "custom_operators"):
        self.custom_operators_dir = custom_operators_dir
        self.loaded_operators: Dict[str, Type[BaseOperator]] = {}
        self.operator_files: Dict[str, str] = {}  # 算子名 -> 文件路径
    
    def scan_custom_operators(self) -> Dict[str, Type[BaseOperator]]:
        """扫描并加载自定义算子"""
        if not os.path.exists(self.custom_operators_dir):
            os.makedirs(self.custom_operators_dir)
            return {}
        
        self.loaded_operators.clear()
        self.operator_files.clear()
        
        # 遍历自定义算子目录
        for filename in os.listdir(self.custom_operators_dir):
            if filename.endswith('.py') and filename != '__init__.py':
                filepath = os.path.join(self.custom_operators_dir, filename)
                self._load_operators_from_file(filepath)
        
        return self.loaded_operators.copy()
    
    def _load_operators_from_file(self, filepath: str):
        """从文件加载算子"""
        try:
            # 动态导入模块
            module_name = os.path.splitext(os.path.basename(filepath))[0]
            spec = importlib.util.spec_from_file_location(module_name, filepath)
            if spec is None or spec.loader is None:
                return
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 查找BaseOperator的子类
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if (issubclass(obj, BaseOperator) and 
                    obj != BaseOperator and 
                    obj.__module__ == module.__name__):
                    
                    self.loaded_operators[name] = obj
                    self.operator_files[name] = filepath
                    print(f"Loaded custom operator: {name} from {filepath}")
        
        except Exception as e:
            print(f"Error loading operators from {filepath}: {e}")
    
    def reload_operator(self, operator_name: str) -> bool:
        """重新加载指定算子"""
        if operator_name not in self.operator_files:
            return False
        
        filepath = self.operator_files[operator_name]
        
        # 移除旧的算子
        if operator_name in self.loaded_operators:
            del self.loaded_operators[operator_name]
        
        # 重新加载
        self._load_operators_from_file(filepath)
        
        return operator_name in self.loaded_operators
    
    def get_operator_info(self, operator_name: str) -> Dict:
        """获取算子信息"""
        if operator_name not in self.loaded_operators:
            return {}
        
        operator_class = self.loaded_operators[operator_name]
        
        # 创建临时实例获取信息
        try:
            temp_instance = operator_class()
            info = temp_instance.get_info()
            info['file_path'] = self.operator_files.get(operator_name, "")
            info['is_custom'] = True
            return info
        except Exception as e:
            return {
                'name': operator_name,
                'error': str(e),
                'file_path': self.operator_files.get(operator_name, ""),
                'is_custom': True
            }
    
    def create_operator_template(self, operator_name: str, filepath: str = None) -> str:
        """创建算子模板文件"""
        if filepath is None:
            filepath = os.path.join(self.custom_operators_dir, f"{operator_name.lower()}.py")
        
        template = f'''"""
自定义算子: {operator_name}
"""
import cv2
import numpy as np
from core.operator import BaseOperator, Parameter


class {operator_name}(BaseOperator):
    """自定义算子: {operator_name}"""
    
    def __init__(self):
        super().__init__("{operator_name}")

    def _setup_parameters(self):
        """设置算子参数"""
        # 示例参数
        self.add_parameter(Parameter("param1", int, 1, 1, 100, "参数1描述"))
        self.add_parameter(Parameter("param2", float, 1.0, 0.1, 10.0, "参数2描述"))
        self.add_parameter(Parameter("param3", bool, True, description="参数3描述"))

    def _setup_ports(self):
        """设置输入输出端口"""
        self.input_ports = ["image"]
        self.output_ports = ["image"]

    def process(self, inputs):
        """处理函数"""
        image = inputs["image"]
        
        # 获取参数
        param1 = self.get_parameter("param1")
        param2 = self.get_parameter("param2")
        param3 = self.get_parameter("param3")
        
        # 在这里实现你的图像处理逻辑
        # 示例: 简单的图像复制
        result = image.copy()
        
        # 示例: 根据参数进行一些处理
        if param3:
            # 应用高斯模糊
            result = cv2.GaussianBlur(result, (param1*2+1, param1*2+1), param2)
        
        return {{"image": result}}
'''
        
        # 确保目录存在
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # 写入文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(template)
        
        return filepath


def create_example_custom_operators():
    """创建示例自定义算子"""
    loader = CustomOperatorLoader()
    
    # 创建一个简单的颜色空间转换算子
    color_convert_template = '''"""
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
'''
    
    # 创建一个图像混合算子
    blend_template = '''"""
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
'''
    
    # 写入示例文件
    custom_dir = "custom_operators"
    os.makedirs(custom_dir, exist_ok=True)
    
    with open(os.path.join(custom_dir, "color_converter.py"), 'w', encoding='utf-8') as f:
        f.write(color_convert_template)
    
    with open(os.path.join(custom_dir, "image_blender.py"), 'w', encoding='utf-8') as f:
        f.write(blend_template)
    
    print("Created example custom operators:")
    print("- custom_operators/color_converter.py")
    print("- custom_operators/image_blender.py")


if __name__ == "__main__":
    # 创建示例自定义算子
    create_example_custom_operators()
    
    # 测试加载器
    loader = CustomOperatorLoader()
    operators = loader.scan_custom_operators()
    
    print(f"\\nLoaded {len(operators)} custom operators:")
    for name, op_class in operators.items():
        print(f"- {name}: {op_class}")
        info = loader.get_operator_info(name)
        print(f"  Info: {info}")
