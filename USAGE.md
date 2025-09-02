# LocalCVTools 使用指南

## 安装依赖

### 方法1：使用conda（推荐）
```bash
conda install pyqt opencv numpy pillow matplotlib
```

### 方法2：使用pip
```bash
pip install PyQt5 opencv-python numpy Pillow matplotlib
```

如果遇到PyQt5安装问题，可以尝试：
```bash
# macOS
brew install qt5
pip install PyQt5

# Ubuntu/Debian
sudo apt-get install python3-pyqt5
pip install opencv-python numpy Pillow matplotlib

# Windows
pip install PyQt5 opencv-python numpy Pillow matplotlib
```

## 运行程序

```bash
python main.py
```

## 基本使用流程

### 1. 加载图像
- 点击工具栏的"📁 Open"按钮或使用快捷键 `Ctrl+O`
- 选择要处理的图像文件
- 注意：需要先添加"Image Input"算子

### 2. 添加算子
- 在左侧算子库中双击算子名称
- 算子会自动添加到中央的节点编辑器中
- 可用的算子类别：
  - **Filters**: 高斯模糊、中值滤波、双边滤波等
  - **Edge Detection**: Canny边缘检测、霍夫变换等
  - **Morphology**: 腐蚀、膨胀、开闭运算等
  - **Custom**: 自定义算子

### 3. 连接算子
- 从输出端口（右侧圆点）拖拽到输入端口（左侧圆点）
- 连接线会显示为贝塞尔曲线
- 每个输入端口只能有一个连接

### 4. 调整参数
- 选中算子节点
- 在左侧参数面板中调整参数
- 参数会实时更新到算子中

### 5. 执行管道
- 点击"▶️ Execute"按钮或按 `F5`
- 处理结果会显示在右侧图像查看器中
- 可以在"Result"和"Compare"标签页之间切换

## 快捷键

- `Ctrl+O`: 打开图像
- `Ctrl+S`: 保存管道配置
- `Ctrl+L`: 加载管道配置
- `F5`: 执行管道
- `Ctrl+Del`: 清空管道
- `Delete`: 删除选中的节点
- `Ctrl+A`: 全选节点
- `Ctrl+D`: 取消选择
- 鼠标滚轮: 缩放视图
- 鼠标拖拽: 移动节点

## 自定义算子

### 创建自定义算子
1. 使用菜单 `Tools -> Create Operator Template`
2. 输入算子名称
3. 编辑生成的Python文件
4. 使用 `Tools -> Reload Custom Operators` 加载

### 自定义算子模板
```python
from core.operator import BaseOperator, Parameter
import cv2
import numpy as np

class MyCustomOperator(BaseOperator):
    def __init__(self):
        super().__init__("My Custom Operator")

    def _setup_parameters(self):
        self.add_parameter(Parameter("param1", int, 1, 1, 100, "参数描述"))

    def _setup_ports(self):
        self.input_ports = ["image"]
        self.output_ports = ["image"]

    def process(self, inputs):
        image = inputs["image"]
        param1 = self.get_parameter("param1")
        
        # 在这里实现你的图像处理逻辑
        result = image.copy()
        
        return {"image": result}
```

## 示例工作流

### 基础边缘检测流程
1. 添加 "Image Input" 算子
2. 添加 "Gaussian Blur" 算子
3. 添加 "Canny Edge Detection" 算子
4. 连接: Image Input -> Gaussian Blur -> Canny
5. 调整高斯模糊的kernel_size和sigma参数
6. 调整Canny的阈值参数
7. 执行管道查看结果

### 形态学处理流程
1. 添加 "Image Input" 算子
2. 添加 "Threshold" 算子进行二值化
3. 添加 "Opening" 算子去除噪点
4. 添加 "Closing" 算子填充空洞
5. 连接并调整参数
6. 执行查看效果

## 故障排除

### 常见问题

1. **PyQt5安装失败**
   - 确保系统已安装Qt开发环境
   - 尝试使用conda安装
   - 检查Python版本兼容性

2. **图像无法加载**
   - 确保已添加"Image Input"算子
   - 检查图像文件格式是否支持
   - 确保文件路径正确

3. **算子执行失败**
   - 检查算子连接是否正确
   - 确保输入图像格式符合要求
   - 查看状态栏的错误信息

4. **自定义算子无法加载**
   - 检查Python语法是否正确
   - 确保继承了BaseOperator类
   - 使用"Reload Custom Operators"重新加载

### 性能优化

- 使用缓存机制，相同输入和参数不会重复计算
- 大图像处理时可能需要较长时间
- 复杂的算子链可能消耗大量内存

## 扩展功能

### 支持的图像格式
- PNG, JPG, JPEG, BMP, TIFF, TIF

### 参数类型
- `int`: 整数，支持滑块和数值输入
- `float`: 浮点数，支持滑块和数值输入  
- `bool`: 布尔值，使用复选框
- `str`: 字符串，支持下拉选择和文本输入

### 端口系统
- 每个算子可以有多个输入和输出端口
- 支持不同名称的端口用于特殊用途
- 自动类型检查和连接验证
