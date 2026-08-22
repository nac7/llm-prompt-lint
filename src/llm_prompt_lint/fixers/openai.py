from llm_prompt_lint.fixers._shared import MAX_STOP_SEQUENCES, strip_special_tokens
from llm_prompt_lint.report import Fix


def _merge_system_messages(data: dict, path: str) -> list[Fix]:
    messages = data.get("messages", [])
    system_indices = [i for i, m in enumerate(messages) if m.get("role") == "system"]
    if not system_indices or system_indices == [0]:
        return []

    # A system message with structured (non-string) content is rare and we
    # don't know how to losslessly merge it -- leave it for manual review
    # rather than risk dropping content.
    if any(not isinstance(messages[i].get("content"), str) for i in system_indices):
        return []

    parts = [messages[i]["content"] for i in system_indices if messages[i]["content"].strip()]
    merged = "\n".join(parts)
    new_messages = [m for i, m in enumerate(messages) if i not in system_indices]
    if merged:
        new_messages.insert(0, {"role": "system", "content": merged})
    data["messages"] = new_messages

    return [
        Fix(
            rule_id="system-prompt/merged",
            message=(
                f"merged {len(system_indices)} system-role message(s) into a single "
                "leading system message"
            ),
            path=path,
        )
    ]


def _drop_empty_system_message(data: dict, path: str) -> list[Fix]:
    messages = data.get("messages", [])
    if messages and messages[0].get("role") == "system":
        content = messages[0].get("content")
        if isinstance(content, str) and not content.strip():
            data["messages"] = messages[1:]
            return [
                Fix(
                    rule_id="system-prompt/empty",
                    message="removed empty system message",
                    path=path,
                )
            ]
    return []


def _strip_leaked_tokens(data: dict, path: str) -> list[Fix]:
    changed = False
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
            message="stripped leaked chat-template tokens from message content",
            path=path,
        )
    ]


def _truncate_stop_sequences(data: dict, path: str) -> list[Fix]:
    stop = data.get("stop")
    if not isinstance(stop, list) or len(stop) <= MAX_STOP_SEQUENCES:
        return []
    dropped = stop[MAX_STOP_SEQUENCES:]
    data["stop"] = stop[:MAX_STOP_SEQUENCES]
    return [
        Fix(
            rule_id="stop-sequences",
            message=f"truncated to {MAX_STOP_SEQUENCES} stop sequences, dropped {dropped!r}",
            path=path,
        )
    ]


def _rename_legacy_function_role(data: dict, path: str) -> list[Fix]:
    fixes = []
    for m in data.get("messages", []):
        if m.get("role") == "function":
            m["role"] = "tool"
            fixes.append(
                Fix(
                    rule_id="unsupported-role/legacy-function",
                    message=(
                        "renamed role 'function' to 'tool' -- add a matching tool_call_id "
                        "by hand, this can't be inferred automatically"
                    ),
                    path=path,
                    needs_manual_followup=True,
                )
            )
    return fixes


def fix(data: dict, path: str = "<unknown>") -> list[Fix]:
    fixes: list[Fix] = []
    fixes += _merge_system_messages(data, path)
    fixes += _drop_empty_system_message(data, path)
    fixes += _strip_leaked_tokens(data, path)
    fixes += _truncate_stop_sequences(data, path)
    fixes += _rename_legacy_function_role(data, path)
    return fixes
