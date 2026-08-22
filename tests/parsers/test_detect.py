from llm_prompt_lint.parsers import detect_and_parse


def test_detects_anthropic_via_stop_sequences():
    data = {"messages": [], "stop_sequences": ["END"]}
    doc = detect_and_parse(data)
    assert doc.stop == ["END"]  # would be [] if misrouted to the OpenAI parser


def test_detects_anthropic_via_input_schema_tool():
    data = {"messages": [], "tools": [{"name": "x", "input_schema": {}}]}
    doc = detect_and_parse(data)
    assert doc.tools[0].name == "x"


def test_defaults_to_openai():
    data = {"messages": [{"role": "system", "content": "Hi"}, {"role": "user", "content": "x"}]}
    doc = detect_and_parse(data)
    assert doc.system == "Hi"
