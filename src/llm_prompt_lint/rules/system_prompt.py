from llm_prompt_lint.model import PromptDoc
from llm_prompt_lint.report import Finding

RULE_ID = "system-prompt"


def check(doc: PromptDoc) -> list[Finding]:
    findings = []

    if doc.system is not None and doc.system.strip() == "":
        findings.append(
            Finding(
                rule_id=f"{RULE_ID}/empty",
                severity="warning",
                message="system prompt is present but empty -- likely accidental",
                path=doc.source_path,
            )
        )

    inline_system = [i for i, m in enumerate(doc.messages) if m.role == "system"]
    if inline_system and inline_system[0] != 0:
        findings.append(
            Finding(
                rule_id=f"{RULE_ID}/not-first",
                severity="error",
                message=(
                    "a system-role message appears mid-conversation -- providers that "
                    "require a single leading system turn (or a dedicated system field, "
                    "like Anthropic) will reject or silently reorder this"
                ),
                path=doc.source_path,
            )
        )
    if len(inline_system) > 1:
        findings.append(
            Finding(
                rule_id=f"{RULE_ID}/multiple",
                severity="warning",
                message=(
                    f"{len(inline_system)} system-role messages found -- only the first "
                    "is portable to providers that accept a single system instruction"
                ),
                path=doc.source_path,
            )
        )

    return findings
