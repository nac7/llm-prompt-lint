from llm_prompt_lint.parsers.anthropic import parse_anthropic_messages


def test_top_level_system_field_is_used_directly():
    data = {
        "system": "You are helpful.",
        "messages": [{"role": "user", "content": "Hi"}],
    }
    doc = parse_anthropic_messages(data)
    assert doc.system == "You are helpful."
    assert [m.role for m in doc.messages] == ["user"]


def test_structured_system_blocks_are_joined_to_text():
    data = {
        "system": [{"type": "text", "text": "Be terse."}],
        "messages": [],
    }
    doc = parse_anthropic_messages(data)
    assert doc.system == "Be terse."


def test_stop_sequences_field_is_used():
    data = {"messages": [], "stop_sequences": ["END", "STOP"]}
    doc = parse_anthropic_messages(data)
    assert doc.stop == ["END", "STOP"]


def test_extracts_tool_input_schema_shape():
    data = {
        "messages": [],
        "tools": [
            {
                "name": "get_weather",
                "description": "Get the weather",
                "input_schema": {"type": "object", "properties": {}},
            }
        ],
    }
    doc = parse_anthropic_messages(data)
    assert len(doc.tools) == 1
    assert doc.tools[0].name == "get_weather"
    assert doc.tools[0].parameters == {"type": "object", "properties": {}}
