"""
处理节点：使用 LLM 处理文本（Agent 节点示例）
"""

from jinja2 import Template
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_dev_sdk import LLMClient
from coze_coding_utils.runtime_ctx.context import Context

from config.settings import load_llm_node_config
from graphs.state import ProcessNodeInput, ProcessNodeOutput


def process_node(state: ProcessNodeInput, config: RunnableConfig, runtime: Runtime[Context]) -> ProcessNodeOutput:
    """
    title: 文本处理节点
    desc: 使用大语言模型处理输入文本，生成处理结果
    integrations: 大语言模型
    """
    ctx = runtime.context

    config_file = config.get('metadata', {}).get('llm_cfg', '')
    if not config_file:
        raise ValueError("未找到 LLM 配置文件路径")

    llm_settings = load_llm_node_config(config_file)
    llm_config = llm_settings.config

    template = Template(llm_settings.up)
    user_prompt = template.render(state.model_dump())

    client = LLMClient(ctx=ctx)

    messages = []
    if llm_settings.sp:
        messages.append(SystemMessage(content=llm_settings.sp))
    messages.append(HumanMessage(content=user_prompt))

    response = client.invoke(
        messages=messages,
        model=llm_config.model,
        temperature=llm_config.temperature,
        top_p=llm_config.top_p,
        max_completion_tokens=llm_config.max_completion_tokens,
        thinking=llm_config.thinking
    )

    if isinstance(response.content, str):
        processed_text = response.content
    elif isinstance(response.content, list):
        text_parts = []
        for item in response.content:
            if isinstance(item, str):
                text_parts.append(item)
            elif isinstance(item, dict) and item.get('type') == 'text':
                text_parts.append(item.get('text', ''))
        processed_text = ' '.join(text_parts)
    else:
        processed_text = str(response.content)

    return ProcessNodeOutput(processed_text=processed_text)
