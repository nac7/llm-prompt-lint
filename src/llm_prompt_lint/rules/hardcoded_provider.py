import re

from llm_prompt_lint.model import PromptDoc
from llm_prompt_lint.report import Finding

RULE_ID = "hardcoded-provider-reference"

# Phrases that bake a specific provider/model identity into the prompt text
# itself, rather than leaving it to the API's model selection -- these read
# oddly (or wrongly) once the same prompt is sent to a different provider.
_PATTERNS = [
    re.compile(r"\byou are (chatgpt|gpt-3|gpt-4|gpt-5)\b", re.IGNORECASE),
    re.compile(r"\byou are claude\b", re.IGNORECASE),
    re.compile(r"\byou are gemini\b", re.IGNORECASE),
    re.compile(r"\bas an? (openai|anthropic|google) (model|ai|assistant)\b", re.IGNORECASE),
]


def check(doc: PromptDoc) -> list[Finding]:
    findings = []
    texts = [("system", doc.system)] if doc.system else []
    texts += [(m.role, m.content) for m in doc.messages]

    for role, text in texts:
        for pattern in _PATTERNS:
            match = pattern.search(text)
            if match:
                findings.append(
                    Finding(
                        rule_id=RULE_ID,
                        severity="warning",
                        message=(
                            f"{role} message hardcodes a provider/model identity "
                            f"({match.group(0)!r}) -- misleading or wrong once this "
                            "prompt is sent to a different provider"
                        ),
                        path=doc.source_path,
                    )
                )
    return findings
