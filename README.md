# prompt-portability

[![CI](https://github.com/nac7/prompt-portability/actions/workflows/ci.yml/badge.svg)](https://github.com/nac7/prompt-portability/actions/workflows/ci.yml)

Lint LLM chat-completion prompts for cross-provider portability issues.

A prompt authored and tuned against one provider's API often breaks --
silently, or with a rejected request -- when the same request body is sent
to another. `prompt-portability` reads OpenAI- or Anthropic-shaped request JSON
and flags the assumptions that don't travel: system-prompt placement,
provider-specific limits (stop-sequence counts, temperature ranges), leaked
chat-template tokens from a different model family, deprecated/nonstandard
message roles, and JSON-mode footguns.

## Quickstart

```bash
pip install prompt-portability

prompt-portability check prompts/*.json
```

Exits non-zero if any finding is error-severity, so it's usable as a CI gate.
Add `--json` for machine-readable output.

`check` only detects issues. To resolve the ones that have an unambiguous,
lossless rewrite -- rather than requiring a human judgment call -- run:

```bash
prompt-portability fix prompts/*.json
```

`fix` rewrites the file(s) in place and prints what changed, followed by
whatever findings remain (still exits non-zero if any of those are
error-severity). Add `--dry-run` to preview without writing.

## Suppressing a rule

A known, intentional case (e.g. a deliberately high `temperature`) doesn't
have to fail CI. Suppress it per-invocation:

```bash
prompt-portability check prompts/*.json --ignore temperature-range
```

or check it in so the whole team gets it, via a `.prompt-portability.json` file
(looked up in the current directory by default; `--config` to point
elsewhere) next to where you run the CLI:

```json
{"ignore": ["temperature-range"]}
```

`--ignore` is repeatable and stacks with the config file. A bare family
name (e.g. `"system-prompt"`) suppresses every rule in that family
(`system-prompt/empty`, `system-prompt/multiple`, etc). Suppression isn't
embedded in the request JSON itself, since those files are meant to double
as real API request bodies -- an extra top-level key risks a provider that
rejects unknown fields.

## What it checks (v0.1.0)

| Rule | Severity | Catches | `fix`? |
|---|---|---|---|
| `system-prompt/not-first` | error | A `system`-role message appears mid-conversation instead of first/dedicated | yes -- merged into the leading/dedicated system field |
| `system-prompt/multiple` | warning | More than one inline system-role message | yes -- merged (nothing dropped) |
| `system-prompt/empty` | warning | A present-but-blank system prompt | yes -- removed |
| `stop-sequences` | error | More than 4 stop sequences (OpenAI's hard limit) | yes -- truncated to 4, order-preserved |
| `temperature-range` | warning | `temperature > 1.0` (valid on OpenAI's 0-2 scale, out of range elsewhere) | no -- clamping changes sampling behavior |
| `hardcoded-provider-reference` | warning | Prompt text says "you are ChatGPT/Claude/Gemini" etc. | no -- rewriting authored text is a content decision |
| `leaked-special-tokens` | error | Literal `<\|im_start\|>`, `[INST]`, `<<SYS>>`, `<start_of_turn>` in message content | yes -- stripped |
| `unsupported-role/legacy-function` | warning | OpenAI's deprecated `function` role instead of `tool` | partial -- renamed, but you must add a `tool_call_id` by hand |
| `unsupported-role` | error | A message role outside `{user, assistant, tool}` | no -- no way to infer the intended portable role |
| `json-mode-missing-hint` | warning | `response_format: json_object` with no message mentioning "json" | no -- injecting text changes the actual instructions |

`fix` only touches the rows marked `yes`/`partial` above -- see
[Auto-fixing](#auto-fixing-fix) for why the rest are left to a human.

## Input format

Point `check` at JSON files shaped like an OpenAI Chat Completions request
body, an Anthropic Messages API request body, or a Google Gemini
`generateContent` request body -- the format is auto-detected per file
(`llm_prompt_lint.parsers.detect_and_parse`). All three shapes are
normalized to one provider-agnostic model before rules run, so every rule
applies to all three.

```json
{
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hi"}
  ],
  "temperature": 0.7,
  "stop": ["END"]
}
```

## Auto-fixing (`fix`)

Only findings with an unambiguous, lossless rewrite are auto-fixed --
deliberately not all 10 rules. Merging duplicate system messages, dropping
an empty one, stripping a leaked template token, and truncating excess stop
sequences are mechanical: nothing about the fix depends on guessing what
the prompt author meant. Renaming OpenAI's legacy `function` role to `tool`
is applied but flagged for manual follow-up, since a valid `tool` message
also needs a `tool_call_id` that can't be inferred.

The other three rules are left alone on purpose: clamping `temperature`
changes actual sampling behavior, rewriting "you are ChatGPT" requires
knowing what the author intended instead, and injecting the word "json"
to satisfy OpenAI's json-mode requirement changes the model's actual
instructions. Those are content decisions, not syntax fixes -- `fix`
reports them as remaining issues rather than guessing.

## Library API

```python
from llm_prompt_lint.parsers import detect_and_parse
from llm_prompt_lint.linter import lint
from llm_prompt_lint.fixers import apply_fixes

fixes = apply_fixes(request_body, path="prompts/greet.json")  # mutates in place

doc = detect_and_parse(request_body, source_path="prompts/greet.json")
report = lint(doc)
print(report.to_table())
```

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check .
mypy
```

## Status

v0.1.0. OpenAI + Anthropic + Gemini request parsers; 10 portability rules;
`check` (detect) and `fix` (auto-fix the 4-and-a-half safely-fixable ones,
`--dry-run` supported); per-rule suppression (`--ignore`, `.prompt-portability.json`);
JSON/table CLI output; CI across 3 OSes x 3 Python versions plus a
lint/type-check job. 86 tests passing.

Known gap: rules operate on a single request snapshot, not a stored prompt
template with variable substitution.

## License

MIT
