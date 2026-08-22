import json

import pytest

from llm_prompt_lint.cli import main


def _write(tmp_path, name, data):
    path = tmp_path / name
    path.write_text(json.dumps(data))
    return str(path)


def test_check_returns_zero_for_clean_prompt(tmp_path, capsys):
    path = _write(
        tmp_path,
        "clean.json",
        {
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hi"},
            ],
            "temperature": 0.7,
        },
    )
    exit_code = main(["check", path])
    assert exit_code == 0
    assert "No portability issues found" in capsys.readouterr().out


def test_check_returns_one_for_error_finding(tmp_path, capsys):
    path = _write(
        tmp_path,
        "bad.json",
        {"messages": [], "stop": ["a", "b", "c", "d", "e"]},
    )
    exit_code = main(["check", path])
    assert exit_code == 1
    assert "stop-sequences" in capsys.readouterr().out


def test_check_json_output(tmp_path, capsys):
    path = _write(tmp_path, "bad.json", {"messages": [], "stop": ["a", "b", "c", "d", "e"]})
    main(["check", path, "--json"])
    out = capsys.readouterr().out
    parsed = json.loads(out)
    assert parsed[0]["rule_id"] == "stop-sequences"


def test_check_glob_lints_multiple_files(tmp_path, capsys):
    _write(tmp_path, "a.json", {"messages": [], "stop": ["a", "b", "c", "d", "e"]})
    _write(tmp_path, "b.json", {"messages": [{"role": "user", "content": "hi"}]})
    exit_code = main(["check", str(tmp_path / "*.json")])
    assert exit_code == 1
    out = capsys.readouterr().out
    assert "a.json" in out


def test_check_reports_unreadable_file_cleanly(tmp_path):
    path = tmp_path / "not_json.json"
    path.write_text("{not valid json")
    with pytest.raises(SystemExit, match="could not read"):
        main(["check", str(path)])


def test_check_reports_non_object_json_cleanly(tmp_path):
    path = _write(tmp_path, "list.json", ["not", "a", "request", "body"])
    with pytest.raises(SystemExit, match="not a JSON object"):
        main(["check", str(path)])
