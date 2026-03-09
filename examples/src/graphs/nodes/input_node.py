"""
输入节点：接收并传递输入文本
"""

from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from graphs.state import InputNodeInput, InputNodeOutput


def input_node(state: InputNodeInput, config: RunnableConfig, runtime: Runtime[Context]) -> InputNodeOutput:
    """
    title: 输入节点
    desc: 接收用户的输入文本并传递给下一个节点
    integrations: 无
    """
    ctx = runtime.context

    # 这里只是简单的传递输入，实际场景中可以做输入验证、预处理等
    # 例如：
    # - 检查输入是否为空
    # - 去除首尾空格
    # - 格式验证等

    cleaned_text = state.input_text.strip() if state.input_text else ""

    return InputNodeOutput(input_text=cleaned_text)
