import json

import pytest

from llm_prompt_lint.config import is_ignored, load_ignore_config


def test_missing_config_file_returns_empty_list(tmp_path):
    assert load_ignore_config(str(tmp_path / "nope.json")) == []


def test_loads_ignore_list_from_config_file(tmp_path):
    path = tmp_path / ".prompt-portability.json"
    path.write_text(json.dumps({"ignore": ["temperature-range", "system-prompt"]}))
    assert load_ignore_config(str(path)) == ["temperature-range", "system-prompt"]


def test_malformed_config_file_raises_clean_error(tmp_path):
    path = tmp_path / ".prompt-portability.json"
    path.write_text("{not valid json")
    with pytest.raises(SystemExit, match="could not read"):
        load_ignore_config(str(path))


def test_config_missing_ignore_key_defaults_to_empty_list(tmp_path):
    path = tmp_path / ".prompt-portability.json"
    path.write_text(json.dumps({"some_future_key": True}))
    assert load_ignore_config(str(path)) == []


def test_config_with_non_list_ignore_raises_clean_error(tmp_path):
    path = tmp_path / ".prompt-portability.json"
    path.write_text(json.dumps({"ignore": "not-a-list"}))
    with pytest.raises(SystemExit, match='"ignore"'):
        load_ignore_config(str(path))


def test_is_ignored_exact_match():
    assert is_ignored("temperature-range", ["temperature-range"]) is True
    assert is_ignored("stop-sequences", ["temperature-range"]) is False


def test_is_ignored_family_prefix_match():
    assert is_ignored("system-prompt/empty", ["system-prompt"]) is True
    assert is_ignored("system-prompt/multiple", ["system-prompt"]) is True
    assert is_ignored("system-promptx/empty", ["system-prompt"]) is False
