from llm_prompt_lint.model import PromptDoc
from llm_prompt_lint.report import Finding

RULE_ID = "temperature-range"

# OpenAI accepts temperature in [0, 2]; Anthropic and most other providers
# cap it at [0, 1]. A value above 1.0 is valid on OpenAI but out of range
# elsewhere.
PORTABLE_MAX_TEMPERATURE = 1.0


def check(doc: PromptDoc) -> list[Finding]:
    if doc.temperature is not None and doc.temperature > PORTABLE_MAX_TEMPERATURE:
        return [
            Finding(
                rule_id=RULE_ID,
                severity="warning",
                message=(
                    f"temperature={doc.temperature} is valid on OpenAI's 0-2 scale but "
                    f"exceeds the {PORTABLE_MAX_TEMPERATURE} cap most other providers "
                    "(e.g. Anthropic) enforce"
                ),
                path=doc.source_path,
            )
        ]
    return []
