from llm_prompt_lint.model import PromptDoc
from llm_prompt_lint.report import Finding

RULE_ID = "unsupported-role"

# The role names portable across OpenAI's and Anthropic's chat APIs.
# "function" is OpenAI's now-legacy pre-tools role name -- flagged
# separately below with a more specific message, not just "unknown".
PORTABLE_ROLES = {"user", "assistant", "tool"}


def check(doc: PromptDoc) -> list[Finding]:
    findings = []
    for m in doc.messages:
        if m.role == "function":
            findings.append(
                Finding(
                    rule_id=f"{RULE_ID}/legacy-function",
                    severity="warning",
                    message=(
                        "role 'function' is OpenAI's deprecated pre-tools message role -- "
                        "use 'tool' (with a tool_call_id) for portability"
                    ),
                    path=doc.source_path,
                )
            )
        elif m.role not in PORTABLE_ROLES:
            findings.append(
                Finding(
                    rule_id=RULE_ID,
                    severity="error",
                    message=f"role {m.role!r} is not a portable message role",
                    path=doc.source_path,
                )
            )
    return findings
