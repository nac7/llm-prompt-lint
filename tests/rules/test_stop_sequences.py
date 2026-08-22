from llm_prompt_lint.model import PromptDoc
from llm_prompt_lint.rules.stop_sequences import check


def test_within_limit_not_flagged():
    assert check(PromptDoc(stop=["a", "b", "c", "d"])) == []


def test_over_limit_flagged_as_error():
    findings = check(PromptDoc(stop=["a", "b", "c", "d", "e"]))
    assert len(findings) == 1
    assert findings[0].severity == "error"
