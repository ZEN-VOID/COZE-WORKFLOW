"""
处理节点：使用 LLM 处理文本（Agent 节点示例）
"""

import os
import json
from jinja2 import Template
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from coze_coding_dev_sdk import LLMClient
from graphs.state import ProcessNodeInput, ProcessNodeOutput


def process_node(state: ProcessNodeInput, config: RunnableConfig, runtime: Runtime[Context]) -> ProcessNodeOutput:
    """
    title: 文本处理节点
    desc: 使用大语言模型处理输入文本，生成处理结果
    integrations: 大语言模型
    """
    ctx = runtime.context

    # 从配置文件读取 LLM 配置
    config_file = config.get('metadata', {}).get('llm_cfg', '')
    if not config_file:
        raise ValueError("未找到 LLM 配置文件路径")

    # 构建配置文件的完整路径
    workspace_path = os.getenv('COZE_WORKSPACE_PATH', '')
    cfg_path = os.path.join(workspace_path, config_file)

    # 读取配置文件
    with open(cfg_path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)

    # 提取配置
    llm_config = cfg.get('config', {})
    system_prompt = cfg.get('sp', '')
    user_prompt_template = cfg.get('up', '')

    # 使用 Jinja2 模板渲染用户提示词
    template = Template(user_prompt_template)
    user_prompt = template.render({'input_text': state.input_text})

    # 初始化 LLM 客户端
    client = LLMClient(ctx=ctx)

    # 构建消息列表
    messages = [
        HumanMessage(content=user_prompt)
    ]

    # 调用 LLM
    response = client.invoke(
        messages=messages,
        model=llm_config.get('model', 'doubao-seed-1-8-251228'),
        temperature=llm_config.get('temperature', 0.7),
        top_p=llm_config.get('top_p', 0.7),
        max_completion_tokens=llm_config.get('max_completion_tokens', 2000),
        thinking=llm_config.get('thinking', 'disabled')
    )

    # 处理响应（response.content 可能是 str 或 list）
    if isinstance(response.content, str):
        processed_text = response.content
    elif isinstance(response.content, list):
        # 处理列表类型的响应
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
