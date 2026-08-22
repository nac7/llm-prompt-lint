from llm_prompt_lint.parsers.anthropic import parse_anthropic_messages
from llm_prompt_lint.parsers.gemini import parse_gemini_generate_content
from llm_prompt_lint.parsers.openai import parse_openai_chat_completion

__all__ = [
    "parse_openai_chat_completion",
    "parse_anthropic_messages",
    "parse_gemini_generate_content",
    "detect_provider",
    "detect_and_parse",
]


def detect_provider(data: dict) -> str:
    """Guess which provider's request shape `data` matches.

    Gemini's `contents`/`generationConfig` shape and Anthropic's Messages API
    shape (`stop_sequences`, tool `input_schema`, a top-level `system` string)
    are both distinctive enough to check first; an OpenAI-shaped body
    (`messages`, `stop`, tool `function.parameters`) is the default fallthrough.
    """
    if "contents" in data:
        return "gemini"

    tools = data.get("tools") or []
    looks_anthropic = "stop_sequences" in data or (
        tools and isinstance(tools[0], dict) and "input_schema" in tools[0]
    )
    if looks_anthropic:
        return "anthropic"

    return "openai"


_PARSERS = {
    "openai": parse_openai_chat_completion,
    "anthropic": parse_anthropic_messages,
    "gemini": parse_gemini_generate_content,
}


def detect_and_parse(data: dict, source_path: str = "<unknown>"):
    provider = detect_provider(data)
    return _PARSERS[provider](data, source_path)
