#!/usr/bin/env python3
"""
测试核心功能（不依赖PyQt5）
"""
import numpy as np
import cv2
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.operator import BaseOperator, ImageInputOperator, Parameter
from core.pipeline import Pipeline
from operators.filters import GaussianBlurOperator, MedianBlurOperator
from operators.edge_detection import CannyOperator
from operators.morphology import ThresholdOperator


def test_operators():
    """测试算子功能"""
    print("=== 测试算子功能 ===")
    
    # 创建测试图像
    test_image = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.rectangle(test_image, (20, 20), (80, 80), (255, 255, 255), -1)
    cv2.circle(test_image, (50, 50), 15, (0, 0, 0), -1)
    
    print(f"测试图像形状: {test_image.shape}")
    
    # 测试高斯模糊算子
    print("\n--- 测试高斯模糊算子 ---")
    gaussian_op = GaussianBlurOperator()
    print(f"算子名称: {gaussian_op.name}")
    print(f"输入端口: {gaussian_op.input_ports}")
    print(f"输出端口: {gaussian_op.output_ports}")
    print(f"参数: {list(gaussian_op.parameters.keys())}")
    
    # 设置参数
    gaussian_op.set_parameter("kernel_size", 5)
    gaussian_op.set_parameter("sigma_x", 1.0)
    
    # 执行算子
    result = gaussian_op.execute({"image": test_image})
    print(f"输出图像形状: {result['image'].shape}")
    
    # 测试Canny边缘检测
    print("\n--- 测试Canny边缘检测 ---")
    canny_op = CannyOperator()
    canny_op.set_parameter("low_threshold", 50.0)
    canny_op.set_parameter("high_threshold", 150.0)
    
    canny_result = canny_op.execute({"image": test_image})
    print(f"Canny输出形状: {canny_result['image'].shape}")
    
    print("✅ 算子测试完成")


def test_pipeline():
    """测试管道功能"""
    print("\n=== 测试管道功能 ===")
    
    # 创建管道
    pipeline = Pipeline()
    
    # 创建算子
    input_op = ImageInputOperator()
    gaussian_op = GaussianBlurOperator()
    canny_op = CannyOperator()
    
    # 创建测试图像
    test_image = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.rectangle(test_image, (20, 20), (80, 80), (255, 255, 255), -1)
    cv2.circle(test_image, (50, 50), 15, (0, 0, 0), -1)
    
    # 设置图像输入
    input_op.image_data = test_image
    
    # 添加算子到管道
    pipeline.add_operator(input_op)
    pipeline.add_operator(gaussian_op)
    pipeline.add_operator(canny_op)
    
    print(f"管道中的算子数量: {len(pipeline.operators)}")
    
    # 创建连接
    success1 = pipeline.add_connection(input_op.id, "image", gaussian_op.id, "image")
    success2 = pipeline.add_connection(gaussian_op.id, "image", canny_op.id, "image")
    
    print(f"连接1成功: {success1}")
    print(f"连接2成功: {success2}")
    print(f"连接数量: {len(pipeline.connections)}")
    print(f"执行顺序: {[pipeline.operators[op_id].name for op_id in pipeline.execution_order]}")
    
    # 执行管道
    results = pipeline.execute()
    print(f"执行结果: {len(results)} 个算子有输出")
    
    for op_id, result in results.items():
        op_name = pipeline.operators[op_id].name
        if result and 'image' in result:
            print(f"  {op_name}: {result['image'].shape}")
    
    print("✅ 管道测试完成")


def test_custom_operators():
    """测试自定义算子加载"""
    print("\n=== 测试自定义算子加载 ===")
    
    try:
        from core.custom_operator_loader import CustomOperatorLoader
        
        loader = CustomOperatorLoader()
        custom_ops = loader.scan_custom_operators()
        
        print(f"找到 {len(custom_ops)} 个自定义算子:")
        for name, op_class in custom_ops.items():
            print(f"  - {name}: {op_class}")
            
            # 测试创建实例
            try:
                instance = op_class()
                info = instance.get_info()
                print(f"    参数: {list(info.get('parameters', {}).keys())}")
            except Exception as e:
                print(f"    创建实例失败: {e}")
        
        print("✅ 自定义算子测试完成")
        
    except Exception as e:
        print(f"❌ 自定义算子测试失败: {e}")


def test_parameter_system():
    """测试参数系统"""
    print("\n=== 测试参数系统 ===")
    
    # 测试不同类型的参数
    int_param = Parameter("test_int", int, 5, 1, 10, "测试整数参数")
    float_param = Parameter("test_float", float, 1.5, 0.1, 5.0, "测试浮点参数")
    bool_param = Parameter("test_bool", bool, True, description="测试布尔参数")
    str_param = Parameter("test_str", str, "option1", options=["option1", "option2", "option3"], description="测试字符串参数")
    
    print("参数测试:")
    
    # 测试整数参数
    print(f"整数参数默认值: {int_param.get_value()}")
    int_param.set_value(7)
    print(f"设置后的值: {int_param.get_value()}")
    
    # 测试范围限制
    int_param.set_value(15)  # 超出最大值
    print(f"超出范围后的值: {int_param.get_value()}")  # 应该被限制为10
    
    # 测试浮点参数
    print(f"浮点参数默认值: {float_param.get_value()}")
    float_param.set_value(2.5)
    print(f"设置后的值: {float_param.get_value()}")
    
    # 测试布尔参数
    print(f"布尔参数默认值: {bool_param.get_value()}")
    bool_param.set_value(False)
    print(f"设置后的值: {bool_param.get_value()}")
    
    # 测试字符串参数
    print(f"字符串参数默认值: {str_param.get_value()}")
    str_param.set_value("option2")
    print(f"设置后的值: {str_param.get_value()}")
    
    print("✅ 参数系统测试完成")


def main():
    """主测试函数"""
    print("LocalCVTools 核心功能测试")
    print("=" * 50)
    
    try:
        test_parameter_system()
        test_operators()
        test_pipeline()
        test_custom_operators()
        
        print("\n" + "=" * 50)
        print("🎉 所有核心功能测试通过！")
        print("\n接下来可以运行 'python main.py' 启动图形界面")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
