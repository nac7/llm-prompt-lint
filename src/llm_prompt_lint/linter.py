from llm_prompt_lint.model import PromptDoc
from llm_prompt_lint.report import Finding, LintReport
from llm_prompt_lint.rules import ALL_RULES


def lint(doc: PromptDoc) -> LintReport:
    findings: list[Finding] = []
    for rule in ALL_RULES:
        findings.extend(rule(doc))
    return LintReport(findings=findings)
