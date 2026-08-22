import re

from llm_prompt_lint.model import PromptDoc
from llm_prompt_lint.report import Finding

RULE_ID = "leaked-special-tokens"

# Chat-template control tokens that belong to a specific provider/model
# family's own templating layer. If they show up literally inside message
# content, the prompt was likely authored/copied from a raw-template context
# (e.g. a Llama/ChatML fine-tuning example) and will confuse -- or simply
# render as garbage text in -- any other provider's chat API.
# Exported for reuse by llm_prompt_lint.fixers, which strips these same
# tokens rather than just flagging them.
PATTERNS = [
    re.compile(r"<\|im_start\|>|<\|im_end\|>"),  # ChatML (OpenAI-family fine-tunes)
    re.compile(r"\[INST\]|\[/INST\]"),  # Llama/Mistral instruction format
    re.compile(r"<<SYS>>|<</SYS>>"),  # Llama 2 system block
    re.compile(r"<start_of_turn>|<end_of_turn>"),  # Gemma
]


def check(doc: PromptDoc) -> list[Finding]:
    findings = []
    texts = [("system", doc.system)] if doc.system else []
    texts += [(m.role, m.content) for m in doc.messages]

    for role, text in texts:
        for pattern in PATTERNS:
            match = pattern.search(text)
            if match:
                findings.append(
                    Finding(
                        rule_id=RULE_ID,
                        severity="error",
                        message=(
                            f"{role} message contains a literal chat-template token "
                            f"({match.group(0)!r}) -- this belongs to one model family's "
                            "own templating and will not be interpreted by other providers"
                        ),
                        path=doc.source_path,
                    )
                )
    return findings
