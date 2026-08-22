from llm_prompt_lint.fixers._shared import MAX_STOP_SEQUENCES, strip_special_tokens
from llm_prompt_lint.report import Fix


def _merge_system_messages(data: dict, path: str) -> list[Fix]:
    # Anthropic's API has no system-role message -- any role=="system" entry
    # in `messages` is malformed input (e.g. ported from OpenAI without
    # adjustment). Fold it into the dedicated top-level `system` field.
    messages = data.get("messages", [])
    system_indices = [i for i, m in enumerate(messages) if m.get("role") == "system"]
    if not system_indices:
        return []
    if any(not isinstance(messages[i].get("content"), str) for i in system_indices):
        return []

    parts = [messages[i]["content"] for i in system_indices if messages[i]["content"].strip()]
    existing = data.get("system")
    if isinstance(existing, str) and existing.strip():
        parts.insert(0, existing)
    merged = "\n".join(parts)

    data["messages"] = [m for i, m in enumerate(messages) if i not in system_indices]
    if merged:
        data["system"] = merged

    return [
        Fix(
            rule_id="system-prompt/merged",
            message=(
                f"moved {len(system_indices)} inline system-role message(s) into the "
                "top-level system field"
            ),
            path=path,
        )
    ]


def _drop_empty_system_field(data: dict, path: str) -> list[Fix]:
    system = data.get("system")
    if isinstance(system, str) and not system.strip():
        del data["system"]
        return [Fix(rule_id="system-prompt/empty", message="removed empty system field", path=path)]
    return []


def _strip_leaked_tokens(data: dict, path: str) -> list[Fix]:
    changed = False
    system = data.get("system")
    if isinstance(system, str):
        cleaned = strip_special_tokens(system).strip()
        if cleaned != system:
            data["system"] = cleaned
            changed = True
    for m in data.get("messages", []):
        content = m.get("content")
        if isinstance(content, str):
            cleaned = strip_special_tokens(content).strip()
            if cleaned != content:
                m["content"] = cleaned
                changed = True
    if not changed:
        return []
    return [
        Fix(
            rule_id="leaked-special-tokens",
            message="stripped leaked chat-template tokens",
            path=path,
        )
    ]


def _truncate_stop_sequences(data: dict, path: str) -> list[Fix]:
    stop = data.get("stop_sequences")
    if not isinstance(stop, list) or len(stop) <= MAX_STOP_SEQUENCES:
        return []
    dropped = stop[MAX_STOP_SEQUENCES:]
    data["stop_sequences"] = stop[:MAX_STOP_SEQUENCES]
    return [
        Fix(
            rule_id="stop-sequences",
            message=f"truncated to {MAX_STOP_SEQUENCES} stop sequences, dropped {dropped!r}",
            path=path,
        )
    ]


def fix(data: dict, path: str = "<unknown>") -> list[Fix]:
    fixes: list[Fix] = []
    fixes += _merge_system_messages(data, path)
    fixes += _drop_empty_system_field(data, path)
    fixes += _strip_leaked_tokens(data, path)
    fixes += _truncate_stop_sequences(data, path)
    return fixes
