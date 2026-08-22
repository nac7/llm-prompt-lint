from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class Message:
    role: str
    content: str


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str = ""
    parameters: dict = field(default_factory=dict)


@dataclass(frozen=True)
class PromptDoc:
    """Provider-agnostic normalization of a chat-completion-style request.

    Parsers (openai.py, anthropic.py) are responsible for mapping each
    provider's request shape onto this common model -- in particular,
    splitting a provider's dedicated system-prompt field (Anthropic's
    `system`, or an OpenAI request's leading system-role message) into
    `system`, so `messages` holds only the user/assistant/tool turns.
    """

    messages: list[Message] = field(default_factory=list)
    system: Optional[str] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    stop: list[str] = field(default_factory=list)
    tools: list[ToolSpec] = field(default_factory=list)
    response_format: Optional[str] = None
    source_path: str = "<unknown>"
