from llm_prompt_lint.parsers.anthropic import parse_anthropic_messages
from llm_prompt_lint.parsers.openai import parse_openai_chat_completion

__all__ = ["parse_openai_chat_completion", "parse_anthropic_messages", "detect_and_parse"]


def detect_and_parse(data: dict, source_path: str = "<unknown>"):
    """Guess which provider's request shape `data` matches and parse it.

    Anthropic's Messages API is the more distinctively-shaped of the two
    (`stop_sequences`, tool `input_schema`, a top-level `system` string) --
    checked first so an OpenAI-shaped body (`stop`, tool `function.parameters`)
    falls through to the OpenAI parser by default.
    """
    tools = data.get("tools") or []
    looks_anthropic = (
        "stop_sequences" in data
        or (tools and isinstance(tools[0], dict) and "input_schema" in tools[0])
    )
    if looks_anthropic:
        return parse_anthropic_messages(data, source_path)
    return parse_openai_chat_completion(data, source_path)
