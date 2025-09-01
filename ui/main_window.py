"""
主窗口界面
"""
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import os
from typing import Dict, List, Optional

from core.operator import BaseOperator, ImageInputOperator
from core.pipeline import Pipeline
from core.node_editor import NodeEditor
from core.custom_operator_loader import CustomOperatorLoader
from ui.image_viewer import ImageViewer, ImageComparisonViewer
from ui.parameter_panel import ParameterPanel

# 导入所有算子
from operators.filters import *
from operators.edge_detection import *
from operators.morphology import *


class OperatorLibrary(QWidget):
    """算子库面板"""
    
    operator_requested = pyqtSignal(str)  # 请求创建算子
    
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel("Operator Library")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        layout.addWidget(title_label)
        
        # 创建算子列表
        self.operator_list = QListWidget()
        self.operator_list.itemDoubleClicked.connect(self._on_operator_double_clicked)
        
        # 添加算子类别
        self._add_operators()
        
        layout.addWidget(self.operator_list)
        self.setLayout(layout)
    
    def _add_operators(self):
        """添加算子到列表"""
        # 输入算子
        input_item = QListWidgetItem("📁 Image Input")
        input_item.setData(Qt.UserRole, "ImageInputOperator")
        self.operator_list.addItem(input_item)
        
        # 分隔符
        separator = QListWidgetItem("─── Filters ───")
        separator.setFlags(Qt.NoItemFlags)
        self.operator_list.addItem(separator)
        
        # 滤波算子
        filters = [
            ("🔍 Gaussian Blur", "GaussianBlurOperator"),
            ("🔍 Median Blur", "MedianBlurOperator"),
            ("🔍 Bilateral Filter", "BilateralFilterOperator"),
            ("🔍 Box Filter", "BoxFilterOperator"),
            ("🔍 Laplacian", "LaplacianOperator"),
            ("🔍 Sobel", "SobelOperator"),
        ]
        
        for name, class_name in filters:
            item = QListWidgetItem(name)
            item.setData(Qt.UserRole, class_name)
            self.operator_list.addItem(item)
        
        # 边缘检测
        separator = QListWidgetItem("─── Edge Detection ───")
        separator.setFlags(Qt.NoItemFlags)
        self.operator_list.addItem(separator)
        
        edge_operators = [
            ("📐 Canny", "CannyOperator"),
            ("📐 Hough Lines", "HoughLinesOperator"),
            ("📐 Hough Circles", "HoughCirclesOperator"),
            ("📐 Contours", "ContourDetectionOperator"),
        ]
        
        for name, class_name in edge_operators:
            item = QListWidgetItem(name)
            item.setData(Qt.UserRole, class_name)
            self.operator_list.addItem(item)
        
        # 形态学操作
        separator = QListWidgetItem("─── Morphology ───")
        separator.setFlags(Qt.NoItemFlags)
        self.operator_list.addItem(separator)
        
        morph_operators = [
            ("⚫ Erosion", "ErosionOperator"),
            ("⚪ Dilation", "DilationOperator"),
            ("🔓 Opening", "OpeningOperator"),
            ("🔒 Closing", "ClosingOperator"),
            ("📊 Gradient", "GradientOperator"),
            ("🎩 Top Hat", "TopHatOperator"),
            ("🎩 Black Hat", "BlackHatOperator"),
            ("🔲 Threshold", "ThresholdOperator"),
        ]
        
        for name, class_name in morph_operators:
            item = QListWidgetItem(name)
            item.setData(Qt.UserRole, class_name)
            self.operator_list.addItem(item)

    def add_custom_operators(self, custom_operators: dict):
        """添加自定义算子到列表"""
        if not custom_operators:
            return

        # 添加分隔符
        separator = QListWidgetItem("─── Custom ───")
        separator.setFlags(Qt.NoItemFlags)
        self.operator_list.addItem(separator)

        # 添加自定义算子
        for class_name in custom_operators.keys():
            item = QListWidgetItem(f"🔧 {class_name}")
            item.setData(Qt.UserRole, class_name)
            self.operator_list.addItem(item)
    
    def _on_operator_double_clicked(self, item):
        """算子双击事件"""
        class_name = item.data(Qt.UserRole)
        if class_name:
            self.operator_requested.emit(class_name)


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("LocalCVTools - OpenCV算子调试工具")
        self.setGeometry(100, 100, 1400, 900)
        
        # 核心组件
        self.pipeline = Pipeline()
        self.custom_loader = CustomOperatorLoader()
        self.operator_factory = self._create_operator_factory()

        # 当前选中的算子
        self.current_operator = None
        
        # 创建界面
        self._create_ui()
        self._create_menu_bar()
        self._create_toolbar()
        self._create_status_bar()

        # 加载自定义算子
        self._load_custom_operators()

        # 连接信号
        self._connect_signals()
    
    def _create_ui(self):
        """创建用户界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout()
        
        # 左侧面板
        left_panel = QWidget()
        left_panel.setMaximumWidth(250)
        left_layout = QVBoxLayout()
        
        # 算子库
        self.operator_library = OperatorLibrary()
        left_layout.addWidget(self.operator_library)
        
        # 参数面板
        self.parameter_panel = ParameterPanel()
        left_layout.addWidget(self.parameter_panel)
        
        left_panel.setLayout(left_layout)
        
        # 中央区域 - 节点编辑器
        self.node_editor = NodeEditor()
        
        # 右侧面板 - 图像显示
        right_panel = QWidget()
        right_panel.setMaximumWidth(400)
        right_layout = QVBoxLayout()
        
        # 图像查看器选项卡
        self.image_tabs = QTabWidget()
        
        # 单图像查看器
        self.single_viewer = ImageViewer()
        self.image_tabs.addTab(self.single_viewer, "Result")
        
        # 对比查看器
        self.comparison_viewer = ImageComparisonViewer()
        self.image_tabs.addTab(self.comparison_viewer, "Compare")
        
        right_layout.addWidget(self.image_tabs)
        
        # 执行按钮
        execute_btn = QPushButton("Execute Pipeline")
        execute_btn.clicked.connect(self._execute_pipeline)
        execute_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; padding: 8px; }")
        right_layout.addWidget(execute_btn)
        
        right_panel.setLayout(right_layout)
        
        # 添加到主布局
        main_layout.addWidget(left_panel)
        main_layout.addWidget(self.node_editor, 1)
        main_layout.addWidget(right_panel)
        
        central_widget.setLayout(main_layout)
    
    def _create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('File')
        
        # 打开图像
        open_action = QAction('Open Image', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self._open_image)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        # 保存管道
        save_pipeline_action = QAction('Save Pipeline', self)
        save_pipeline_action.setShortcut('Ctrl+S')
        save_pipeline_action.triggered.connect(self._save_pipeline)
        file_menu.addAction(save_pipeline_action)
        
        # 加载管道
        load_pipeline_action = QAction('Load Pipeline', self)
        load_pipeline_action.setShortcut('Ctrl+L')
        load_pipeline_action.triggered.connect(self._load_pipeline)
        file_menu.addAction(load_pipeline_action)
        
        file_menu.addSeparator()
        
        # 退出
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 编辑菜单
        edit_menu = menubar.addMenu('Edit')
        
        # 清空管道
        clear_action = QAction('Clear Pipeline', self)
        clear_action.triggered.connect(self._clear_pipeline)
        edit_menu.addAction(clear_action)
        
        # 视图菜单
        view_menu = menubar.addMenu('View')

        # 重置视图
        reset_view_action = QAction('Reset View', self)
        reset_view_action.triggered.connect(self._reset_view)
        view_menu.addAction(reset_view_action)

        # 工具菜单
        tools_menu = menubar.addMenu('Tools')

        # 重新加载自定义算子
        reload_custom_action = QAction('Reload Custom Operators', self)
        reload_custom_action.triggered.connect(self._reload_custom_operators)
        tools_menu.addAction(reload_custom_action)

        # 创建自定义算子模板
        create_template_action = QAction('Create Operator Template', self)
        create_template_action.triggered.connect(self._create_operator_template)
        tools_menu.addAction(create_template_action)
    
    def _create_status_bar(self):
        """创建状态栏"""
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")
    
    def _connect_signals(self):
        """连接信号"""
        # 算子库信号
        self.operator_library.operator_requested.connect(self._create_operator)
        
        # 节点编辑器信号
        self.node_editor.node_selected.connect(self._on_node_selected)
        self.node_editor.connection_created.connect(self._on_connection_created)
        
        # 参数面板信号
        self.parameter_panel.parameter_changed.connect(self._on_parameter_changed)
    
    def _create_operator_factory(self) -> Dict[str, type]:
        """创建算子工厂"""
        factory = {
            'ImageInputOperator': ImageInputOperator,
            'GaussianBlurOperator': GaussianBlurOperator,
            'MedianBlurOperator': MedianBlurOperator,
            'BilateralFilterOperator': BilateralFilterOperator,
            'BoxFilterOperator': BoxFilterOperator,
            'LaplacianOperator': LaplacianOperator,
            'SobelOperator': SobelOperator,
            'CannyOperator': CannyOperator,
            'HoughLinesOperator': HoughLinesOperator,
            'HoughCirclesOperator': HoughCirclesOperator,
            'ContourDetectionOperator': ContourDetectionOperator,
            'ErosionOperator': ErosionOperator,
            'DilationOperator': DilationOperator,
            'OpeningOperator': OpeningOperator,
            'ClosingOperator': ClosingOperator,
            'GradientOperator': GradientOperator,
            'TopHatOperator': TopHatOperator,
            'BlackHatOperator': BlackHatOperator,
            'ThresholdOperator': ThresholdOperator,
        }

        # 添加自定义算子
        custom_operators = self.custom_loader.scan_custom_operators()
        factory.update(custom_operators)

        return factory
    
    def _create_operator(self, class_name: str):
        """创建算子"""
        if class_name in self.operator_factory:
            operator_class = self.operator_factory[class_name]
            operator = operator_class()
            
            # 添加到管道
            self.pipeline.add_operator(operator)
            
            # 添加到节点编辑器
            self.node_editor.add_node(operator)
            
            self.status_bar.showMessage(f"Added {operator.name}")
    
    def _on_node_selected(self, operator: BaseOperator):
        """节点被选中"""
        self.current_operator = operator
        self.parameter_panel.set_operator(operator)
        self.status_bar.showMessage(f"Selected: {operator.name}")
    
    def _on_connection_created(self, source_op, source_port, target_op, target_port):
        """连接被创建"""
        success = self.pipeline.add_connection(
            source_op.id, source_port, target_op.id, target_port
        )
        
        if success:
            # 在节点编辑器中创建可视化连接
            self.node_editor.create_connection(
                source_op.id, source_port, target_op.id, target_port
            )
            self.status_bar.showMessage(f"Connected {source_op.name} to {target_op.name}")
        else:
            self.status_bar.showMessage("Connection failed - would create cycle")
    
    def _on_parameter_changed(self, param_name: str, value):
        """参数改变"""
        if self.current_operator:
            self.status_bar.showMessage(f"Parameter {param_name} changed to {value}")
    
    def _execute_pipeline(self):
        """执行管道"""
        try:
            results = self.pipeline.execute()
            
            # 显示结果
            if results:
                # 找到最后一个有结果的算子
                last_result = None
                for op_id in reversed(self.pipeline.execution_order):
                    if op_id in results and results[op_id]:
                        last_result = results[op_id]
                        break
                
                if last_result and 'image' in last_result:
                    self.single_viewer.set_image(last_result['image'])
                    self.status_bar.showMessage("Pipeline executed successfully")
                else:
                    self.status_bar.showMessage("No image result found")
            else:
                self.status_bar.showMessage("Pipeline execution failed")
                
        except Exception as e:
            QMessageBox.critical(self, "Execution Error", str(e))
            self.status_bar.showMessage(f"Execution failed: {str(e)}")
    
    def _open_image(self):
        """打开图像"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", 
            "Image Files (*.png *.jpg *.jpeg *.bmp *.tiff *.tif)"
        )
        
        if file_path:
            # 查找图像输入算子
            input_operators = [op for op in self.pipeline.operators.values() 
                             if isinstance(op, ImageInputOperator)]
            
            if input_operators:
                # 使用第一个图像输入算子
                input_op = input_operators[0]
                input_op.load_image(file_path)
                self.status_bar.showMessage(f"Loaded image: {os.path.basename(file_path)}")
            else:
                QMessageBox.information(self, "Info", 
                                      "Please add an Image Input operator first")
    
    def _save_pipeline(self):
        """保存管道"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Pipeline", "", "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                self.pipeline.save_pipeline(file_path)
                self.status_bar.showMessage(f"Pipeline saved: {os.path.basename(file_path)}")
            except Exception as e:
                QMessageBox.critical(self, "Save Error", str(e))
    
    def _load_pipeline(self):
        """加载管道"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Pipeline", "", "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                # 这里需要实现管道加载逻辑
                self.status_bar.showMessage("Pipeline loading not implemented yet")
            except Exception as e:
                QMessageBox.critical(self, "Load Error", str(e))
    
    def _clear_pipeline(self):
        """清空管道"""
        reply = QMessageBox.question(self, "Clear Pipeline", 
                                   "Are you sure you want to clear the pipeline?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.pipeline.clear()
            self.node_editor.scene.clear()
            self.node_editor.nodes.clear()
            self.node_editor.connections.clear()
            self.parameter_panel.clear_parameters()
            self.single_viewer.clear_image()
            self.comparison_viewer.clear_images()
            self.status_bar.showMessage("Pipeline cleared")
    
    def _reset_view(self):
        """重置视图"""
        self.node_editor.resetTransform()
        self.node_editor.centerOn(0, 0)

    def _load_custom_operators(self):
        """加载自定义算子"""
        custom_operators = self.custom_loader.scan_custom_operators()
        self.operator_library.add_custom_operators(custom_operators)
        if custom_operators:
            self.status_bar.showMessage(f"Loaded {len(custom_operators)} custom operators")

    def _reload_custom_operators(self):
        """重新加载自定义算子"""
        # 清除现有的自定义算子
        self.operator_library.operator_list.clear()
        self.operator_library._add_operators()

        # 重新创建算子工厂
        self.operator_factory = self._create_operator_factory()

        # 重新加载自定义算子
        self._load_custom_operators()

        self.status_bar.showMessage("Custom operators reloaded")

    def _create_operator_template(self):
        """创建算子模板"""
        operator_name, ok = QInputDialog.getText(
            self, "Create Operator Template",
            "Enter operator name (e.g., MyCustomOperator):"
        )

        if ok and operator_name:
            try:
                filepath = self.custom_loader.create_operator_template(operator_name)
                QMessageBox.information(
                    self, "Template Created",
                    f"Operator template created at:\n{filepath}\n\n"
                    "Edit the file and use 'Tools -> Reload Custom Operators' to load it."
                )
                self.status_bar.showMessage(f"Template created: {operator_name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create template: {e}")
