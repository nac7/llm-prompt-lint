from llm_prompt_lint.model import Message, PromptDoc
from llm_prompt_lint.rules.json_mode import check


def test_not_json_mode_not_flagged():
    doc = PromptDoc(response_format=None, messages=[Message(role="user", content="hi")])
    assert check(doc) == []


def test_json_mode_without_word_json_flagged():
    doc = PromptDoc(response_format="json_object", messages=[Message(role="user", content="hi")])
    findings = check(doc)
    assert len(findings) == 1
    assert findings[0].severity == "warning"


def test_json_mode_with_word_json_in_system_not_flagged():
    doc = PromptDoc(
        response_format="json_object",
        system="Respond with valid JSON only.",
        messages=[Message(role="user", content="hi")],
    )
    assert check(doc) == []


def test_json_mode_with_word_json_in_message_not_flagged():
    doc = PromptDoc(
        response_format="json_object",
        messages=[Message(role="user", content="Reply in JSON.")],
    )
    assert check(doc) == []
