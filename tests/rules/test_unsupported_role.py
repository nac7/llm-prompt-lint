from llm_prompt_lint.model import Message, PromptDoc
from llm_prompt_lint.rules.unsupported_role import check


def test_portable_roles_not_flagged():
    doc = PromptDoc(
        messages=[Message(role="user", content="hi"), Message(role="tool", content="x")]
    )
    assert check(doc) == []


def test_legacy_function_role_flagged_as_warning():
    doc = PromptDoc(messages=[Message(role="function", content="{}")])
    findings = check(doc)
    assert len(findings) == 1
    assert findings[0].severity == "warning"
    assert findings[0].rule_id == "unsupported-role/legacy-function"


def test_unknown_role_flagged_as_error():
    doc = PromptDoc(messages=[Message(role="narrator", content="hi")])
    findings = check(doc)
    assert len(findings) == 1
    assert findings[0].severity == "error"
