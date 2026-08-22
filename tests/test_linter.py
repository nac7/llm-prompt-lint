from llm_prompt_lint.linter import lint
from llm_prompt_lint.model import Message, PromptDoc


def test_clean_doc_produces_no_findings():
    doc = PromptDoc(
        system="You are a helpful assistant.",
        messages=[Message(role="user", content="Hello")],
        temperature=0.7,
        stop=["END"],
        source_path="clean.json",
    )
    report = lint(doc)
    assert report.findings == []
    assert report.has_errors is False


def test_findings_aggregate_across_rules():
    doc = PromptDoc(
        system="You are ChatGPT.",  # hardcoded-provider-reference
        stop=["a", "b", "c", "d", "e"],  # stop-sequences (error)
        temperature=1.9,  # temperature-range
        source_path="messy.json",
    )
    report = lint(doc)
    rule_ids = {f.rule_id for f in report.findings}
    assert "hardcoded-provider-reference" in rule_ids
    assert "stop-sequences" in rule_ids
    assert "temperature-range" in rule_ids
    assert report.has_errors is True  # stop-sequences is an error


def test_report_table_and_json_render():
    doc = PromptDoc(system="You are ChatGPT.", source_path="x.json")
    report = lint(doc)
    assert "x.json" in report.to_table()
    assert "hardcoded-provider-reference" in report.to_json()
