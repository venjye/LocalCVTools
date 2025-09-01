"""
可视化节点编辑器核心组件
"""
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from typing import Dict, List, Optional, Tuple
import math

from core.operator import BaseOperator
from core.pipeline import Pipeline, Connection


class NodePort(QGraphicsItem):
    """节点端口"""
    
    def __init__(self, name: str, is_input: bool, parent_node):
        super().__init__()
        self.name = name
        self.is_input = is_input
        self.parent_node = parent_node
        self.connections = []
        self.radius = 8
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        
    def boundingRect(self):
        return QRectF(-self.radius, -self.radius, 2*self.radius, 2*self.radius)
    
    def paint(self, painter, option, widget):
        # 绘制端口圆圈
        if self.connections:
            painter.setBrush(QBrush(QColor(100, 200, 100)))
        else:
            painter.setBrush(QBrush(QColor(150, 150, 150)))
        
        painter.setPen(QPen(QColor(50, 50, 50), 2))
        painter.drawEllipse(self.boundingRect())
        
    def add_connection(self, connection):
        """添加连接"""
        if connection not in self.connections:
            self.connections.append(connection)
            self.update()
    
    def remove_connection(self, connection):
        """移除连接"""
        if connection in self.connections:
            self.connections.remove(connection)
            self.update()


class NodeConnection(QGraphicsItem):
    """节点连接线"""
    
    def __init__(self, source_port: NodePort, target_port: NodePort):
        super().__init__()
        self.source_port = source_port
        self.target_port = target_port
        self.setZValue(-1)  # 连接线在节点下方
        
        # 添加到端口的连接列表
        source_port.add_connection(self)
        target_port.add_connection(self)
        
    def boundingRect(self):
        source_pos = self.source_port.scenePos()
        target_pos = self.target_port.scenePos()
        
        return QRectF(
            min(source_pos.x(), target_pos.x()) - 10,
            min(source_pos.y(), target_pos.y()) - 10,
            abs(target_pos.x() - source_pos.x()) + 20,
            abs(target_pos.y() - source_pos.y()) + 20
        )
    
    def paint(self, painter, option, widget):
        source_pos = self.source_port.scenePos()
        target_pos = self.target_port.scenePos()
        
        # 绘制贝塞尔曲线
        path = QPainterPath()
        path.moveTo(source_pos)
        
        # 控制点
        dx = target_pos.x() - source_pos.x()
        control1 = QPointF(source_pos.x() + dx * 0.5, source_pos.y())
        control2 = QPointF(target_pos.x() - dx * 0.5, target_pos.y())
        
        path.cubicTo(control1, control2, target_pos)
        
        painter.setPen(QPen(QColor(100, 100, 100), 3))
        painter.drawPath(path)
    
    def remove(self):
        """移除连接"""
        self.source_port.remove_connection(self)
        self.target_port.remove_connection(self)
        if self.scene():
            self.scene().removeItem(self)


class OperatorNode(QGraphicsItem):
    """算子节点"""
    
    def __init__(self, operator: BaseOperator):
        super().__init__()
        self.operator = operator
        self.width = 150
        self.height = 80
        self.input_ports = {}
        self.output_ports = {}
        
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        
        self._create_ports()
        
    def _create_ports(self):
        """创建端口"""
        # 创建输入端口
        for i, port_name in enumerate(self.operator.input_ports):
            port = NodePort(port_name, True, self)
            port.setParentItem(self)
            y_offset = (i + 1) * self.height / (len(self.operator.input_ports) + 1)
            port.setPos(-port.radius, y_offset - self.height/2)
            self.input_ports[port_name] = port
        
        # 创建输出端口
        for i, port_name in enumerate(self.operator.output_ports):
            port = NodePort(port_name, False, self)
            port.setParentItem(self)
            y_offset = (i + 1) * self.height / (len(self.operator.output_ports) + 1)
            port.setPos(self.width + port.radius, y_offset - self.height/2)
            self.output_ports[port_name] = port
    
    def boundingRect(self):
        return QRectF(0, -self.height/2, self.width, self.height)
    
    def paint(self, painter, option, widget):
        # 绘制节点背景
        rect = self.boundingRect()
        
        if self.isSelected():
            painter.setBrush(QBrush(QColor(100, 150, 200)))
        else:
            painter.setBrush(QBrush(QColor(80, 80, 80)))
        
        painter.setPen(QPen(QColor(50, 50, 50), 2))
        painter.drawRoundedRect(rect, 5, 5)
        
        # 绘制节点标题
        painter.setPen(QPen(QColor(255, 255, 255)))
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        painter.setFont(font)
        
        title_rect = QRectF(5, -self.height/2 + 5, self.width - 10, 20)
        painter.drawText(title_rect, Qt.AlignCenter, self.operator.name)
    
    def itemChange(self, change, value):
        """处理节点位置变化"""
        if change == QGraphicsItem.ItemPositionChange:
            # 更新连接线
            for port in list(self.input_ports.values()) + list(self.output_ports.values()):
                for connection in port.connections:
                    connection.update()
        
        return super().itemChange(change, value)


class NodeEditor(QGraphicsView):
    """节点编辑器视图"""
    
    # 信号
    node_selected = pyqtSignal(object)  # 节点被选中
    connection_created = pyqtSignal(object, str, object, str)  # 连接被创建
    
    def __init__(self):
        super().__init__()
        
        # 创建场景
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        
        # 设置视图属性
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # 节点管理
        self.nodes = {}  # operator_id -> OperatorNode
        self.connections = {}  # connection_id -> NodeConnection
        
        # 连接创建状态
        self.creating_connection = False
        self.connection_start_port = None
        self.temp_connection_line = None
        
        # 背景网格
        self.grid_size = 20
        
    def drawBackground(self, painter, rect):
        """绘制网格背景"""
        painter.setPen(QPen(QColor(60, 60, 60), 1))
        
        # 绘制网格线
        left = int(rect.left()) - (int(rect.left()) % self.grid_size)
        top = int(rect.top()) - (int(rect.top()) % self.grid_size)
        
        lines = []
        for x in range(left, int(rect.right()), self.grid_size):
            lines.append(QLineF(x, rect.top(), x, rect.bottom()))
        for y in range(top, int(rect.bottom()), self.grid_size):
            lines.append(QLineF(rect.left(), y, rect.right(), y))
        
        painter.drawLines(lines)
    
    def add_node(self, operator: BaseOperator, pos: QPointF = None):
        """添加节点"""
        node = OperatorNode(operator)
        if pos:
            node.setPos(pos)
        else:
            # 默认位置
            node.setPos(len(self.nodes) * 200, 0)
        
        self.scene.addItem(node)
        self.nodes[operator.id] = node
        
        return node
    
    def remove_node(self, operator_id: int):
        """移除节点"""
        if operator_id in self.nodes:
            node = self.nodes[operator_id]
            
            # 移除所有相关连接
            all_ports = list(node.input_ports.values()) + list(node.output_ports.values())
            for port in all_ports:
                for connection in port.connections[:]:  # 复制列表避免修改时出错
                    connection.remove()
            
            # 移除节点
            self.scene.removeItem(node)
            del self.nodes[operator_id]
    
    def create_connection(self, source_op_id: int, source_port: str, 
                         target_op_id: int, target_port: str):
        """创建连接"""
        if source_op_id not in self.nodes or target_op_id not in self.nodes:
            return None
        
        source_node = self.nodes[source_op_id]
        target_node = self.nodes[target_op_id]
        
        if source_port not in source_node.output_ports:
            return None
        if target_port not in target_node.input_ports:
            return None
        
        source_port_item = source_node.output_ports[source_port]
        target_port_item = target_node.input_ports[target_port]
        
        # 移除目标端口的现有连接
        for connection in target_port_item.connections[:]:
            connection.remove()
        
        # 创建新连接
        connection = NodeConnection(source_port_item, target_port_item)
        self.scene.addItem(connection)
        
        connection_id = f"{source_op_id}_{source_port}_{target_op_id}_{target_port}"
        self.connections[connection_id] = connection
        
        return connection
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        item = self.itemAt(event.pos())
        
        if isinstance(item, NodePort):
            if event.button() == Qt.LeftButton:
                self._start_connection(item)
                return
        elif isinstance(item, OperatorNode):
            self.node_selected.emit(item.operator)
        
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self.creating_connection and self.temp_connection_line:
            # 更新临时连接线
            scene_pos = self.mapToScene(event.pos())
            line = self.temp_connection_line.line()
            self.temp_connection_line.setLine(line.x1(), line.y1(), 
                                            scene_pos.x(), scene_pos.y())
        
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if self.creating_connection:
            item = self.itemAt(event.pos())
            if isinstance(item, NodePort):
                self._finish_connection(item)
            else:
                self._cancel_connection()
        
        super().mouseReleaseEvent(event)
    
    def _start_connection(self, port: NodePort):
        """开始创建连接"""
        if port.is_input:
            return  # 只能从输出端口开始连接
        
        self.creating_connection = True
        self.connection_start_port = port
        
        # 创建临时连接线
        start_pos = port.scenePos()
        self.temp_connection_line = QGraphicsLineItem(start_pos.x(), start_pos.y(), 
                                                     start_pos.x(), start_pos.y())
        self.temp_connection_line.setPen(QPen(QColor(100, 100, 100), 2, Qt.DashLine))
        self.scene.addItem(self.temp_connection_line)
    
    def _finish_connection(self, target_port: NodePort):
        """完成连接创建"""
        if (target_port.is_input and 
            self.connection_start_port and 
            not self.connection_start_port.is_input and
            target_port.parent_node != self.connection_start_port.parent_node):
            
            # 发射连接创建信号
            self.connection_created.emit(
                self.connection_start_port.parent_node.operator,
                self.connection_start_port.name,
                target_port.parent_node.operator,
                target_port.name
            )
        
        self._cancel_connection()
    
    def _cancel_connection(self):
        """取消连接创建"""
        self.creating_connection = False
        self.connection_start_port = None
        
        if self.temp_connection_line:
            self.scene.removeItem(self.temp_connection_line)
            self.temp_connection_line = None
    
    def wheelEvent(self, event):
        """鼠标滚轮缩放"""
        factor = 1.2
        if event.angleDelta().y() < 0:
            factor = 1.0 / factor
        
        self.scale(factor, factor)
