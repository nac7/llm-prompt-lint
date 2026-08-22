# Changelog

All notable changes to this project are documented in this file.

## [0.1.0] - 2026-08-22

Initial release.

### Added
- Parsers normalizing OpenAI Chat Completions, Anthropic Messages API, and Google Gemini `generateContent` request bodies into one provider-agnostic `PromptDoc` model, with format auto-detection (`llm_prompt_lint.parsers.detect_and_parse`). Gemini's `model`/`function` roles are normalized to the portable `assistant`/`tool` roles, and its `generationConfig` (temperature, topP, stopSequences, responseMimeType) into the shared `PromptDoc` fields, so every rule applies to all three providers.
- 10 portability rules: system-prompt placement/duplication/emptiness, OpenAI's 4-stop-sequence limit, temperature range mismatches across providers, hardcoded provider/model identity in prompt text, leaked chat-template tokens from other model families (ChatML, Llama `[INST]`, Llama 2 `<<SYS>>`, Gemma), the deprecated OpenAI `function` role, non-portable message roles, and OpenAI's json-mode "must mention json" requirement.
- `check` CLI command: lints one or more JSON files (or globs), table or `--json` output, exits non-zero on any error-severity finding for CI gating. Fails cleanly (naming the file) on unreadable JSON or a JSON value that isn't an object.
- `fix` CLI command: auto-fixes the findings that have an unambiguous, lossless rewrite -- merging duplicate/misplaced system messages (without dropping content), removing an empty system prompt, stripping leaked chat-template tokens, and truncating excess stop sequences to OpenAI's 4-sequence limit (order-preserving, reports what was dropped). Also renames OpenAI's legacy `function` role to `tool`, flagged as needing manual follow-up (a valid `tool` message also needs a `tool_call_id` this can't infer). `--dry-run` previews without writing. The remaining 5 rules (`temperature-range`, `hardcoded-provider-reference`, `unsupported-role`, `json-mode-missing-hint`) are left as manual-only findings by design -- fixing them would mean rewriting prompt content based on a guess about author intent, not a mechanical syntax fix. `llm_prompt_lint.fixers.apply_fixes()` exposes this as a library API, one fixer module per provider shape mirroring `parsers/`.
- Per-rule suppression: `--ignore RULE_ID` (repeatable, supports a bare family prefix like `system-prompt`) on both `check` and `fix`, plus a `.prompt-portability.json` sidecar config file (`{"ignore": [...]}`, `--config` to point elsewhere) so a team can check a suppression in rather than repeat the flag. Deliberately not embedded in the request JSON itself, since those files are meant to double as real API request bodies. An unrecognized rule name is a hard error, not a silent no-op, so a typo in a suppression you're relying on in CI can't fail quietly.
- CI: test matrix across 3 OSes x 3 Python versions, plus a lint/type-check job (ruff + mypy). A `release.yml` workflow publishes to PyPI via trusted publishing (OIDC, no stored token) on a `v*` tag push, after running the full test suite.
- 91 tests passing.

### Fixed
- A JSON file saved in a non-UTF-8 encoding used to crash `check`/`fix` with a raw, uncaught `UnicodeDecodeError`; it's now caught alongside the other file-read errors and reported cleanly.

### Changed
- Renamed the distribution from `llm-prompt-lint` to `prompt-portability` -- PyPI rejected the original name as too similar to two existing unrelated packages. The importable Python module is unchanged (`llm_prompt_lint`); only the PyPI name, CLI command, and docs changed.
