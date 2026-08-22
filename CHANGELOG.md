# Changelog

All notable changes to this project are documented in this file.

## [0.1.0] - 2026-08-22

Initial release.

### Added
- Parsers normalizing OpenAI Chat Completions, Anthropic Messages API, and Google Gemini `generateContent` request bodies into one provider-agnostic `PromptDoc` model, with format auto-detection (`llm_prompt_lint.parsers.detect_and_parse`). Gemini's `model`/`function` roles are normalized to the portable `assistant`/`tool` roles, and its `generationConfig` (temperature, topP, stopSequences, responseMimeType) into the shared `PromptDoc` fields, so every rule applies to all three providers.
- 10 portability rules: system-prompt placement/duplication/emptiness, OpenAI's 4-stop-sequence limit, temperature range mismatches across providers, hardcoded provider/model identity in prompt text, leaked chat-template tokens from other model families (ChatML, Llama `[INST]`, Llama 2 `<<SYS>>`, Gemma), the deprecated OpenAI `function` role, non-portable message roles, and OpenAI's json-mode "must mention json" requirement.
- `check` CLI command: lints one or more JSON files (or globs), table or `--json` output, exits non-zero on any error-severity finding for CI gating. Fails cleanly (naming the file) on unreadable JSON or a JSON value that isn't an object.
- CI: test matrix across 3 OSes x 3 Python versions, plus a lint/type-check job (ruff + mypy).
- 51 tests passing.
