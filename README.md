# LocalCVTools - OpenCV算子调试工具

一个基于PyQt5的可视化OpenCV算子调试工具，支持拖拽式算子编排和实时结果预览。

## 功能特性

- 🎯 可视化节点编辑器，支持拖拽连接算子
- 🔧 内置常用OpenCV算子（滤波、边缘检测、形态学操作等）
- 🎨 实时预览每个算子的处理结果
- 📝 支持自定义算子扩展
- 💾 算子链保存和加载
- 🖼️ 多种图像格式支持

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行

```bash
python main.py
```

## 项目结构

```
LocalCVTools/
├── main.py                 # 主程序入口
├── core/                   # 核心模块
│   ├── __init__.py
│   ├── operator.py         # 算子基类
│   ├── pipeline.py         # 处理管道
│   └── node_editor.py      # 节点编辑器
├── operators/              # 内置算子
│   ├── __init__.py
│   ├── filters.py          # 滤波算子
│   ├── morphology.py       # 形态学算子
│   └── edge_detection.py   # 边缘检测算子
├── ui/                     # 界面组件
│   ├── __init__.py
│   ├── main_window.py      # 主窗口
│   ├── node_widget.py      # 节点组件
│   └── image_viewer.py     # 图像查看器
└── custom_operators/       # 自定义算子目录
    └── __init__.py
```
