"""
工作流状态定义文件
定义全局状态、图输入输出、以及各节点的输入输出类型
"""

from typing import Optional
from pydantic import BaseModel, Field


# ============================================================================
# 全局状态定义 (Global State)
# ============================================================================
class GlobalState(BaseModel):
    """全局状态：用于在节点间共享的数据"""
    input_text: str = Field(default="", description="输入的原始文本")
    processed_text: str = Field(default="", description="经过处理后的文本")
    result: str = Field(default="", description="最终结果")
    error_message: str = Field(default="", description="错误信息")


# ============================================================================
# 工作流输入输出定义
# ============================================================================
class GraphInput(BaseModel):
    """工作流输入"""
    input_text: str = Field(..., description="待处理的输入文本")


class GraphOutput(BaseModel):
    """工作流输出"""
    result: str = Field(..., description="处理后的最终结果")
    error_message: str = Field(default="", description="错误信息（如果有）")


# ============================================================================
# 节点输入输出定义（每个节点独立的类型定义）
# ============================================================================

# --- InputNode：输入节点 ---
class InputNodeInput(BaseModel):
    """输入节点的输入"""
    input_text: str = Field(..., description="输入的原始文本")


class InputNodeOutput(BaseModel):
    """输入节点的输出"""
    input_text: str = Field(..., description="输入的原始文本")


# --- ProcessNode：处理节点（Agent 节点）---
class ProcessNodeInput(BaseModel):
    """处理节点的输入"""
    input_text: str = Field(..., description="需要处理的文本")


class ProcessNodeOutput(BaseModel):
    """处理节点的输出"""
    processed_text: str = Field(..., description="LLM 处理后的文本")


# --- OutputNode：输出节点 ---
class OutputNodeInput(BaseModel):
    """输出节点的输入"""
    processed_text: str = Field(..., description="处理后的文本")


class OutputNodeOutput(BaseModel):
    """输出节点的输出"""
    result: str = Field(..., description="最终结果")


# ============================================================================
# 条件判断节点输入输出定义
# ============================================================================

# --- CheckErrorNode：错误检查条件节点 ---
class CheckErrorInput(BaseModel):
    """错误检查节点的输入"""
    error_message: str = Field(default="", description="错误信息")


# ============================================================================
# 循环节点输入输出定义（如果需要）
# ============================================================================

# --- LoopItemProcessNode：循环节点处理项 ---
class LoopItemProcessInput(BaseModel):
    """循环节点处理项的输入"""
    item: str = Field(..., description="当前处理项")


class LoopItemProcessOutput(BaseModel):
    """循环节点处理项的输出"""
    processed_item: str = Field(..., description="处理后的项")
