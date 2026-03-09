"""
主图编排文件
定义工作流的整体结构和节点连接关系
"""

from langgraph.graph import END, StateGraph

from config.settings import load_graph_definition
from graphs.nodes.input_node import input_node
from graphs.nodes.output_node import output_node
from graphs.nodes.process_node import process_node
from graphs.state import GlobalState, GraphInput, GraphOutput

graph_definition = load_graph_definition()
node_map = {node.name: node for node in graph_definition.nodes}

builder = StateGraph(GlobalState, input_schema=GraphInput, output_schema=GraphOutput)

builder.add_node("input_node", input_node, metadata=node_map["input_node"].to_metadata())
builder.add_node("process_node", process_node, metadata=node_map["process_node"].to_metadata())
builder.add_node("output_node", output_node, metadata=node_map["output_node"].to_metadata())

builder.set_entry_point(graph_definition.entry_point)

for edge in graph_definition.edges:
    target = END if edge.target == "END" else edge.target
    builder.add_edge(edge.source, target)


# ============================================================================
# 条件分支示例（可选）
# ============================================================================
# 如果需要条件分支，可以这样定义：
#
# def should_process(state: CheckErrorInput) -> str:
#     """根据错误信息决定流程走向"""
#     if state.error_message:
#         return "输出错误"
#     else:
#         return "继续处理"
#
# builder.add_conditional_edges(
#     source="input_node",           # 源节点名称（字符串）
#     path=should_process,           # 路径决策函数（函数对象）
#     path_map={
#         "输出错误": "error_handler", # 分支名称 -> 目标节点名称
#         "继续处理": "process_node"
#     }
# )


# ============================================================================
# 并行执行示例（可选）
# ============================================================================
# 如果需要并行执行多个节点，可以这样定义：
#
# builder.add_edge("input_node", "parallel_node1")
# builder.add_edge("input_node", "parallel_node2")
# # 两个并行分支汇聚到 merge_node
# builder.add_edge(["parallel_node1", "parallel_node2"], "merge_node")


# ============================================================================
# 循环示例（可选）
# ============================================================================
# 如果需要循环处理，必须使用子图实现：
# 1. 在 loop_graph.py 中定义子图
# 2. 在主图中添加一个普通节点调用子图
# 3. 添加 metadata 标记为循环类型
#
# builder.add_node(
#     "loop_process",
#     loop_process_node,
#     metadata={"type": "looparray"}  # 或 "loopcond"
# )


# ============================================================================
# 编译图
# ============================================================================
main_graph = builder.compile()
