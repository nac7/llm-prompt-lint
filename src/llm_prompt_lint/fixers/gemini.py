from llm_prompt_lint.fixers._shared import MAX_STOP_SEQUENCES, strip_special_tokens
from llm_prompt_lint.report import Fix


def _parts_text(parts) -> str:
    if isinstance(parts, str):
        return parts
    if isinstance(parts, list) and all(isinstance(p, dict) for p in parts):
        return " ".join(p["text"] for p in parts if p.get("text"))
    return ""


def _instruction_text(instruction) -> str:
    """Extract text from a systemInstruction value, which may be a bare
    string or the dict shape ({"parts": [...]})  the real API expects."""
    if instruction is None:
        return ""
    if isinstance(instruction, str):
        return instruction
    if isinstance(instruction, dict):
        return _parts_text(instruction.get("parts"))
    return ""


def _merge_system_contents(data: dict, path: str) -> list[Fix]:
    # Gemini's API has no system-role content entry -- any role=="system"
    # entry is malformed input. Fold it into the dedicated systemInstruction.
    contents = data.get("contents", [])
    system_indices = [i for i, c in enumerate(contents) if c.get("role") == "system"]
    if not system_indices:
        return []
    if any(
        not isinstance(contents[i].get("parts"), (str, list)) for i in system_indices
    ):
        return []

    texts = [_parts_text(contents[i]["parts"]) for i in system_indices]
    texts = [t for t in texts if t.strip()]
    existing_text = _instruction_text(data.get("systemInstruction"))
    if existing_text.strip():
        texts.insert(0, existing_text)
    merged = "\n".join(texts)

    data["contents"] = [c for i, c in enumerate(contents) if i not in system_indices]
    if merged:
        data["systemInstruction"] = {"parts": [{"text": merged}]}

    return [
        Fix(
            rule_id="system-prompt/merged",
            message=(
                f"moved {len(system_indices)} system-role content(s) into systemInstruction"
            ),
            path=path,
        )
    ]


def _drop_empty_system_instruction(data: dict, path: str) -> list[Fix]:
    instruction = data.get("systemInstruction")
    if instruction is None:
        return []
    if not _instruction_text(instruction).strip():
        del data["systemInstruction"]
        return [
            Fix(rule_id="system-prompt/empty", message="removed empty systemInstruction", path=path)
        ]
    return []


def _strip_leaked_tokens(data: dict, path: str) -> list[Fix]:
    changed = False

    instruction = data.get("systemInstruction")
    if isinstance(instruction, dict):
        for part in instruction.get("parts", []):
            if isinstance(part, dict) and isinstance(part.get("text"), str):
                cleaned = strip_special_tokens(part["text"]).strip()
                if cleaned != part["text"]:
                    part["text"] = cleaned
                    changed = True

    for c in data.get("contents", []):
        parts = c.get("parts")
        if isinstance(parts, list):
            for part in parts:
                if isinstance(part, dict) and isinstance(part.get("text"), str):
                    cleaned = strip_special_tokens(part["text"]).strip()
                    if cleaned != part["text"]:
                        part["text"] = cleaned
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
    config = data.get("generationConfig")
    if not isinstance(config, dict):
        return []
    stop = config.get("stopSequences")
    if not isinstance(stop, list) or len(stop) <= MAX_STOP_SEQUENCES:
        return []
    dropped = stop[MAX_STOP_SEQUENCES:]
    config["stopSequences"] = stop[:MAX_STOP_SEQUENCES]
    return [
        Fix(
            rule_id="stop-sequences",
            message=f"truncated to {MAX_STOP_SEQUENCES} stop sequences, dropped {dropped!r}",
            path=path,
        )
    ]


def fix(data: dict, path: str = "<unknown>") -> list[Fix]:
    fixes: list[Fix] = []
    fixes += _merge_system_contents(data, path)
    fixes += _drop_empty_system_instruction(data, path)
    fixes += _strip_leaked_tokens(data, path)
    fixes += _truncate_stop_sequences(data, path)
    return fixes
