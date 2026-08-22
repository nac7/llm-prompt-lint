from llm_prompt_lint.fixers.gemini import fix


def test_moves_system_role_content_into_system_instruction():
    data = {
        "contents": [
            {"role": "system", "parts": [{"text": "Be helpful."}]},
            {"role": "user", "parts": [{"text": "hi"}]},
        ]
    }
    fixes = fix(data)
    assert any(f.rule_id == "system-prompt/merged" for f in fixes)
    assert data["systemInstruction"] == {"parts": [{"text": "Be helpful."}]}
    assert data["contents"] == [{"role": "user", "parts": [{"text": "hi"}]}]


def test_no_system_role_content_is_a_noop():
    data = {"contents": [{"role": "user", "parts": [{"text": "hi"}]}]}
    assert fix(data) == []


def test_drops_empty_system_instruction():
    data = {"systemInstruction": {"parts": [{"text": "   "}]}, "contents": []}
    fixes = fix(data)
    assert any(f.rule_id == "system-prompt/empty" for f in fixes)
    assert "systemInstruction" not in data


def test_strips_leaked_tokens_from_contents():
    data = {"contents": [{"role": "user", "parts": [{"text": "<start_of_turn>hi<end_of_turn>"}]}]}
    fixes = fix(data)
    assert any(f.rule_id == "leaked-special-tokens" for f in fixes)
    assert "<start_of_turn>" not in data["contents"][0]["parts"][0]["text"]


def test_truncates_stop_sequences_in_generation_config():
    data = {"contents": [], "generationConfig": {"stopSequences": ["a", "b", "c", "d", "e"]}}
    fixes = fix(data)
    assert any(f.rule_id == "stop-sequences" for f in fixes)
    assert data["generationConfig"]["stopSequences"] == ["a", "b", "c", "d"]
