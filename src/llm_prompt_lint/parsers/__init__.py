from llm_prompt_lint.parsers.anthropic import parse_anthropic_messages
from llm_prompt_lint.parsers.gemini import parse_gemini_generate_content
from llm_prompt_lint.parsers.openai import parse_openai_chat_completion

__all__ = [
    "parse_openai_chat_completion",
    "parse_anthropic_messages",
    "parse_gemini_generate_content",
    "detect_and_parse",
]


def detect_and_parse(data: dict, source_path: str = "<unknown>"):
    """Guess which provider's request shape `data` matches and parse it.

    Gemini's `contents`/`generationConfig` shape and Anthropic's Messages API
    shape (`stop_sequences`, tool `input_schema`, a top-level `system` string)
    are both distinctive enough to check first; an OpenAI-shaped body
    (`messages`, `stop`, tool `function.parameters`) is the default fallthrough.
    """
    if "contents" in data:
        return parse_gemini_generate_content(data, source_path)

    tools = data.get("tools") or []
    looks_anthropic = (
        "stop_sequences" in data
        or (tools and isinstance(tools[0], dict) and "input_schema" in tools[0])
    )
    if looks_anthropic:
        return parse_anthropic_messages(data, source_path)
    return parse_openai_chat_completion(data, source_path)
