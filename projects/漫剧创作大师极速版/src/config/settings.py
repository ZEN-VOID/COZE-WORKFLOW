import os
from functools import lru_cache
from typing import Any, Dict, Optional

from config.loader import deep_merge, get_workspace_path, load_json_file, load_yaml_file
from config.models import GraphDefinition, LLMNodeConfig, ProjectSettings


def _normalize_profile(profile: Optional[str]) -> str:
    value = (profile or "").strip().lower()
    if value in {"", "local"}:
        return "local"
    if value in {"dev", "development"}:
        return "dev"
    if value in {"prod", "production"}:
        return "prod"
    return value


def _read_bool(value: Optional[str]) -> Optional[bool]:
    if value is None or value == "":
        return None
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"无法解析布尔配置: {value}")


def _read_int(value: Optional[str]) -> Optional[int]:
    if value is None or value == "":
        return None
    return int(value)


def _set_value(container: Dict[str, Any], section: str, key: str, value: Any) -> None:
    if value is None or value == "":
        return
    section_data = container.setdefault(section, {})
    section_data[key] = value


def _build_env_overrides(profile: str) -> Dict[str, Any]:
    workspace_path = str(get_workspace_path())
    env_name = os.getenv("COZE_ENV") or os.getenv("COZE_PROJECT_ENV") or profile
    overrides: Dict[str, Any] = {}
    _set_value(overrides, "runtime", "env", _normalize_profile(env_name))
    _set_value(overrides, "runtime", "profile", profile)
    _set_value(overrides, "runtime", "workspace_path", workspace_path)
    _set_value(overrides, "http", "host", os.getenv("APP_HOST") or os.getenv("HOST"))
    _set_value(overrides, "http", "port", _read_int(os.getenv("APP_PORT") or os.getenv("PORT")))
    _set_value(overrides, "http", "reload", _read_bool(os.getenv("APP_RELOAD")))
    _set_value(overrides, "http", "workers", _read_int(os.getenv("APP_WORKERS")))
    _set_value(overrides, "workflow", "timeout_seconds", _read_int(os.getenv("WORKFLOW_TIMEOUT_SECONDS")))
    _set_value(overrides, "workflow", "default_input_text", os.getenv("DEFAULT_INPUT_TEXT"))
    _set_value(overrides, "logging", "level", os.getenv("LOG_LEVEL"))
    _set_value(overrides, "logging", "log_file", os.getenv("LOG_FILE"))
    _set_value(overrides, "database", "url", os.getenv("PGDATABASE_URL"))
    _set_value(overrides, "database", "pool_size", _read_int(os.getenv("DB_POOL_SIZE")))
    _set_value(overrides, "database", "max_overflow", _read_int(os.getenv("DB_MAX_OVERFLOW")))
    _set_value(overrides, "database", "pool_timeout", _read_int(os.getenv("DB_POOL_TIMEOUT")))
    _set_value(overrides, "database", "pool_recycle", _read_int(os.getenv("DB_POOL_RECYCLE")))
    _set_value(overrides, "checkpoint", "backend", os.getenv("CHECKPOINT_BACKEND"))
    _set_value(overrides, "checkpoint", "schema", os.getenv("CHECKPOINT_SCHEMA"))
    _set_value(overrides, "checkpoint", "connection_timeout", _read_int(os.getenv("CHECKPOINT_CONNECTION_TIMEOUT")))
    _set_value(overrides, "checkpoint", "max_retries", _read_int(os.getenv("CHECKPOINT_MAX_RETRIES")))
    _set_value(overrides, "storage", "s3_bucket", os.getenv("COZE_BUCKET_NAME"))
    _set_value(overrides, "storage", "s3_region", os.getenv("S3_REGION"))
    _set_value(overrides, "storage", "s3_endpoint_url", os.getenv("S3_ENDPOINT_URL"))
    return overrides


@lru_cache(maxsize=4)
def _load_settings(profile: str) -> ProjectSettings:
    normalized_profile = _normalize_profile(profile)
    base_config = load_yaml_file("config/app/base.yaml")
    profile_config = load_yaml_file(f"config/app/{normalized_profile}.yaml")
    merged = deep_merge(base_config, profile_config)
    merged = deep_merge(merged, _build_env_overrides(normalized_profile))
    runtime_data = merged.setdefault("runtime", {})
    runtime_data.setdefault("profile", normalized_profile)
    runtime_data.setdefault("workspace_path", str(get_workspace_path()))
    runtime_data.setdefault("env", normalized_profile)
    return ProjectSettings.model_validate(merged)


def get_settings(profile: Optional[str] = None, force_reload: bool = False) -> ProjectSettings:
    normalized_profile = _normalize_profile(profile or os.getenv("COZE_ENV") or os.getenv("COZE_PROJECT_ENV"))
    if force_reload:
        _load_settings.cache_clear()
    return _load_settings(normalized_profile)


def load_llm_node_config(config_path: str) -> LLMNodeConfig:
    config_data = load_json_file(config_path)
    return LLMNodeConfig.model_validate(config_data)


def load_graph_definition(config_path: str = "config/graph/main.yaml") -> GraphDefinition:
    config_data = load_yaml_file(config_path)
    return GraphDefinition.model_validate(config_data)
