# llm-prompt-lint

[![CI](https://github.com/nac7/llm-prompt-lint/actions/workflows/ci.yml/badge.svg)](https://github.com/nac7/llm-prompt-lint/actions/workflows/ci.yml)

Lint LLM chat-completion prompts for cross-provider portability issues.

A prompt authored and tuned against one provider's API often breaks --
silently, or with a rejected request -- when the same request body is sent
to another. `llm-prompt-lint` reads OpenAI- or Anthropic-shaped request JSON
and flags the assumptions that don't travel: system-prompt placement,
provider-specific limits (stop-sequence counts, temperature ranges), leaked
chat-template tokens from a different model family, deprecated/nonstandard
message roles, and JSON-mode footguns.

## Quickstart

```bash
pip install llm-prompt-lint

llm-prompt-lint check prompts/*.json
```

Exits non-zero if any finding is error-severity, so it's usable as a CI gate.
Add `--json` for machine-readable output.

## What it checks (v0.1.0)

| Rule | Severity | Catches |
|---|---|---|
| `system-prompt/not-first` | error | A `system`-role message appears mid-conversation instead of first/dedicated |
| `system-prompt/multiple` | warning | More than one inline system-role message |
| `system-prompt/empty` | warning | A present-but-blank system prompt |
| `stop-sequences` | error | More than 4 stop sequences (OpenAI's hard limit) |
| `temperature-range` | warning | `temperature > 1.0` (valid on OpenAI's 0-2 scale, out of range elsewhere) |
| `hardcoded-provider-reference` | warning | Prompt text says "you are ChatGPT/Claude/Gemini" etc. |
| `leaked-special-tokens` | error | Literal `<\|im_start\|>`, `[INST]`, `<<SYS>>`, `<start_of_turn>` in message content |
| `unsupported-role/legacy-function` | warning | OpenAI's deprecated `function` role instead of `tool` |
| `unsupported-role` | error | A message role outside `{user, assistant, tool}` |
| `json-mode-missing-hint` | warning | `response_format: json_object` with no message mentioning "json" |

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

## Library API

```python
from llm_prompt_lint.parsers import detect_and_parse
from llm_prompt_lint.linter import lint

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
JSON/table CLI output; CI across 3 OSes x 3 Python versions plus a
lint/type-check job.

Known gap: rules operate on a single request snapshot, not a stored prompt
template with variable substitution.

## License

MIT
