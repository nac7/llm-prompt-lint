from __future__ import annotations

from llm_prompt_lint.model import Message, PromptDoc, ToolSpec


def _extract_stop(data: dict) -> list[str]:
    stop = data.get("stop")
    if stop is None:
        return []
    if isinstance(stop, str):
        return [stop]
    return list(stop)


def _extract_tools(data: dict) -> list[ToolSpec]:
    tools = []
    for raw in data.get("tools") or []:
        fn = raw.get("function", raw)
        tools.append(
            ToolSpec(
                name=fn.get("name", ""),
                description=fn.get("description", ""),
                parameters=fn.get("parameters", {}),
            )
        )
    return tools


def _extract_response_format(data: dict) -> str | None:
    rf = data.get("response_format")
    if not rf:
        return None
    return rf.get("type") if isinstance(rf, dict) else str(rf)


def parse_openai_chat_completion(data: dict, source_path: str = "<unknown>") -> PromptDoc:
    """Parse an OpenAI Chat Completions request body into a PromptDoc.

    A leading system-role message is split out into `system`; any further
    system-role messages are left in `messages` so portability rules can
    flag them (OpenAI tolerates them, but not every provider does).
    """
    raw_messages = data.get("messages", [])
    system = None
    messages = []
    for i, m in enumerate(raw_messages):
        role = m.get("role", "")
        content = m.get("content", "")
        if not isinstance(content, str):
            # Multi-part content (e.g. vision blocks): join text parts for linting.
            content = " ".join(
                part["text"] for part in content if isinstance(part, dict) and part.get("text")
            )
        if i == 0 and role == "system":
            system = content
            continue
        messages.append(Message(role=role, content=content))

    return PromptDoc(
        messages=messages,
        system=system,
        temperature=data.get("temperature"),
        top_p=data.get("top_p"),
        stop=_extract_stop(data),
        tools=_extract_tools(data),
        response_format=_extract_response_format(data),
        source_path=source_path,
    )
