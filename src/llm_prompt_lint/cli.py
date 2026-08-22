from __future__ import annotations

import argparse
import glob
import json
import sys

from llm_prompt_lint.config import DEFAULT_CONFIG_PATH, is_ignored, load_ignore_config
from llm_prompt_lint.fixers import apply_fixes
from llm_prompt_lint.linter import lint
from llm_prompt_lint.parsers import detect_and_parse
from llm_prompt_lint.report import Finding, Fix, LintReport


def _expand_paths(patterns: list[str]) -> list[str]:
    paths: list[str] = []
    for pattern in patterns:
        matches = sorted(glob.glob(pattern, recursive=True))
        paths.extend(matches or [pattern])
    return paths


def _load_request(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SystemExit(f"prompt-portability: could not read {path} as JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise SystemExit(
            f"prompt-portability: {path} is not a JSON object -- expected an OpenAI, "
            "Anthropic, or Gemini chat-completion request body"
        )
    return data


def _resolve_ignore(args: argparse.Namespace) -> list[str]:
    return load_ignore_config(args.config) + (args.ignore or [])


def _check(args: argparse.Namespace) -> int:
    ignore = _resolve_ignore(args)
    all_findings: list[Finding] = []
    for path in _expand_paths(args.paths):
        data = _load_request(path)
        doc = detect_and_parse(data, source_path=path)
        findings = [f for f in lint(doc).findings if not is_ignored(f.rule_id, ignore)]
        all_findings.extend(findings)

    report = LintReport(findings=all_findings)
    print(report.to_json() if args.json else report.to_table())
    return 1 if report.has_errors else 0


def _fix(args: argparse.Namespace) -> int:
    ignore = _resolve_ignore(args)
    all_fixes: list[Fix] = []
    all_remaining: list[Finding] = []

    for path in _expand_paths(args.paths):
        data = _load_request(path)
        fixes = apply_fixes(data, path=path)
        all_fixes.extend(fixes)

        doc = detect_and_parse(data, source_path=path)
        remaining = [f for f in lint(doc).findings if not is_ignored(f.rule_id, ignore)]
        all_remaining.extend(remaining)

        if fixes and not args.dry_run:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
                f.write("\n")

    verb = "Would apply" if args.dry_run else "Applied"
    print(f"{verb} {len(all_fixes)} fix(es)")
    for applied in all_fixes:
        note = " (needs manual follow-up)" if applied.needs_manual_followup else ""
        print(f"  [{applied.path}] {applied.rule_id}: {applied.message}{note}")

    report = LintReport(findings=all_remaining)
    print()
    if all_remaining:
        print("Remaining issues:")
        print(report.to_json() if args.json else report.to_table())
    else:
        print("No remaining portability issues.")

    return 1 if report.has_errors else 0


def _add_ignore_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--ignore",
        action="append",
        metavar="RULE_ID",
        help="Suppress a rule (repeatable). A bare family name (e.g. 'system-prompt') "
        "suppresses every rule in that family.",
    )
    parser.add_argument(
        "--config",
        default=DEFAULT_CONFIG_PATH,
        help=f'Path to a {{"ignore": [<rule-id>, ...]}} JSON config file '
        f"(default: {DEFAULT_CONFIG_PATH} in the current directory, if present)",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="prompt-portability")
    sub = parser.add_subparsers(dest="command", required=True)

    check_p = sub.add_parser(
        "check",
        help="Lint one or more prompt request JSON files for cross-provider portability",
    )
    check_p.add_argument(
        "paths", nargs="+", help="Path(s) or glob(s) to OpenAI/Anthropic/Gemini request JSON files"
    )
    check_p.add_argument("--json", action="store_true", help="Output JSON instead of a table")
    _add_ignore_args(check_p)
    check_p.set_defaults(func=_check)

    fix_p = sub.add_parser(
        "fix",
        help="Auto-fix the portability issues that have an unambiguous, lossless rewrite",
    )
    fix_p.add_argument(
        "paths", nargs="+", help="Path(s) or glob(s) to OpenAI/Anthropic/Gemini request JSON files"
    )
    fix_p.add_argument(
        "--dry-run", action="store_true", help="Show what would change without writing files"
    )
    fix_p.add_argument(
        "--json", action="store_true", help="Output remaining issues as JSON instead of a table"
    )
    _add_ignore_args(fix_p)
    fix_p.set_defaults(func=_fix)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
