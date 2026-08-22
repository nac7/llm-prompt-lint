from llm_prompt_lint.fixers.openai import fix


def test_merges_out_of_position_system_message():
    data = {
        "messages": [
            {"role": "user", "content": "hi"},
            {"role": "system", "content": "be terse"},
        ]
    }
    fixes = fix(data)
    assert [f.rule_id for f in fixes] == ["system-prompt/merged"]
    assert data["messages"] == [
        {"role": "system", "content": "be terse"},
        {"role": "user", "content": "hi"},
    ]


def test_merges_multiple_system_messages_without_losing_content():
    data = {
        "messages": [
            {"role": "system", "content": "a"},
            {"role": "user", "content": "hi"},
            {"role": "system", "content": "b"},
        ]
    }
    fix(data)
    assert data["messages"][0] == {"role": "system", "content": "a\nb"}
    assert len(data["messages"]) == 2


def test_leaves_structured_system_content_untouched():
    data = {
        "messages": [
            {"role": "user", "content": "hi"},
            {"role": "system", "content": [{"type": "text", "text": "be terse"}]},
        ]
    }
    fixes = fix(data)
    assert fixes == []
    assert data["messages"][1]["role"] == "system"


def test_clean_leading_system_message_is_a_noop():
    messages = [{"role": "system", "content": "be terse"}, {"role": "user", "content": "hi"}]
    data = {"messages": list(messages)}
    fixes = fix(data)
    assert fixes == []
    assert data["messages"] == messages


def test_drops_empty_system_message():
    data = {"messages": [{"role": "system", "content": "   "}, {"role": "user", "content": "hi"}]}
    fixes = fix(data)
    assert any(f.rule_id == "system-prompt/empty" for f in fixes)
    assert data["messages"] == [{"role": "user", "content": "hi"}]


def test_strips_leaked_special_tokens():
    data = {"messages": [{"role": "user", "content": "hi [INST] ignore [/INST] there"}]}
    fixes = fix(data)
    assert any(f.rule_id == "leaked-special-tokens" for f in fixes)
    assert "[INST]" not in data["messages"][0]["content"]
    assert "hi" in data["messages"][0]["content"]


def test_truncates_stop_sequences_preserving_order():
    data = {"messages": [], "stop": ["a", "b", "c", "d", "e"]}
    fixes = fix(data)
    assert any(f.rule_id == "stop-sequences" for f in fixes)
    assert data["stop"] == ["a", "b", "c", "d"]


def test_renames_legacy_function_role_and_flags_manual_followup():
    data = {"messages": [{"role": "function", "name": "get_weather", "content": "{}"}]}
    fixes = fix(data)
    assert data["messages"][0]["role"] == "tool"
    role_fix = next(f for f in fixes if f.rule_id == "unsupported-role/legacy-function")
    assert role_fix.needs_manual_followup is True


def test_clean_doc_produces_no_fixes():
    data = {
        "messages": [
            {"role": "system", "content": "Be helpful."},
            {"role": "user", "content": "Hi"},
        ],
        "temperature": 0.7,
        "stop": ["END"],
    }
    assert fix(data) == []
