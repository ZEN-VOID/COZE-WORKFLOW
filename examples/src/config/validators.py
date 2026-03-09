from dataclasses import dataclass
from typing import List

from pydantic import ValidationError

from config.loader import resolve_workspace_path
from config.settings import get_settings, load_graph_definition, load_llm_node_config


@dataclass(frozen=True)
class ValidationIssue:
    severity: str
    location: str
    message: str


def validate_project_configuration() -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []

    try:
        settings = get_settings(force_reload=True)
    except ValidationError as exc:
        issues.append(ValidationIssue("error", "settings", str(exc)))
        return issues

    graph_definition = load_graph_definition()
    node_names = {node.name for node in graph_definition.nodes}
    if graph_definition.entry_point not in node_names:
        issues.append(ValidationIssue("error", "graph.entry_point", f"入口节点不存在: {graph_definition.entry_point}"))

    if len(node_names) != len(graph_definition.nodes):
        issues.append(ValidationIssue("error", "graph.nodes", "节点名称存在重复"))

    for edge in graph_definition.edges:
        if edge.source not in node_names:
            issues.append(ValidationIssue("error", "graph.edges", f"边的 source 不存在: {edge.source}"))
        if edge.target != "END" and edge.target not in node_names:
            issues.append(ValidationIssue("error", "graph.edges", f"边的 target 不存在: {edge.target}"))

    for node in graph_definition.nodes:
        if node.type == "agent":
            if not node.llm_cfg:
                issues.append(ValidationIssue("error", f"graph.nodes.{node.name}", "Agent 节点缺少 llm_cfg"))
                continue
            llm_path = resolve_workspace_path(node.llm_cfg)
            if not llm_path.exists():
                issues.append(ValidationIssue("error", f"graph.nodes.{node.name}", f"LLM 配置文件不存在: {llm_path}"))
                continue
            try:
                llm_config = load_llm_node_config(node.llm_cfg)
                if not llm_config.sp.strip():
                    issues.append(ValidationIssue("warning", f"graph.nodes.{node.name}", "系统提示词为空"))
                if not llm_config.up.strip():
                    issues.append(ValidationIssue("error", f"graph.nodes.{node.name}", "用户提示词模板为空"))
            except ValidationError as exc:
                issues.append(ValidationIssue("error", f"graph.nodes.{node.name}", str(exc)))

    if settings.checkpoint.backend == "postgres" and not settings.database.url:
        issues.append(
            ValidationIssue(
                "warning",
                "database.url",
                "未配置 PGDATABASE_URL，运行时会退化为 MemorySaver",
            )
        )

    return issues
