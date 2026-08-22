from llm_prompt_lint.model import PromptDoc
from llm_prompt_lint.rules.temperature import check


def test_none_not_flagged():
    assert check(PromptDoc(temperature=None)) == []


def test_within_portable_range_not_flagged():
    assert check(PromptDoc(temperature=0.7)) == []


def test_above_portable_range_flagged():
    findings = check(PromptDoc(temperature=1.5))
    assert len(findings) == 1
    assert findings[0].severity == "warning"
