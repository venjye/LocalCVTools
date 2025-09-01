"""
算子基类定义
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import cv2


class Parameter:
    """参数定义类"""
    def __init__(self, name: str, param_type: type, default_value: Any, 
                 min_value: Any = None, max_value: Any = None, 
                 description: str = "", options: List[Any] = None):
        self.name = name
        self.param_type = param_type
        self.default_value = default_value
        self.min_value = min_value
        self.max_value = max_value
        self.description = description
        self.options = options  # 用于枚举类型参数
        self.current_value = default_value

    def set_value(self, value: Any):
        """设置参数值，包含类型和范围检查"""
        if self.param_type == bool:
            self.current_value = bool(value)
        elif self.param_type == int:
            val = int(value)
            if self.min_value is not None:
                val = max(val, self.min_value)
            if self.max_value is not None:
                val = min(val, self.max_value)
            self.current_value = val
        elif self.param_type == float:
            val = float(value)
            if self.min_value is not None:
                val = max(val, self.min_value)
            if self.max_value is not None:
                val = min(val, self.max_value)
            self.current_value = val
        elif self.param_type == str:
            if self.options and value not in self.options:
                raise ValueError(f"Value {value} not in options {self.options}")
            self.current_value = str(value)
        else:
            self.current_value = value

    def get_value(self):
        return self.current_value


class BaseOperator(ABC):
    """算子基类"""
    
    def __init__(self, name: str):
        self.name = name
        self.id = id(self)  # 使用对象id作为唯一标识
        self.parameters: Dict[str, Parameter] = {}
        self.input_ports: List[str] = []  # 输入端口名称列表
        self.output_ports: List[str] = []  # 输出端口名称列表
        self.cached_result: Optional[Dict[str, np.ndarray]] = None
        self.inputs_hash: Optional[str] = None
        self._setup_parameters()
        self._setup_ports()

    @abstractmethod
    def _setup_parameters(self):
        """设置算子参数，子类必须实现"""
        pass

    @abstractmethod
    def _setup_ports(self):
        """设置输入输出端口，子类必须实现"""
        pass

    @abstractmethod
    def process(self, inputs: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """处理函数，子类必须实现"""
        pass

    def add_parameter(self, param: Parameter):
        """添加参数"""
        self.parameters[param.name] = param

    def set_parameter(self, name: str, value: Any):
        """设置参数值"""
        if name in self.parameters:
            self.parameters[name].set_value(value)
            # 参数改变时清除缓存
            self.cached_result = None
            self.inputs_hash = None

    def get_parameter(self, name: str) -> Any:
        """获取参数值"""
        if name in self.parameters:
            return self.parameters[name].get_value()
        return None

    def get_parameters_dict(self) -> Dict[str, Any]:
        """获取所有参数的字典"""
        return {name: param.get_value() for name, param in self.parameters.items()}

    def _calculate_inputs_hash(self, inputs: Dict[str, np.ndarray]) -> str:
        """计算输入数据的哈希值，用于缓存"""
        import hashlib
        hasher = hashlib.md5()
        
        # 添加参数到哈希
        for name, param in self.parameters.items():
            hasher.update(f"{name}:{param.get_value()}".encode())
        
        # 添加输入图像到哈希
        for port_name, image in inputs.items():
            if image is not None:
                hasher.update(f"{port_name}:{image.shape}:{image.dtype}".encode())
                # 只使用图像的一小部分来计算哈希，提高性能
                sample = image[::max(1, image.shape[0]//10), ::max(1, image.shape[1]//10)]
                hasher.update(sample.tobytes())
        
        return hasher.hexdigest()

    def execute(self, inputs: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """执行算子，包含缓存机制"""
        # 检查输入是否有效
        for port in self.input_ports:
            if port not in inputs or inputs[port] is None:
                raise ValueError(f"Missing input for port: {port}")

        # 计算当前输入的哈希
        current_hash = self._calculate_inputs_hash(inputs)
        
        # 如果哈希相同且有缓存，直接返回缓存结果
        if self.inputs_hash == current_hash and self.cached_result is not None:
            return self.cached_result.copy()

        # 执行处理
        try:
            result = self.process(inputs)
            
            # 缓存结果
            self.cached_result = result.copy() if result else None
            self.inputs_hash = current_hash
            
            return result
        except Exception as e:
            raise RuntimeError(f"Error in operator {self.name}: {str(e)}")

    def get_info(self) -> Dict[str, Any]:
        """获取算子信息"""
        return {
            'name': self.name,
            'id': self.id,
            'input_ports': self.input_ports,
            'output_ports': self.output_ports,
            'parameters': {name: {
                'type': param.param_type.__name__,
                'default': param.default_value,
                'current': param.current_value,
                'min': param.min_value,
                'max': param.max_value,
                'description': param.description,
                'options': param.options
            } for name, param in self.parameters.items()}
        }


class ImageInputOperator(BaseOperator):
    """图像输入算子"""
    
    def __init__(self):
        super().__init__("Image Input")
        self.image_path = ""
        self.image_data = None

    def _setup_parameters(self):
        pass  # 图像输入算子没有参数

    def _setup_ports(self):
        self.input_ports = []
        self.output_ports = ["image"]

    def load_image(self, path: str):
        """加载图像"""
        self.image_path = path
        self.image_data = cv2.imread(path)
        if self.image_data is None:
            raise ValueError(f"Cannot load image from {path}")
        # 清除缓存
        self.cached_result = None
        self.inputs_hash = None

    def process(self, inputs: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """返回加载的图像"""
        if self.image_data is None:
            raise ValueError("No image loaded")
        return {"image": self.image_data.copy()}
