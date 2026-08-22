from llm_prompt_lint.rules import (
    hardcoded_provider,
    json_mode,
    special_tokens,
    stop_sequences,
    system_prompt,
    temperature,
    unsupported_role,
)

ALL_RULES = [
    system_prompt.check,
    stop_sequences.check,
    temperature.check,
    hardcoded_provider.check,
    special_tokens.check,
    unsupported_role.check,
    json_mode.check,
]

# The rule_id "family" each module can emit (before any "/" suffix) -- used
# to validate --ignore/config entries so a typo fails loudly instead of
# silently suppressing nothing. Read off each module's own RULE_ID rather
# than duplicated as string literals, so this can't drift from the rules
# themselves.
KNOWN_RULE_FAMILIES = {
    system_prompt.RULE_ID,
    stop_sequences.RULE_ID,
    temperature.RULE_ID,
    hardcoded_provider.RULE_ID,
    special_tokens.RULE_ID,
    unsupported_role.RULE_ID,
    json_mode.RULE_ID,
}

__all__ = ["ALL_RULES", "KNOWN_RULE_FAMILIES"]
