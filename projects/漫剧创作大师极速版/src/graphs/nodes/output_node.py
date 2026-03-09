"""
输出节点：格式化并输出最终结果
"""

from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from graphs.state import OutputNodeInput, OutputNodeOutput


def output_node(state: OutputNodeInput, config: RunnableConfig, runtime: Runtime[Context]) -> OutputNodeOutput:
    """
    title: 输出节点
    desc: 格式化处理结果并输出
    integrations: 无
    """
    ctx = runtime.context

    # 这里可以对结果进行格式化、添加元数据等操作
    # 例如：
    # - 添加时间戳
    # - 格式化为特定格式（JSON、Markdown 等）
    # - 添加处理状态标记等

    result = state.processed_text

    # 简单的格式化示例
    formatted_result = f"处理结果：\n{result}"

    return OutputNodeOutput(result=formatted_result)
