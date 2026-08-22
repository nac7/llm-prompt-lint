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


def test_check_reports_non_utf8_file_cleanly(tmp_path):
    path = tmp_path / "bad_encoding.json"
    path.write_bytes(b"\xff\xfe\x00{not valid utf-8")
    with pytest.raises(SystemExit, match="could not read"):
        main(["check", str(path)])


def test_check_ignore_flag_suppresses_a_rule(tmp_path, capsys):
    path = _write(tmp_path, "bad.json", {"messages": [], "stop": ["a", "b", "c", "d", "e"]})
    exit_code = main(["check", path, "--ignore", "stop-sequences"])
    out = capsys.readouterr().out
    assert exit_code == 0
    assert "No portability issues found" in out


def test_check_ignore_flag_family_prefix(tmp_path, capsys):
    # A leading-but-blank system message only trips system-prompt/empty --
    # unlike an out-of-position one, it never touches doc.messages, so this
    # isolates the family-prefix match from unsupported-role's overlap.
    path = _write(
        tmp_path,
        "bad.json",
        {"messages": [{"role": "system", "content": "   "}, {"role": "user", "content": "hi"}]},
    )
    exit_code = main(["check", path, "--ignore", "system-prompt"])
    out = capsys.readouterr().out
    assert exit_code == 0
    assert "system-prompt" not in out


def test_check_config_file_suppresses_a_rule(tmp_path, capsys):
    config_path = tmp_path / ".prompt-portability.json"
    config_path.write_text(json.dumps({"ignore": ["stop-sequences"]}))
    path = _write(tmp_path, "bad.json", {"messages": [], "stop": ["a", "b", "c", "d", "e"]})

    exit_code = main(["check", path, "--config", str(config_path)])
    out = capsys.readouterr().out
    assert exit_code == 0
    assert "No portability issues found" in out


def test_check_ignore_flag_and_config_file_combine(tmp_path, capsys):
    config_path = tmp_path / ".prompt-portability.json"
    config_path.write_text(json.dumps({"ignore": ["stop-sequences"]}))
    path = _write(
        tmp_path,
        "bad.json",
        {"messages": [], "stop": ["a", "b", "c", "d", "e"], "temperature": 1.9},
    )

    exit_code = main(["check", path, "--config", str(config_path), "--ignore", "temperature-range"])
    out = capsys.readouterr().out
    assert exit_code == 0
    assert "No portability issues found" in out


def test_fix_ignore_flag_suppresses_remaining_finding(tmp_path, capsys):
    path = _write(tmp_path, "bad.json", {"messages": [], "temperature": 1.9})
    exit_code = main(["fix", path, "--ignore", "temperature-range"])
    out = capsys.readouterr().out
    assert exit_code == 0
    assert "No remaining portability issues." in out


def test_check_rejects_unknown_ignore_rule(tmp_path):
    path = _write(tmp_path, "clean.json", {"messages": [{"role": "user", "content": "hi"}]})
    with pytest.raises(SystemExit, match="unknown --ignore rule"):
        main(["check", path, "--ignore", "sytem-prompt"])


def test_fix_writes_corrected_file_and_reports_remaining_issues(tmp_path, capsys):
    path = _write(
        tmp_path,
        "messy.json",
        {
            "messages": [
                {"role": "user", "content": "hi"},
                {"role": "system", "content": "be terse"},
            ],
            "stop": ["a", "b", "c", "d", "e"],
            "temperature": 1.9,
        },
    )
    exit_code = main(["fix", path])
    out = capsys.readouterr().out
    assert "Applied" in out
    assert "system-prompt/merged" in out
    assert "stop-sequences" in out
    # temperature-range has no fixer, so it must survive into "remaining issues".
    assert "temperature-range" in out
    assert exit_code == 0  # remaining temperature-range finding is a warning, not an error

    with open(path, encoding="utf-8") as f:
        fixed = json.load(f)
    assert fixed["messages"][0] == {"role": "system", "content": "be terse"}
    assert fixed["stop"] == ["a", "b", "c", "d"]


def test_fix_dry_run_does_not_write_the_file(tmp_path, capsys):
    path = _write(tmp_path, "messy.json", {"messages": [], "stop": ["a", "b", "c", "d", "e"]})
    with open(path, encoding="utf-8") as f:
        original_text = f.read()

    main(["fix", path, "--dry-run"])
    out = capsys.readouterr().out
    assert "Would apply" in out

    with open(path, encoding="utf-8") as f:
        assert f.read() == original_text


def test_fix_reports_clean_file_with_no_fixes(tmp_path, capsys):
    path = _write(
        tmp_path,
        "clean.json",
        {"messages": [{"role": "user", "content": "hi"}]},
    )
    exit_code = main(["fix", path])
    out = capsys.readouterr().out
    assert "Applied 0 fix(es)" in out
    assert "No remaining portability issues." in out
    assert exit_code == 0
