## 项目概述
- **名称**: 通用工作流开发环境
- **功能**: 提供标准的扣子工作流开发框架，包含完整的项目结构、节点模板和配置示例，支持快速开发、本地调试和测试验证

### 节点清单
| 节点名 | 文件位置 | 类型 | 功能描述 | 分支逻辑 | 配置文件 |
|-------|---------|------|---------|---------|---------|
| input_node | `src/graphs/nodes/input_node.py` | task | 接收用户输入文本并传递 | - | - |
| process_node | `src/graphs/nodes/process_node.py` | agent | 使用大语言模型处理文本 | - | `config/example_llm_cfg.json` |
| output_node | `src/graphs/nodes/output_node.py` | task | 格式化并输出最终结果 | - | - |

**类型说明**: task(task节点) / agent(大模型) / condition(条件分支) / looparray(列表循环) / loopcond(条件循环)

## 子图清单
| 子图名 | 文件位置 | 功能描述 | 被调用节点 |
|-------|---------|------|---------|-----------|
| - | - | - | - |

## 技能使用
- 节点 `process_node` 使用大语言模型技能 (`/skills/public/prod/llm`)
  - 使用 `coze_coding_dev_sdk` 包中的 `LLMClient`
  - 支持多种模型：doubao-seed-1-8-251228（默认）、doubao-seed-2-0-pro-260215 等

## 项目结构
```
├── config/                          # 配置文件目录
│   └── example_llm_cfg.json        # LLM 节点配置示例
├── src/                            # 源代码目录
│   ├── agents/                     # Agent 代码目录（当前为空）
│   ├── graphs/                     # 工作流编排代码目录
│   │   ├── state.py                # 状态定义（全局状态、图输入输出、节点输入输出）
│   │   ├── graph.py                # 主图编排（节点连接关系）
│   │   └── nodes/                  # 节点实现
│   │       ├── input_node.py       # 输入节点
│   │       ├── process_node.py     # 处理节点（Agent）
│   │       └── output_node.py      # 输出节点
│   ├── storage/                    # 存储相关代码
│   │   ├── database/               # 数据库初始化
│   │   ├── memory/                 # 内存存储
│   │   └── s3/                     # S3 对象存储
│   ├── tools/                      # 工具定义（当前为空）
│   ├── utils/                      # 工具类
│   │   └── file/                   # 文件处理工具
│   └── main.py                     # 运行主入口
├── scripts/                        # 脚本目录
│   ├── local_run.sh                # 本地运行脚本
│   ├── http_run.sh                 # HTTP 服务启动脚本
│   └── setup.sh                    # 环境设置脚本
├── assets/                         # 资源目录（测试数据、静态文件等）
├── requirements.txt                # Python 依赖包
├── README.md                       # 项目说明
└── AGENTS.md                       # 项目索引文档（本文件）
```

## 开发规范

### 1. 状态定义规范
- 所有状态类必须继承 `pydantic.BaseModel`
- 必须为每个字段添加类型注解和 `Field(..., description="...")` 描述
- **禁止**在节点出入参中使用 `GlobalState`
- 每个节点必须定义独立的 `XXXInput` 和 `XXXOutput` 类
- 节点输入和输出必须是不同的类

### 2. 节点函数规范
- 节点函数签名必须严格遵循：
  ```python
  def node_name(
      state: NodeInput,
      config: RunnableConfig,
      runtime: Runtime[Context]
  ) -> NodeOutput:
  ```
- 必须包含完整的 docstring（title, desc, integrations）
- **禁止**使用 `lambda` 实现节点
- **禁止**节点函数生成异步函数
- 所有 `import` 语句必须在文件最顶部

### 3. Agent 节点规范
- LLM 配置必须独立存储在 `config/` 目录下的 JSON 文件中
- 配置文件必须包含：`config`、`sp`、`up`、`tools` 四个字段
- `model` 字段必须从技能获取或用户指定，**禁止**编造
- 在 `add_node` 时必须通过 `metadata` 注入配置文件路径
- SP（系统提示词）必须遵循 Agent SP 生成规则

### 4. 图编排规范
- 主图必须是有向无环图（DAG）
- 循环逻辑必须实现为子图（`loop_graph.py`）
- `add_node` 直接添加节点函数对象，**禁止**包装函数
- `add_edge` 使用节点函数名字符串，**禁止**使用函数对象
- 必须指定图的 `input_schema` 和 `output_schema`

### 5. 文件导入规范
- **禁止**在 import 路径中包含 `src.` 前缀
- 正确示例：`from graphs.state import NodeInput`
- 错误示例：`from src.graphs.state import NodeInput`
- 必须显式导入所有使用的标准库（`os`, `json`, `re`, `datetime` 等）

### 6. 防御性编程规范
- 所有外部输入使用前必须判空和类型检查
- Optional 类型使用前必须判空
- 优先使用 `.get(key, default)` 访问字典
- **禁止**链式调用外部输入的方法（如 `response.content.strip()`）

### 7. 测试规范
- 代码完成后必须执行 `test_run` 测试
- 测试失败时读取日志定位问题
- 循环修复直到测试成功
- 尝试 5 次失败后停止并如实告知用户

## 快速开始

### 1. 本地运行
```bash
# 运行完整工作流
bash scripts/local_run.sh -m flow

# 运行单个节点
bash scripts/local_run.sh -m node -n process_node
```

### 2. 启动 HTTP 服务
```bash
bash scripts/http_run.sh -m http -p 5000
```

### 3. 开发新节点
1. 在 `src/graphs/state.py` 中定义节点的输入输出类型
2. 在 `src/graphs/nodes/` 中创建新的节点文件
3. 如果是 Agent 节点，在 `config/` 中创建配置文件
4. 在 `src/graphs/graph.py` 中添加节点并连接边
5. 运行测试验证

### 4. 测试工作流
```python
# 在 Python 中测试
from graphs.graph import main_graph

result = main_graph.invoke({"input_text": "测试输入"})
print(result)
```

## 示例工作流说明

当前示例实现了一个简单的线性工作流：

1. **input_node**: 接收用户输入文本
2. **process_node**: 使用 LLM 处理文本（Agent 节点）
3. **output_node**: 格式化并输出结果

流程图：
```
Input → [input_node] → [process_node] → [output_node] → Output
```

## 扩展指南

### 添加条件分支
1. 在 `state.py` 中定义条件判断节点的输入类型
2. 创建条件判断函数（返回分支名称）
3. 在 `graph.py` 中使用 `add_conditional_edges` 添加分支

### 添加并行执行
```python
builder.add_edge("node_a", "parallel_node1")
builder.add_edge("node_a", "parallel_node2")
builder.add_edge(["parallel_node1", "parallel_node2"], "merge_node")
```

### 添加循环
1. 在 `loop_graph.py` 中定义子图
2. 在主图中创建调用子图的节点
3. 添加 `metadata={"type": "looparray"}` 或 `{"type": "loopcond"}`

### 集成新技能
1. 使用 `load_skill` 加载技能文档
2. 按照技能文档在节点中实现集成
3. 更新 `AGENTS.md` 中的技能使用说明
