from llm_prompt_lint.parsers.gemini import parse_gemini_generate_content


def test_system_instruction_and_model_role_mapping():
    data = {
        "systemInstruction": {"parts": [{"text": "You are helpful."}]},
        "contents": [
            {"role": "user", "parts": [{"text": "Hi"}]},
            {"role": "model", "parts": [{"text": "Hello!"}]},
        ],
    }
    doc = parse_gemini_generate_content(data)
    assert doc.system == "You are helpful."
    assert [m.role for m in doc.messages] == ["user", "assistant"]
    assert doc.messages[1].content == "Hello!"


def test_string_system_instruction_is_used_directly():
    data = {"systemInstruction": "Be terse.", "contents": []}
    doc = parse_gemini_generate_content(data)
    assert doc.system == "Be terse."


def test_generation_config_maps_to_portable_fields():
    data = {
        "contents": [],
        "generationConfig": {
            "temperature": 0.5,
            "topP": 0.9,
            "stopSequences": ["END"],
            "responseMimeType": "application/json",
        },
    }
    doc = parse_gemini_generate_content(data)
    assert doc.temperature == 0.5
    assert doc.top_p == 0.9
    assert doc.stop == ["END"]
    assert doc.response_format == "json_object"


def test_function_declarations_are_extracted_as_tools():
    data = {
        "contents": [],
        "tools": [
            {
                "functionDeclarations": [
                    {
                        "name": "get_weather",
                        "description": "Get the weather",
                        "parameters": {"type": "object", "properties": {}},
                    }
                ]
            }
        ],
    }
    doc = parse_gemini_generate_content(data)
    assert len(doc.tools) == 1
    assert doc.tools[0].name == "get_weather"


def test_function_role_maps_to_tool():
    data = {"contents": [{"role": "function", "parts": [{"text": "{}"}]}]}
    doc = parse_gemini_generate_content(data)
    assert doc.messages[0].role == "tool"
