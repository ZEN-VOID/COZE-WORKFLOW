"""
道具全链路编排智能体节点
功能：A道具整合研究 -> B主体提示词 -> C道具面板合同
"""

import os
import json
from typing import Dict, Any
from jinja2 import Template
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from coze_coding_dev_sdk import LLMClient

from graphs.state import PropOrchestratorInput, PropOrchestratorOutput


def prop_orchestrator_node(
    state: PropOrchestratorInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> PropOrchestratorOutput:
    """
    title: 道具全链路编排
    desc: 执行道具三阶段设计：A阶段道具整合研究、B阶段主体提示词设计、C阶段道具面板编排
    integrations: 大语言模型
    """
    ctx = runtime.context
    
    # 读取配置文件
    cfg_file = os.path.join(
        os.getenv("COZE_WORKSPACE_PATH", ""),
        "config/prop_orchestrator_llm_cfg.json"
    )
    
    try:
        with open(cfg_file, 'r', encoding='utf-8') as fd:
            _cfg = json.load(fd)
    except Exception as e:
        return PropOrchestratorOutput(
            prop_design="",
            status="FAIL",
            message=f"配置文件加载失败: {str(e)}"
        )
    
    llm_config = _cfg.get("config", {})
    sp = _cfg.get("sp", "")
    up = _cfg.get("up", "")
    
    # 渲染用户提示词
    up_tpl = Template(up)
    user_prompt = up_tpl.render({
        "project_name": state.project_name,
        "episode_no": state.episode_no,
        "storyboard_payload": state.video_script,
        "global_style": state.global_style_prompt
    })
    
    # 构建消息
    messages = [
        SystemMessage(content=sp),
        HumanMessage(content=user_prompt)
    ]
    
    # 调用大模型
    try:
        client = LLMClient(ctx=ctx)
        response = client.invoke(
            messages=messages,
            model=llm_config.get("model", "doubao-seed-2-0-pro-260215"),
            temperature=llm_config.get("temperature", 0.4),
            top_p=llm_config.get("top_p", 0.9),
            max_completion_tokens=llm_config.get("max_completion_tokens", 32768)
        )
        
        # 处理响应内容
        content = response.content
        if isinstance(content, list):
            text_parts = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text_parts.append(item.get("text", ""))
                elif isinstance(item, str):
                    text_parts.append(item)
            final_markdown = "\n".join(text_parts)
        else:
            final_markdown = str(content) if content else ""
        
        return PropOrchestratorOutput(
            prop_design=final_markdown,
            status="PASS",
            message="道具设计完成"
        )
        
    except Exception as e:
        return PropOrchestratorOutput(
            prop_design="",
            status="FAIL",
            message=f"大模型调用失败: {str(e)}"
        )
