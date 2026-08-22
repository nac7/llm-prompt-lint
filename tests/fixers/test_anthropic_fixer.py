from llm_prompt_lint.fixers.anthropic import fix


def test_moves_inline_system_role_message_into_system_field():
    data = {
        "system": "Be helpful.",
        "messages": [
            {"role": "system", "content": "Also be terse."},
            {"role": "user", "content": "hi"},
        ],
    }
    fixes = fix(data)
    assert any(f.rule_id == "system-prompt/merged" for f in fixes)
    assert data["system"] == "Be helpful.\nAlso be terse."
    assert data["messages"] == [{"role": "user", "content": "hi"}]


def test_no_inline_system_messages_is_a_noop():
    data = {"system": "Be helpful.", "messages": [{"role": "user", "content": "hi"}]}
    assert fix(data) == []


def test_drops_empty_system_field():
    data = {"system": "   ", "messages": []}
    fixes = fix(data)
    assert any(f.rule_id == "system-prompt/empty" for f in fixes)
    assert "system" not in data


def test_strips_leaked_tokens_from_system_and_messages():
    data = {
        "system": "<<SYS>>be helpful<</SYS>>",
        "messages": [{"role": "user", "content": "hi"}],
    }
    fixes = fix(data)
    assert any(f.rule_id == "leaked-special-tokens" for f in fixes)
    assert "<<SYS>>" not in data["system"]


def test_truncates_stop_sequences():
    data = {"messages": [], "stop_sequences": ["a", "b", "c", "d", "e"]}
    fixes = fix(data)
    assert any(f.rule_id == "stop-sequences" for f in fixes)
    assert data["stop_sequences"] == ["a", "b", "c", "d"]
