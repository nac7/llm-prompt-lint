from llm_prompt_lint.model import Message, PromptDoc
from llm_prompt_lint.rules.hardcoded_provider import check


def test_flags_you_are_chatgpt():
    doc = PromptDoc(system="You are ChatGPT, a large language model.")
    findings = check(doc)
    assert len(findings) == 1
    assert findings[0].severity == "warning"


def test_flags_you_are_claude_in_a_message():
    doc = PromptDoc(messages=[Message(role="user", content="Remember, you are Claude.")])
    assert len(check(doc)) == 1


def test_generic_system_prompt_not_flagged():
    doc = PromptDoc(system="You are a helpful assistant that answers concisely.")
    assert check(doc) == []
