from llm_prompt_lint.model import Message, PromptDoc
from llm_prompt_lint.rules.special_tokens import check


def test_flags_chatml_tokens():
    doc = PromptDoc(system="<|im_start|>system\nBe helpful<|im_end|>")
    findings = check(doc)
    assert len(findings) == 1
    assert findings[0].severity == "error"


def test_flags_llama_inst_tokens():
    doc = PromptDoc(messages=[Message(role="user", content="[INST] Hello [/INST]")])
    assert len(check(doc)) == 1


def test_clean_text_not_flagged():
    doc = PromptDoc(system="Be helpful and concise.")
    assert check(doc) == []
