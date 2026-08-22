from __future__ import annotations

import json
import os

DEFAULT_CONFIG_PATH = ".llm-prompt-lint.json"


def load_ignore_config(config_path: str = DEFAULT_CONFIG_PATH) -> list[str]:
    """Read a rule-id ignore list from a sidecar JSON config file.

    Deliberately not embedded in the request JSON being linted: those files
    are meant to double as real API request bodies (see README), and an
    extra top-level key could be rejected by a provider that's strict about
    unknown fields.
    """
    if not os.path.isfile(config_path):
        return []

    try:
        with open(config_path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SystemExit(f"llm-prompt-lint: could not read {config_path}: {exc}") from exc

    ignore = data.get("ignore", []) if isinstance(data, dict) else None
    if not isinstance(ignore, list) or not all(isinstance(x, str) for x in ignore):
        raise SystemExit(f'llm-prompt-lint: {config_path} must be {{"ignore": [<rule-id>, ...]}}')
    return ignore


def is_ignored(rule_id: str, ignore: list[str]) -> bool:
    """True if `rule_id` (e.g. "system-prompt/empty") matches an ignore
    entry -- either exactly, or as a family prefix ("system-prompt" ignores
    every "system-prompt/*" rule)."""
    return any(rule_id == pattern or rule_id.startswith(f"{pattern}/") for pattern in ignore)
