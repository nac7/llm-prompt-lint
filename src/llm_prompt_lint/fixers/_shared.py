import re

from llm_prompt_lint.rules.special_tokens import PATTERNS as SPECIAL_TOKEN_PATTERNS
from llm_prompt_lint.rules.stop_sequences import OPENAI_MAX_STOP_SEQUENCES

MAX_STOP_SEQUENCES = OPENAI_MAX_STOP_SEQUENCES

_RUN_OF_SPACES = re.compile(r"[ \t]{2,}")


def strip_special_tokens(text: str) -> str:
    """Remove chat-template tokens, collapsing the space gap they leave
    behind -- but only runs of plain spaces/tabs, so an intentional newline
    (e.g. from merging multiple system messages) is left alone."""
    for pattern in SPECIAL_TOKEN_PATTERNS:
        text = pattern.sub(" ", text)
    return _RUN_OF_SPACES.sub(" ", text).strip()
