from typing import Any, Dict, List, Literal

from pydantic import BaseModel, ConfigDict, Field


class RuntimeSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    env: str = Field(default="local")
    profile: str = Field(default="local")
    workspace_path: str = Field(default="")


class HttpSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    host: str = Field(default="0.0.0.0")
    port: int = Field(default=5000)
    reload: bool = Field(default=False)
    workers: int = Field(default=1)


class WorkflowSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    timeout_seconds: int = Field(default=900)
    default_input_text: str = Field(default="你好")


class LoggingSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    level: str = Field(default="INFO")
    json_format: bool = Field(default=True)
    log_file: str = Field(default="")
    max_bytes: int = Field(default=100 * 1024 * 1024)
    backup_count: int = Field(default=5)
    console_output: bool = Field(default=True)


class DatabaseSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    url: str = Field(default="")
    pool_size: int = Field(default=20)
    max_overflow: int = Field(default=20)
    pool_timeout: int = Field(default=30)
    pool_recycle: int = Field(default=1800)


class CheckpointSettings(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    backend: Literal["postgres", "memory"] = Field(default="postgres")
    fallback_enabled: bool = Field(default=True)
    schema_name: str = Field(default="memory", alias="schema")
    connection_timeout: int = Field(default=15)
    max_retries: int = Field(default=2)


class StorageSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    s3_bucket: str = Field(default="")
    s3_region: str = Field(default="")
    s3_endpoint_url: str = Field(default="")
    s3_prefix: str = Field(default="workflows/")


class ProjectSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    runtime: RuntimeSettings = Field(default_factory=RuntimeSettings)
    http: HttpSettings = Field(default_factory=HttpSettings)
    workflow: WorkflowSettings = Field(default_factory=WorkflowSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    checkpoint: CheckpointSettings = Field(default_factory=CheckpointSettings)
    storage: StorageSettings = Field(default_factory=StorageSettings)


class LLMRuntimeConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model: str = Field(..., description="大模型名称")
    temperature: float = Field(default=0.7)
    top_p: float = Field(default=0.7)
    max_completion_tokens: int = Field(default=2000)
    thinking: str = Field(default="disabled")
    timeout_seconds: int = Field(default=60)
    retry_count: int = Field(default=2)
    fallback_model: str = Field(default="")


class LLMNodeConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    config: LLMRuntimeConfig = Field(...)
    tools: List[Dict[str, Any]] = Field(default_factory=list)
    sp: str = Field(default="")
    up: str = Field(default="")


class GraphNodeConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(...)
    type: Literal["task", "agent", "condition", "looparray", "loopcond"] = Field(...)
    llm_cfg: str = Field(default="")

    def to_metadata(self) -> Dict[str, str]:
        metadata: Dict[str, str] = {"type": self.type}
        if self.llm_cfg:
            metadata["llm_cfg"] = self.llm_cfg
        return metadata


class GraphEdgeConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: str = Field(...)
    target: str = Field(...)


class GraphDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(default="main_graph")
    entry_point: str = Field(...)
    nodes: List[GraphNodeConfig] = Field(default_factory=list)
    edges: List[GraphEdgeConfig] = Field(default_factory=list)

    def get_node(self, name: str) -> GraphNodeConfig:
        for node in self.nodes:
            if node.name == name:
                return node
        raise ValueError(f"图配置中未找到节点: {name}")
