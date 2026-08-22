from llm_prompt_lint.model import PromptDoc
from llm_prompt_lint.report import Finding

RULE_ID = "stop-sequences"

# OpenAI's Chat Completions API caps `stop` at 4 sequences; Anthropic has no
# such documented cap. A prompt authored against Anthropic (or a generic
# template) can silently exceed OpenAI's limit if ported without review.
OPENAI_MAX_STOP_SEQUENCES = 4


def check(doc: PromptDoc) -> list[Finding]:
    if len(doc.stop) > OPENAI_MAX_STOP_SEQUENCES:
        return [
            Finding(
                rule_id=RULE_ID,
                severity="error",
                message=(
                    f"{len(doc.stop)} stop sequences configured, exceeding OpenAI's "
                    f"{OPENAI_MAX_STOP_SEQUENCES}-sequence limit -- this request will be "
                    "rejected if ported to OpenAI as-is"
                ),
                path=doc.source_path,
            )
        ]
    return []
