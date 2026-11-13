import yaml
from pathlib import Path
from typing import Any


def load_config(path: str = "dataset_config.yaml") -> dict:
    """Load and validate the main config file."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(p, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    # Basic validation
    required_keys = ["source", "filters", "generation", "output"]
    for key in required_keys:
        if key not in cfg:
            raise ValueError(f"Missing required config key: '{key}'")

    return cfg