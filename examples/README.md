# 扣子工作流项目模板

## 配置结构

```text
config/
├── app/
│   ├── base.yaml
│   ├── local.yaml
│   ├── dev.yaml
│   └── prod.yaml
├── graph/
│   └── main.yaml
├── llm/
│   └── process_node.json
└── schema/
    ├── app_config.schema.json
    ├── graph_config.schema.json
    └── llm_node.schema.json
```

## 配置优先级

运行时按以下顺序覆盖配置：

1. CLI 参数
2. 已存在的环境变量
3. `.env` / `.env.local`
4. `config/app/<profile>.yaml`
5. `config/app/base.yaml`

## 环境准备

1. 复制 `/Volumes/CODE/COZE-WORKFLOW/examples/.env.example:1` 为 `.env`
2. 设置 `COZE_WORKSPACE_PATH` 为当前 `examples/` 绝对路径
3. 按需补充 `PGDATABASE_URL`、`COZE_BUCKET_NAME` 等基础设施配置

## 配置校验

```bash
python scripts/validate_config.py
```

## 本地运行

### 运行完整流程

```bash
bash scripts/local_run.sh -m flow -i '{"input_text":"你好"}'
```

### 运行单个节点

```bash
bash scripts/local_run.sh -m node -n process_node -i '{"input_text":"测试"}'
```

### 启动 HTTP 服务

```bash
bash scripts/http_run.sh -p 5000
```

## 关键配置说明

- `config/app/*.yaml` 管理运行环境、HTTP、日志、超时、数据库和 checkpoint 策略
- `config/graph/main.yaml` 管理主图入口节点、节点列表和边关系
- `config/llm/process_node.json` 管理 Agent 节点模型参数、系统提示词和用户提示词模板
- `scripts/validate_config.py` 在运行前检查图配置与 Agent 配置结构

## 扩展建议

- 新增 Agent 节点时，在 `config/llm/` 下新增独立 JSON 配置
- 新增子图时，在 `config/graph/` 下增加对应图定义文件
- 切换环境时，优先通过 `COZE_ENV=local|dev|prod` 选择 profile
