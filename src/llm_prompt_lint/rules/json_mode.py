from llm_prompt_lint.model import PromptDoc
from llm_prompt_lint.report import Finding

RULE_ID = "json-mode-missing-hint"


def check(doc: PromptDoc) -> list[Finding]:
    if doc.response_format != "json_object":
        return []

    texts = [doc.system or ""] + [m.content for m in doc.messages]
    if any("json" in t.lower() for t in texts):
        return []

    return [
        Finding(
            rule_id=RULE_ID,
            severity="warning",
            message=(
                "response_format is 'json_object' but no message mentions 'json' -- "
                "OpenAI's docs require the word 'json' to appear in the prompt for this "
                "mode to work reliably, and it silently degrades without it"
            ),
            path=doc.source_path,
        )
    ]
