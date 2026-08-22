from llm_prompt_lint.model import Message, PromptDoc
from llm_prompt_lint.rules.system_prompt import check


def test_empty_system_prompt_flagged():
    doc = PromptDoc(system="   ")
    findings = check(doc)
    assert any(f.rule_id == "system-prompt/empty" for f in findings)


def test_populated_system_prompt_not_flagged():
    doc = PromptDoc(system="Be helpful.")
    assert check(doc) == []


def test_system_message_not_first_is_an_error():
    doc = PromptDoc(
        messages=[
            Message(role="user", content="hi"),
            Message(role="system", content="be terse"),
        ]
    )
    findings = check(doc)
    assert any(f.rule_id == "system-prompt/not-first" and f.severity == "error" for f in findings)


def test_multiple_inline_system_messages_flagged():
    doc = PromptDoc(
        messages=[
            Message(role="system", content="a"),
            Message(role="system", content="b"),
        ]
    )
    findings = check(doc)
    assert any(f.rule_id == "system-prompt/multiple" for f in findings)
    # First-position system message shouldn't also trip the not-first rule.
    assert not any(f.rule_id == "system-prompt/not-first" for f in findings)


def test_clean_doc_has_no_findings():
    doc = PromptDoc(system="Be helpful.", messages=[Message(role="user", content="hi")])
    assert check(doc) == []
