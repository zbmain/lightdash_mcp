import importlib
import pkgutil
from pathlib import Path

import yaml

# YAML 配置文件路径（相对于源码目录）
_REGISTRY_YAML_PATH = Path(__file__).parent.parent / "tools_registry.yml"

# 从 YAML 中加载注册配置
_enabled_tools: set[str] = set()
_registry_config: dict = {}
_registry_defaults: dict[str, dict] = {}  # tool_name -> {param: default_value}

if _REGISTRY_YAML_PATH.exists():
    with open(_REGISTRY_YAML_PATH, encoding="utf-8") as f:
        _registry_config = yaml.safe_load(f) or {}
    _enabled_tools = {
        t["name"] for t in _registry_config.get("tools", []) if t.get("enabled", False)
    }
    # 从 tools[].defaults 提取默认值映射
    for tool_entry in _registry_config.get("tools", []):
        if "defaults" in tool_entry:
            _registry_defaults[tool_entry["name"]] = tool_entry["defaults"]

# 自动发现所有工具模块（使用 pkgutil，仅当工具在 registry.yml 中 enabled=true 时才注册）
tool_registry: dict[str, object] = {}

for _, module_name, _ in pkgutil.iter_modules(__path__):
    if module_name in ("base_tool", "utils", "dashboard_utils"):
        continue
    module = importlib.import_module(f".{module_name}", package=__name__)
    tool_name = module.TOOL_DEFINITION.name
    if _enabled_tools and tool_name not in _enabled_tools:
        continue
    tool_registry[tool_name] = module


def validate_registry() -> None:
    """验证 YAML 配置中的工具是否都存在，返回详细信息。"""
    tools_dir = Path(__file__).parent
    _EXCLUDED = {"base_tool", "utils", "dashboard_utils", "__init__"}
    discovered = {p.stem for p in tools_dir.glob("*.py") if p.stem not in _EXCLUDED}

    yaml_tool_names = {t["name"] for t in _registry_config.get("tools", [])}

    def to_module_name(name: str) -> str:
        return name.replace("-", "_")

    missing = {n for n in yaml_tool_names if to_module_name(n) not in discovered}
    orphaned = discovered - {to_module_name(n) for n in yaml_tool_names}

    print(f"Total registered tools: {len(tool_registry)}")
    print(f"Tools in registry.yml:  {len(yaml_tool_names)}")
    print(f"Discovered modules:     {len(discovered)}")

    if missing:
        print(
            f"\n[WARN] Tools in registry.yml but not found in tools/: {sorted(missing)}"
        )
    if orphaned:
        print(f"\n[INFO] Tools in tools/ but not in registry.yml: {sorted(orphaned)}")
    if not missing and not orphaned:
        print("\n[PASS] registry.yml and discovered tools are in sync.")
