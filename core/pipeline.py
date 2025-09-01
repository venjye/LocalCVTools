"""
图像处理管道系统
"""
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
from core.operator import BaseOperator


class Connection:
    """连接类，表示算子之间的连接"""
    
    def __init__(self, source_op: BaseOperator, source_port: str, 
                 target_op: BaseOperator, target_port: str):
        self.source_op = source_op
        self.source_port = source_port
        self.target_op = target_op
        self.target_port = target_port

    def __str__(self):
        return f"{self.source_op.name}[{self.source_port}] -> {self.target_op.name}[{self.target_port}]"


class Pipeline:
    """图像处理管道"""
    
    def __init__(self):
        self.operators: Dict[int, BaseOperator] = {}  # 算子字典，key为算子id
        self.connections: List[Connection] = []  # 连接列表
        self.execution_order: List[int] = []  # 执行顺序
        self.results_cache: Dict[int, Dict[str, np.ndarray]] = {}  # 结果缓存

    def add_operator(self, operator: BaseOperator) -> int:
        """添加算子到管道"""
        self.operators[operator.id] = operator
        self._update_execution_order()
        return operator.id

    def remove_operator(self, operator_id: int):
        """从管道中移除算子"""
        if operator_id in self.operators:
            # 移除相关连接
            self.connections = [conn for conn in self.connections 
                              if conn.source_op.id != operator_id and conn.target_op.id != operator_id]
            # 移除算子
            del self.operators[operator_id]
            # 清除缓存
            if operator_id in self.results_cache:
                del self.results_cache[operator_id]
            # 更新执行顺序
            self._update_execution_order()

    def add_connection(self, source_op_id: int, source_port: str, 
                      target_op_id: int, target_port: str) -> bool:
        """添加连接"""
        if source_op_id not in self.operators or target_op_id not in self.operators:
            return False
        
        source_op = self.operators[source_op_id]
        target_op = self.operators[target_op_id]
        
        # 检查端口是否存在
        if source_port not in source_op.output_ports:
            return False
        if target_port not in target_op.input_ports:
            return False
        
        # 检查是否已存在相同的连接
        for conn in self.connections:
            if (conn.target_op.id == target_op_id and 
                conn.target_port == target_port):
                # 目标端口已被占用，移除旧连接
                self.connections.remove(conn)
                break
        
        # 添加新连接
        connection = Connection(source_op, source_port, target_op, target_port)
        self.connections.append(connection)
        
        # 检查是否形成循环
        if self._has_cycle():
            self.connections.remove(connection)
            return False
        
        # 更新执行顺序
        self._update_execution_order()
        return True

    def remove_connection(self, source_op_id: int, source_port: str, 
                         target_op_id: int, target_port: str):
        """移除连接"""
        self.connections = [conn for conn in self.connections 
                          if not (conn.source_op.id == source_op_id and 
                                conn.source_port == source_port and
                                conn.target_op.id == target_op_id and 
                                conn.target_port == target_port)]
        self._update_execution_order()

    def _has_cycle(self) -> bool:
        """检查是否存在循环依赖"""
        # 使用DFS检测循环
        visited = set()
        rec_stack = set()
        
        def dfs(op_id: int) -> bool:
            visited.add(op_id)
            rec_stack.add(op_id)
            
            # 查找所有从当前算子出发的连接
            for conn in self.connections:
                if conn.source_op.id == op_id:
                    target_id = conn.target_op.id
                    if target_id not in visited:
                        if dfs(target_id):
                            return True
                    elif target_id in rec_stack:
                        return True
            
            rec_stack.remove(op_id)
            return False
        
        for op_id in self.operators:
            if op_id not in visited:
                if dfs(op_id):
                    return True
        return False

    def _update_execution_order(self):
        """更新执行顺序（拓扑排序）"""
        # 计算每个算子的入度
        in_degree = {op_id: 0 for op_id in self.operators}
        for conn in self.connections:
            in_degree[conn.target_op.id] += 1
        
        # 拓扑排序
        queue = [op_id for op_id, degree in in_degree.items() if degree == 0]
        execution_order = []
        
        while queue:
            current = queue.pop(0)
            execution_order.append(current)
            
            # 减少后继节点的入度
            for conn in self.connections:
                if conn.source_op.id == current:
                    target_id = conn.target_op.id
                    in_degree[target_id] -= 1
                    if in_degree[target_id] == 0:
                        queue.append(target_id)
        
        self.execution_order = execution_order

    def execute(self, force_refresh: bool = False) -> Dict[int, Dict[str, np.ndarray]]:
        """执行管道"""
        if force_refresh:
            self.results_cache.clear()
            # 清除所有算子的缓存
            for operator in self.operators.values():
                operator.cached_result = None
                operator.inputs_hash = None
        
        results = {}
        
        for op_id in self.execution_order:
            operator = self.operators[op_id]
            
            # 准备输入数据
            inputs = {}
            for conn in self.connections:
                if conn.target_op.id == op_id:
                    source_result = results.get(conn.source_op.id)
                    if source_result and conn.source_port in source_result:
                        inputs[conn.target_port] = source_result[conn.source_port]
            
            # 对于没有输入连接的算子（如图像输入算子），使用空输入
            if not inputs and operator.input_ports:
                # 跳过没有输入的算子
                continue
            
            try:
                # 执行算子
                result = operator.execute(inputs)
                results[op_id] = result
                self.results_cache[op_id] = result
            except Exception as e:
                print(f"Error executing operator {operator.name}: {e}")
                results[op_id] = {}
        
        return results

    def get_operator_result(self, operator_id: int) -> Optional[Dict[str, np.ndarray]]:
        """获取指定算子的结果"""
        return self.results_cache.get(operator_id)

    def get_operator_by_id(self, operator_id: int) -> Optional[BaseOperator]:
        """根据ID获取算子"""
        return self.operators.get(operator_id)

    def get_connections_for_operator(self, operator_id: int) -> Tuple[List[Connection], List[Connection]]:
        """获取指定算子的输入和输出连接"""
        input_connections = [conn for conn in self.connections if conn.target_op.id == operator_id]
        output_connections = [conn for conn in self.connections if conn.source_op.id == operator_id]
        return input_connections, output_connections

    def clear(self):
        """清空管道"""
        self.operators.clear()
        self.connections.clear()
        self.execution_order.clear()
        self.results_cache.clear()

    def get_pipeline_info(self) -> Dict[str, Any]:
        """获取管道信息"""
        return {
            'operators': [op.get_info() for op in self.operators.values()],
            'connections': [str(conn) for conn in self.connections],
            'execution_order': [self.operators[op_id].name for op_id in self.execution_order]
        }

    def save_pipeline(self, filepath: str):
        """保存管道配置到文件"""
        import json
        
        pipeline_data = {
            'operators': [],
            'connections': []
        }
        
        # 保存算子信息
        for operator in self.operators.values():
            op_data = {
                'id': operator.id,
                'name': operator.name,
                'class_name': operator.__class__.__name__,
                'parameters': operator.get_parameters_dict()
            }
            pipeline_data['operators'].append(op_data)
        
        # 保存连接信息
        for conn in self.connections:
            conn_data = {
                'source_op_id': conn.source_op.id,
                'source_port': conn.source_port,
                'target_op_id': conn.target_op.id,
                'target_port': conn.target_port
            }
            pipeline_data['connections'].append(conn_data)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(pipeline_data, f, indent=2, ensure_ascii=False)

    def load_pipeline(self, filepath: str):
        """从文件加载管道配置"""
        import json
        
        with open(filepath, 'r', encoding='utf-8') as f:
            pipeline_data = json.load(f)
        
        # 清空当前管道
        self.clear()
        
        # 这里需要一个算子工厂来根据类名创建算子实例
        # 暂时留空，在主程序中实现
        pass
