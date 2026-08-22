# Changelog

All notable changes to this project are documented in this file.

## [Unreleased]

### Added
- Google Gemini `generateContent` request parser (`llm_prompt_lint.parsers.gemini`), auto-detected via the `contents` field. Normalizes Gemini's `model`/`function` roles to the portable `assistant`/`tool` roles, and `generationConfig` (temperature, topP, stopSequences, responseMimeType) into the shared `PromptDoc` fields, so all 10 rules apply to it unchanged.

### Fixed
- A JSON file that parses but isn't an object (e.g. a bare array) used to crash with a raw `AttributeError`; `check` now exits cleanly naming the file.

## [0.1.0] - 2026-08-22

Initial release.

### Added
- Parsers normalizing OpenAI Chat Completions and Anthropic Messages API request bodies into one provider-agnostic `PromptDoc` model, with format auto-detection (`llm_prompt_lint.parsers.detect_and_parse`).
- 10 portability rules: system-prompt placement/duplication/emptiness, OpenAI's 4-stop-sequence limit, temperature range mismatches across providers, hardcoded provider/model identity in prompt text, leaked chat-template tokens from other model families (ChatML, Llama `[INST]`, Llama 2 `<<SYS>>`, Gemma), the deprecated OpenAI `function` role, non-portable message roles, and OpenAI's json-mode "must mention json" requirement.
- `check` CLI command: lints one or more JSON files (or globs), table or `--json` output, exits non-zero on any error-severity finding for CI gating.
- CI: test matrix across 3 OSes x 3 Python versions, plus a lint/type-check job (ruff + mypy).
- 44 tests passing.
