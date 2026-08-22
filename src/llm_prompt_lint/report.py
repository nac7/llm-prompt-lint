import json
from dataclasses import asdict, dataclass, field

SEVERITY_ORDER = {"error": 0, "warning": 1, "info": 2}


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: str
    message: str
    path: str


@dataclass(frozen=True)
class LintReport:
    findings: list[Finding] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(f.severity == "error" for f in self.findings)

    def to_json(self) -> str:
        return json.dumps([asdict(f) for f in self.findings], indent=2)

    def to_table(self) -> str:
        if not self.findings:
            return "No portability issues found."
        ordered = sorted(self.findings, key=lambda f: (f.path, SEVERITY_ORDER[f.severity]))
        lines = []
        for f in ordered:
            lines.append(f"{f.path}: [{f.severity.upper()}] {f.rule_id}: {f.message}")
        return "\n".join(lines)
