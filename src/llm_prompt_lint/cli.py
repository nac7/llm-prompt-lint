from __future__ import annotations

import argparse
import glob
import json
import sys

from llm_prompt_lint.linter import lint
from llm_prompt_lint.parsers import detect_and_parse
from llm_prompt_lint.report import Finding, LintReport


def _expand_paths(patterns: list[str]) -> list[str]:
    paths: list[str] = []
    for pattern in patterns:
        matches = sorted(glob.glob(pattern, recursive=True))
        paths.extend(matches or [pattern])
    return paths


def _check(args: argparse.Namespace) -> int:
    all_findings: list[Finding] = []
    for path in _expand_paths(args.paths):
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError) as exc:
            raise SystemExit(f"llm-prompt-lint: could not read {path} as JSON: {exc}") from exc

        if not isinstance(data, dict):
            raise SystemExit(
                f"llm-prompt-lint: {path} is not a JSON object -- expected an OpenAI, "
                "Anthropic, or Gemini chat-completion request body"
            )

        doc = detect_and_parse(data, source_path=path)
        all_findings.extend(lint(doc).findings)

    report = LintReport(findings=all_findings)
    print(report.to_json() if args.json else report.to_table())
    return 1 if report.has_errors else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="llm-prompt-lint")
    sub = parser.add_subparsers(dest="command", required=True)

    check_p = sub.add_parser(
        "check",
        help="Lint one or more prompt request JSON files for cross-provider portability",
    )
    check_p.add_argument(
        "paths", nargs="+", help="Path(s) or glob(s) to OpenAI/Anthropic request JSON files"
    )
    check_p.add_argument("--json", action="store_true", help="Output JSON instead of a table")
    check_p.set_defaults(func=_check)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
