import yaml
from pathlib import Path
from typing import Optional

_PROMPT_DIR = Path(__file__).resolve().parent.parent / "prompts"


def _load_yaml(path: Path) -> Optional[dict]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception:
        return None


def get_prompt(agent_name: str, key: str = "system") -> str:
    """Load a prompt template for an agent from app/prompts/{agent_name}.yaml.

    Falls back to empty string if not found. Designed to be additive and non-breaking.
    """
    p = _PROMPT_DIR / f"{agent_name}.yaml"
    data = _load_yaml(p)
    if not data:
        return ""
    return data.get(key, "")
