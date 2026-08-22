from __future__ import annotations

from llm_prompt_lint.model import Message, PromptDoc, ToolSpec

# Gemini's generateContent API uses "model" instead of "assistant" for the
# other-turn role, and "function" instead of "tool" for a function-result
# turn -- normalized here so every rule can work off one portable role set.
_ROLE_MAP = {"model": "assistant", "function": "tool"}


def _parts_to_text(parts) -> str:
    if isinstance(parts, str):
        return parts
    return " ".join(p["text"] for p in parts or [] if isinstance(p, dict) and p.get("text"))


def _extract_system(data: dict) -> str | None:
    instruction = data.get("systemInstruction")
    if instruction is None:
        return None
    if isinstance(instruction, str):
        return instruction
    return _parts_to_text(instruction.get("parts"))


def _extract_tools(data: dict) -> list[ToolSpec]:
    tools = []
    for entry in data.get("tools") or []:
        for decl in entry.get("functionDeclarations", []):
            tools.append(
                ToolSpec(
                    name=decl.get("name", ""),
                    description=decl.get("description", ""),
                    parameters=decl.get("parameters", {}),
                )
            )
    return tools


def parse_gemini_generate_content(data: dict, source_path: str = "<unknown>") -> PromptDoc:
    """Parse a Google Gemini generateContent request body into a PromptDoc."""
    messages = []
    for c in data.get("contents", []):
        role = c.get("role", "user")
        content = _parts_to_text(c.get("parts"))
        messages.append(Message(role=_ROLE_MAP.get(role, role), content=content))

    config = data.get("generationConfig") or {}
    response_format = (
        "json_object" if config.get("responseMimeType") == "application/json" else None
    )

    return PromptDoc(
        messages=messages,
        system=_extract_system(data),
        temperature=config.get("temperature"),
        top_p=config.get("topP"),
        stop=list(config.get("stopSequences") or []),
        tools=_extract_tools(data),
        response_format=response_format,
        source_path=source_path,
    )
