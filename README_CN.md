# Lightdash MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-compatible-green.svg)](https://modelcontextprotocol.io/)
[![PyPI](https://img.shields.io/pypi/v/lightdash-mcp.svg)](https://pypi.org/project/lightdash-mcp/)
[![GitHub stars](https://img.shields.io/github/stars/zbmain/lightdash_mcp)](https://github.com/zbmain/lightdash_mcp/stargazers)

> 使用 Model Context Protocol (MCP) 将 Claude、Cursor 等 AI 助手连接到 Lightdash 分析平台。

Lightdash 的 Model Context Protocol (MCP) 服务器，使 LLM 能够以编程方式发现数据、创建图表和管理仪表板。

## 功能特性

本 MCP 服务器提供完整数据分析工作流程的全面工具集：

*   **数据发现**：探索数据目录，查找表/explores，理解数据结构
*   **数据查询**：支持完整筛选、指标和聚合的查询执行
*   **图表管理**：创建、读取、更新和删除复杂可视化图表
*   **仪表板管理**：构建和管理包含卡片、筛选器和布局的仪表板
*   **资源组织**：创建和管理用于组织内容的空间

## 安装

### 前置要求

*   Python 3.10+
*   Lightdash 实例（云端或自托管）
*   Lightdash 个人访问令牌（从个人设置中获取）

### 使用 pip 快速安装（推荐）

```bash
pip install lightdash-mcp
```

### 使用 uvx 快速安装

```bash
uvx lightdash-mcp
```

### 使用 pipx 快速安装

```bash
pipx run lightdash-mcp
```

### 从源码安装

```bash
git clone https://github.com/zbmain/lightdash_mcp.git
cd lightdash_mcp
pip install .
```

### Google Cloud IAP 支持

如果 Lightdash 实例部署在 [Google Cloud Identity-Aware Proxy](https://cloud.google.com/iap) 后面（如使用 `--iap` 的 Cloud Run），请安装带 `iap` 扩展的版本：

```bash
pip install lightdash-mcp[iap]
# 或从源码安装
pip install .[iap]
```

设置 `IAP_ENABLED=true`。服务器将通过 IAM Credentials API 签署 JWT（受众为 `{LIGHTDASH_URL}/*`），并在每个请求中附加为 `Proxy-Authorization: Bearer <jwt>`。Lightdash 的 `Authorization: ApiKey` 请求头保持不变。

支持两种凭据类型：

**服务账号凭据**（Cloud Run、GCE 等默认方式）：
- 运行时服务账号需要对自己拥有 `roles/iam.serviceAccountTokenCreator` 权限
- 运行时服务账号需要对 Cloud Run 服务拥有 `roles/iap.httpsResourceAccessor` 权限

**用户凭据（ADC）**（如 `gcloud auth application-default login`）：
- 设置 `IAP_SA` 为用于签署 JWT 的服务账号邮箱
- 用户需要在目标服务账号上拥有 `roles/iam.serviceAccountTokenCreator` 权限
- 目标服务账号需要对 Cloud Run 服务拥有 `roles/iap.httpsResourceAccessor` 权限

## 配置

### 环境变量

服务器需要以下环境变量：

| 变量 | 必填 | 说明 | 示例 |
| :--- | :---: | :--- | :--- |
| `LIGHTDASH_TOKEN` | ✅ | 你的 Lightdash 个人访问令牌 | `ldt_abc123...` |
| `LIGHTDASH_URL` | ✅ | Lightdash 实例的基础 URL | `https://app.lightdash.cloud` |
| `CF_ACCESS_CLIENT_ID` | ❌ | Cloudflare Access 客户端 ID（如果使用 CF Access） | - |
| `CF_ACCESS_CLIENT_SECRET` | ❌ | Cloudflare Access 客户端密钥（如果使用 CF Access） | - |
| `LIGHTDASH_PROJECT_UUID` | ❌ | 默认项目 UUID（留空则自动使用第一个可用项目） | `3fc2835f-...` |
| `IAP_ENABLED` | ❌ | 启用 Google Cloud IAP 认证（`true`/`1`） | `true` |
| `IAP_SA` | ❌ | 使用用户凭据（ADC）时用于签署 JWT 的服务账号邮箱 | `sa@project.iam.gserviceaccount.com` |

### 获取 Lightdash 令牌

1. 登录你的 Lightdash 实例
2. 进入 **设置** → **个人访问令牌**
3. 点击 **生成新令牌**
4. 复制令牌（以 `ldt_` 开头）

### 在 Claude Desktop 中使用

在 `claude_desktop_config.json` 中添加以下配置：

```json
{
  "mcpServers": {
    "lightdash": {
      "command": "uvx",
      "args": ["lightdash-mcp"],
      "env": {
        "LIGHTDASH_TOKEN": "ldt_your_token_here",
        "LIGHTDASH_URL": "https://app.lightdash.cloud",
        "LIGHTDASH_PROJECT_UUID": "your-project-uuid"
      }
    }
  }
}
```

### 在 Claude Code (CLI) 中使用

在项目根目录创建或编辑 `.mcp.json`：

```json
{
  "mcpServers": {
    "lightdash": {
      "type": "stdio",
      "command": "lightdash-mcp",
      "env": {
        "LIGHTDASH_URL": "https://your-lightdash-instance.com",
        "LIGHTDASH_TOKEN": "ldt_your_token_here",
        "LIGHTDASH_PROJECT_UUID": "your-project-uuid"
      }
    }
  }
}
```

重启 Claude Code 并运行 `/mcp` 验证服务器已连接。

> **注意**：如果 `.mcp.json` 包含敏感信息，请勿将其提交到版本控制 —— 请将其添加到 `.gitignore`。

### 在其他 MCP 客户端中使用

运行前先导出环境变量：

```bash
export LIGHTDASH_TOKEN="ldt_your_token_here"
export LIGHTDASH_URL="https://app.lightdash.cloud"
lightdash-mcp
```

## 可用工具

### 📊 数据发现与元数据

| 工具 | 说明 |
| :--- | :--- |
| `list-projects` | 列出 Lightdash 组织中的所有可用项目 |
| `get-project` | 获取特定项目的详细信息 |
| `list-explores` | 列出项目中所有可用的 explores/表 |
| `get-explore-schema` | 获取特定 explore 的详细结构（维度、指标、关联） |
| `list-spaces` | 列出项目中的所有空间（文件夹） |
| `get-custom-metrics` | 获取项目中定义的自定义指标 |
| `list-table-field-values` | 搜索特定表字段的唯一值 |

### 📈 图表管理

| 工具 | 说明 |
| :--- | :--- |
| `list-charts` | 列出所有已保存的图表，支持按名称筛选 |
| `search-charts` | 按名称或描述搜索图表 |
| `get-chart-details` | 获取特定图表的完整配置 |
| `run-chart-query` | 执行图表查询并返回数据 |

### 📋 仪表板管理

| 工具 | 说明 |
| :--- | :--- |
| `list-dashboards` | 列出项目中的所有仪表板 |
| `get-dashboard-tiles` | 获取仪表板的所有卡片，支持可选的完整配置 |
| `get-dashboard-tile-chart-config` | 获取特定仪表板卡片的完整图表配置 |
| `get-dashboard-code` | 以代码形式获取完整仪表板配置 |
| `run-dashboard-tiles` | 并发执行一个、多个或所有仪表板卡片 |

### 🔍 查询执行

| 工具 | 说明 |
| :--- | :--- |
| `run-chart-query` | 执行已保存图表的查询并返回数据 |
| `run-dashboard-tiles` | 执行仪表板卡片的查询（支持批量执行） |
| `run-raw-query` | 对任何 explore 执行即席指标查询 |

### 🗂️ 资源管理

## 项目结构

```
.
├── Justfile                     # Just 常用开发任务快捷命令
├── pyproject.toml               # 包配置
├── lightdash_mcp/               # 主包
│   ├── __init__.py              # 包初始化
│   ├── server.py                # MCP 服务器入口
│   ├── lightdash_client.py      # Lightdash API 客户端
│   ├── tools_registry.yml       # 工具注册配置（YAML）
│   └── tools/                   # 工具实现
│       ├── __init__.py          # 自动发现与工具注册（YAML 过滤）
│       ├── base_tool.py         # 基础工具接口
│       └── *.py                 # 各工具实现文件
├── README.md
└── LICENSE
```

## 开发

### 添加新工具

服务器自动从 `tools/` 目录发现和注册工具。添加新工具的步骤如下：

1.  **创建新文件**：在 `lightdash_mcp/tools/` 下创建新文件（如 `my_new_tool.py`）

2.  **定义工具**：
    ```python
    from pydantic import BaseModel, Field
    from .base_tool import ToolDefinition
    from .. import lightdash_client as client

    class MyToolInput(BaseModel):
        param1: str = Field(..., description="param1 的描述")

    TOOL_DEFINITION = ToolDefinition(
        name="my-new-tool",
        description="此工具的功能描述",
        input_schema=MyToolInput
    )

    def run(param1: str) -> dict:
        """执行工具逻辑"""
        result = client.get(f"/api/v1/some/endpoint/{param1}")
        return result
    ```

3.  **在 YAML 中注册**：在 `tools_registry.yml` 中添加工具条目并设置 `enabled: true`

4.  **重启服务器** —— 工具将自动注册

### 测试

可以直接导入工具进行测试：

```python
from lightdash_mcp.tools import tool_registry

# 列出所有已注册工具
print(tool_registry.keys())

# 测试特定工具
result = tool_registry['list-projects'].run()
print(result)
```

## 工具注册机制

工具通过以下两种机制自动发现和过滤：

1. **自动发现**：`tools/__init__.py` 扫描 `tools/` 目录下的 Python 模块
2. **YAML 过滤**：只有 `tools_registry.yml` 中 `enabled: true` 的工具才会被注册

### tools_registry.yml

集中式 YAML 配置（`lightdash_mcp/tools_registry.yml`）控制哪些工具处于激活状态。它允许你：
- 无需删除代码即可启用/禁用单个工具
- 按类别（discovery、chart、dashboard、query、resource）对工具分组
- 将禁用的工具保留在代码库中供将来使用

```yaml
tools:
  - name: list-projects
    category: discovery
    enabled: true   # ← 只有 enabled=true 的工具才会被注册
```

### 验证注册

```bash
# 检查 YAML 配置与已发现工具是否同步
just validate-registry
```

## 故障排除

### 认证错误

如果遇到 `401 Unauthorized` 错误：
*   确认 `LIGHTDASH_TOKEN` 正确且以 `ldt_` 开头
*   检查令牌是否已过期
*   确保你在 Lightdash 中有所需的权限

### 连接错误

如果遇到连接错误：
*   确认 `LIGHTDASH_URL` 正确
*   Lightdash 云端：使用 `https://app.lightdash.cloud`
*   自托管：使用 `https://your-domain.com`
*   如果使用 Cloudflare Access，请确保设置了 `CF_ACCESS_CLIENT_ID` 和 `CF_ACCESS_CLIENT_SECRET`
*   如果使用 Google Cloud IAP，请确保设置了 `IAP_ENABLED=true`，并使用 `pip install lightdash-mcp[iap]` 安装，同时验证服务账号对自己拥有 `serviceAccountTokenCreator` 权限

### 工具未找到

如果工具没有出现：
*   检查文件是否在 `tools/` 目录中
*   确保文件定义了 `TOOL_DEFINITION` 变量
*   确认文件不在 `tools/__init__.py` 的排除列表中
*   重启 MCP 服务器

## 贡献

欢迎贡献！请：
1. Fork 本仓库
2. 创建功能分支
3. 添加适当的测试
4. 提交 Pull Request

## 许可证

本项目采用 MIT 许可证 —— 详见 [LICENSE](LICENSE) 文件。

## 致谢

* [poddubnyoleg/lightdash_mcp](https://github.com/poddubnyoleg/lightdash_mcp) - 原始项目，本 fork 基于此。

## 获取支持

如有问题：
*   [Lightdash 文档](https://docs.lightdash.com/)
*   [Lightdash 社区 Slack](https://join.slack.com/t/lightdash-community/shared_invite/)
*   [MCP 文档](https://modelcontextprotocol.io/)
