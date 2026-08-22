from __future__ import annotations

from llm_prompt_lint.model import Message, PromptDoc, ToolSpec


def _extract_tools(data: dict) -> list[ToolSpec]:
    tools = []
    for raw in data.get("tools") or []:
        tools.append(
            ToolSpec(
                name=raw.get("name", ""),
                description=raw.get("description", ""),
                parameters=raw.get("input_schema", {}),
            )
        )
    return tools


def parse_anthropic_messages(data: dict, source_path: str = "<unknown>") -> PromptDoc:
    """Parse an Anthropic Messages API request body into a PromptDoc.

    Anthropic takes `system` as a dedicated top-level field, never a message
    with role "system" -- so unlike the OpenAI parser, nothing needs
    splitting out of `messages` here.
    """
    system = data.get("system")
    if isinstance(system, list):
        # Structured system blocks (e.g. with cache_control): join text parts.
        system = " ".join(
            block["text"] for block in system if isinstance(block, dict) and block.get("text")
        )

    messages = []
    for m in data.get("messages", []):
        role = m.get("role", "")
        content = m.get("content", "")
        if not isinstance(content, str):
            content = " ".join(
                part["text"] for part in content if isinstance(part, dict) and part.get("text")
            )
        messages.append(Message(role=role, content=content))

    return PromptDoc(
        messages=messages,
        system=system,
        temperature=data.get("temperature"),
        top_p=data.get("top_p"),
        stop=list(data.get("stop_sequences") or []),
        tools=_extract_tools(data),
        response_format=None,
        source_path=source_path,
    )
