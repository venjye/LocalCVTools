"""
参数面板组件
"""
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from typing import Dict, Any, Callable
from core.operator import BaseOperator, Parameter


class ParameterWidget(QWidget):
    """单个参数的控件"""
    
    value_changed = pyqtSignal(str, object)  # 参数名, 新值
    
    def __init__(self, parameter: Parameter):
        super().__init__()
        self.parameter = parameter
        self.control_widget = None
        self._create_widget()
    
    def _create_widget(self):
        """根据参数类型创建对应的控件"""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 参数名标签
        label = QLabel(self.parameter.name + ":")
        label.setMinimumWidth(80)
        layout.addWidget(label)
        
        # 根据参数类型创建控件
        if self.parameter.param_type == bool:
            self.control_widget = QCheckBox()
            self.control_widget.setChecked(self.parameter.current_value)
            self.control_widget.stateChanged.connect(self._on_bool_changed)
        
        elif self.parameter.param_type == int:
            if self.parameter.min_value is not None and self.parameter.max_value is not None:
                # 使用滑块
                widget_container = QWidget()
                widget_layout = QHBoxLayout()
                widget_layout.setContentsMargins(0, 0, 0, 0)
                
                self.control_widget = QSlider(Qt.Horizontal)
                self.control_widget.setMinimum(self.parameter.min_value)
                self.control_widget.setMaximum(self.parameter.max_value)
                self.control_widget.setValue(self.parameter.current_value)
                self.control_widget.valueChanged.connect(self._on_int_changed)
                
                self.value_label = QLabel(str(self.parameter.current_value))
                self.value_label.setMinimumWidth(40)
                
                widget_layout.addWidget(self.control_widget)
                widget_layout.addWidget(self.value_label)
                widget_container.setLayout(widget_layout)
                
                layout.addWidget(widget_container)
            else:
                # 使用数字输入框
                self.control_widget = QSpinBox()
                if self.parameter.min_value is not None:
                    self.control_widget.setMinimum(self.parameter.min_value)
                else:
                    self.control_widget.setMinimum(-999999)
                if self.parameter.max_value is not None:
                    self.control_widget.setMaximum(self.parameter.max_value)
                else:
                    self.control_widget.setMaximum(999999)
                self.control_widget.setValue(self.parameter.current_value)
                self.control_widget.valueChanged.connect(self._on_int_changed)
                layout.addWidget(self.control_widget)
        
        elif self.parameter.param_type == float:
            if self.parameter.min_value is not None and self.parameter.max_value is not None:
                # 使用滑块 + 数字输入框组合
                widget_container = QWidget()
                widget_layout = QHBoxLayout()
                widget_layout.setContentsMargins(0, 0, 0, 0)
                
                # 滑块（放大100倍处理小数）
                self.control_widget = QSlider(Qt.Horizontal)
                self.control_widget.setMinimum(int(self.parameter.min_value * 100))
                self.control_widget.setMaximum(int(self.parameter.max_value * 100))
                self.control_widget.setValue(int(self.parameter.current_value * 100))
                self.control_widget.valueChanged.connect(self._on_float_slider_changed)
                
                # 数字输入框
                self.spin_box = QDoubleSpinBox()
                self.spin_box.setMinimum(self.parameter.min_value)
                self.spin_box.setMaximum(self.parameter.max_value)
                self.spin_box.setValue(self.parameter.current_value)
                self.spin_box.setSingleStep(0.1)
                self.spin_box.setDecimals(2)
                self.spin_box.valueChanged.connect(self._on_float_spin_changed)
                
                widget_layout.addWidget(self.control_widget, 2)
                widget_layout.addWidget(self.spin_box, 1)
                widget_container.setLayout(widget_layout)
                
                layout.addWidget(widget_container)
            else:
                # 只使用数字输入框
                self.control_widget = QDoubleSpinBox()
                if self.parameter.min_value is not None:
                    self.control_widget.setMinimum(self.parameter.min_value)
                else:
                    self.control_widget.setMinimum(-999999.0)
                if self.parameter.max_value is not None:
                    self.control_widget.setMaximum(self.parameter.max_value)
                else:
                    self.control_widget.setMaximum(999999.0)
                self.control_widget.setValue(self.parameter.current_value)
                self.control_widget.setSingleStep(0.1)
                self.control_widget.setDecimals(2)
                self.control_widget.valueChanged.connect(self._on_float_changed)
                layout.addWidget(self.control_widget)
        
        elif self.parameter.param_type == str:
            if self.parameter.options:
                # 使用下拉框
                self.control_widget = QComboBox()
                self.control_widget.addItems(self.parameter.options)
                self.control_widget.setCurrentText(self.parameter.current_value)
                self.control_widget.currentTextChanged.connect(self._on_string_changed)
            else:
                # 使用文本输入框
                self.control_widget = QLineEdit()
                self.control_widget.setText(self.parameter.current_value)
                self.control_widget.textChanged.connect(self._on_string_changed)
            layout.addWidget(self.control_widget)
        
        # 添加描述工具提示
        if self.parameter.description:
            label.setToolTip(self.parameter.description)
            if hasattr(self.control_widget, 'setToolTip'):
                self.control_widget.setToolTip(self.parameter.description)
        
        self.setLayout(layout)
    
    def _on_bool_changed(self, state):
        """布尔值改变"""
        value = state == Qt.Checked
        self.value_changed.emit(self.parameter.name, value)
    
    def _on_int_changed(self, value):
        """整数值改变"""
        if hasattr(self, 'value_label'):
            self.value_label.setText(str(value))
        self.value_changed.emit(self.parameter.name, value)
    
    def _on_float_changed(self, value):
        """浮点数值改变"""
        self.value_changed.emit(self.parameter.name, value)
    
    def _on_float_slider_changed(self, value):
        """浮点数滑块改变"""
        float_value = value / 100.0
        if hasattr(self, 'spin_box'):
            self.spin_box.blockSignals(True)
            self.spin_box.setValue(float_value)
            self.spin_box.blockSignals(False)
        self.value_changed.emit(self.parameter.name, float_value)
    
    def _on_float_spin_changed(self, value):
        """浮点数输入框改变"""
        if hasattr(self, 'control_widget'):
            self.control_widget.blockSignals(True)
            self.control_widget.setValue(int(value * 100))
            self.control_widget.blockSignals(False)
        self.value_changed.emit(self.parameter.name, value)
    
    def _on_string_changed(self, value):
        """字符串值改变"""
        self.value_changed.emit(self.parameter.name, value)
    
    def update_value(self, value):
        """更新控件显示的值"""
        if self.parameter.param_type == bool and isinstance(self.control_widget, QCheckBox):
            self.control_widget.blockSignals(True)
            self.control_widget.setChecked(value)
            self.control_widget.blockSignals(False)
        elif self.parameter.param_type == int:
            if isinstance(self.control_widget, QSlider):
                self.control_widget.blockSignals(True)
                self.control_widget.setValue(value)
                self.control_widget.blockSignals(False)
                if hasattr(self, 'value_label'):
                    self.value_label.setText(str(value))
            elif isinstance(self.control_widget, QSpinBox):
                self.control_widget.blockSignals(True)
                self.control_widget.setValue(value)
                self.control_widget.blockSignals(False)
        elif self.parameter.param_type == float:
            if isinstance(self.control_widget, QSlider):
                self.control_widget.blockSignals(True)
                self.control_widget.setValue(int(value * 100))
                self.control_widget.blockSignals(False)
                if hasattr(self, 'spin_box'):
                    self.spin_box.blockSignals(True)
                    self.spin_box.setValue(value)
                    self.spin_box.blockSignals(False)
            elif isinstance(self.control_widget, QDoubleSpinBox):
                self.control_widget.blockSignals(True)
                self.control_widget.setValue(value)
                self.control_widget.blockSignals(False)
        elif self.parameter.param_type == str:
            if isinstance(self.control_widget, QComboBox):
                self.control_widget.blockSignals(True)
                self.control_widget.setCurrentText(str(value))
                self.control_widget.blockSignals(False)
            elif isinstance(self.control_widget, QLineEdit):
                self.control_widget.blockSignals(True)
                self.control_widget.setText(str(value))
                self.control_widget.blockSignals(False)


class ParameterPanel(QWidget):
    """参数面板"""
    
    parameter_changed = pyqtSignal(str, object)  # 参数名, 新值
    
    def __init__(self):
        super().__init__()
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # 参数容器
        self.parameter_container = QWidget()
        self.parameter_layout = QVBoxLayout()
        self.parameter_layout.setAlignment(Qt.AlignTop)
        self.parameter_container.setLayout(self.parameter_layout)
        
        scroll_area.setWidget(self.parameter_container)
        
        # 主布局
        main_layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel("Parameters")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        main_layout.addWidget(title_label)
        
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)
        
        # 当前算子和参数控件
        self.current_operator = None
        self.parameter_widgets = {}
    
    def set_operator(self, operator: BaseOperator):
        """设置当前算子"""
        self.current_operator = operator
        self._update_parameters()
    
    def clear_parameters(self):
        """清除所有参数"""
        self.current_operator = None
        self._clear_parameter_widgets()
    
    def _clear_parameter_widgets(self):
        """清除参数控件"""
        for widget in self.parameter_widgets.values():
            widget.setParent(None)
            widget.deleteLater()
        self.parameter_widgets.clear()
    
    def _update_parameters(self):
        """更新参数显示"""
        self._clear_parameter_widgets()
        
        if not self.current_operator:
            return
        
        # 为每个参数创建控件
        for param_name, parameter in self.current_operator.parameters.items():
            param_widget = ParameterWidget(parameter)
            param_widget.value_changed.connect(self._on_parameter_changed)
            
            self.parameter_layout.addWidget(param_widget)
            self.parameter_widgets[param_name] = param_widget
        
        # 添加弹性空间
        self.parameter_layout.addStretch()
    
    def _on_parameter_changed(self, param_name: str, value):
        """参数值改变"""
        if self.current_operator:
            self.current_operator.set_parameter(param_name, value)
            self.parameter_changed.emit(param_name, value)
    
    def update_parameter_value(self, param_name: str, value):
        """更新参数值显示"""
        if param_name in self.parameter_widgets:
            self.parameter_widgets[param_name].update_value(value)
