from llm_prompt_lint.fixers import anthropic, gemini, openai
from llm_prompt_lint.parsers import detect_provider
from llm_prompt_lint.report import Fix

__all__ = ["apply_fixes"]

_FIXERS = {
    "openai": openai.fix,
    "anthropic": anthropic.fix,
    "gemini": gemini.fix,
}


def apply_fixes(data: dict, path: str = "<unknown>") -> list[Fix]:
    """Mutate `data` in place, applying every fix that's safe to apply
    without guessing at prompt-authoring intent. Returns what changed.

    Not every portability finding has a corresponding fix here -- see
    `fixers/openai.py`, `fixers/anthropic.py`, `fixers/gemini.py` for what's
    covered per provider shape, and the README for why the rest are
    left for a human (rewriting prompt text or inventing a role name is a
    content decision, not a mechanical rewrite).
    """
    provider = detect_provider(data)
    return _FIXERS[provider](data, path)
