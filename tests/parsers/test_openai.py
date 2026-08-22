from llm_prompt_lint.parsers.openai import parse_openai_chat_completion


def test_splits_leading_system_message_out_of_messages():
    data = {
        "messages": [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Hi"},
        ]
    }
    doc = parse_openai_chat_completion(data)
    assert doc.system == "You are helpful."
    assert [m.role for m in doc.messages] == ["user"]


def test_non_leading_system_message_stays_in_messages():
    data = {
        "messages": [
            {"role": "user", "content": "Hi"},
            {"role": "system", "content": "Actually, be terse."},
        ]
    }
    doc = parse_openai_chat_completion(data)
    assert doc.system is None
    assert [m.role for m in doc.messages] == ["user", "system"]


def test_stop_string_is_wrapped_in_a_list():
    data = {"messages": [], "stop": "STOP"}
    doc = parse_openai_chat_completion(data)
    assert doc.stop == ["STOP"]


def test_extracts_tool_function_shape():
    data = {
        "messages": [],
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get the weather",
                    "parameters": {"type": "object", "properties": {}},
                },
            }
        ],
    }
    doc = parse_openai_chat_completion(data)
    assert len(doc.tools) == 1
    assert doc.tools[0].name == "get_weather"


def test_extracts_json_object_response_format():
    data = {"messages": [], "response_format": {"type": "json_object"}}
    doc = parse_openai_chat_completion(data)
    assert doc.response_format == "json_object"


def test_multipart_content_is_joined_to_text():
    data = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this:"},
                    {"type": "image_url", "image_url": {"url": "https://example.com/x.png"}},
                ],
            }
        ]
    }
    doc = parse_openai_chat_completion(data)
    assert doc.messages[0].content == "Describe this:"
