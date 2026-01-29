# Kiro Agent SDK User Guide - Design Document

**Date:** 2026-01-29
**Status:** Approved
**Purpose:** Comprehensive user guide for experienced Python developers

## Target Audience

Experienced developers familiar with AI APIs. Concise explanations, API-focused, quick reference structure.

## Structure

```
docs/guide/
├── index.md
├── getting-started.md
├── api-reference.md
├── examples.md
├── error-handling.md
├── architecture.md
└── troubleshooting.md
```

## File Specifications

### index.md
- One-line SDK description
- Links to each guide section with 1-sentence descriptions
- Quick 5-line example showing simplest usage

### getting-started.md
- Prerequisites: Python 3.10+, kiro-cli installed and authenticated
- Installation: pip install command
- Your First Query: minimal working example with query()
- Extracting text from AssistantMessage
- Configuring Options: KiroAgentOptions basics (system_prompt, allowed_tools, trust_all_tools, cwd)

### api-reference.md
- **query()**: Signature, parameters table, return type (AsyncIterator), iteration pattern
- **KiroSDKClient**: Constructor, async context manager, start()/stop() methods
  - Note: Currently limited - multi-turn not fully implemented due to CLI constraints
- **KiroAgentOptions**: Full dataclass reference table with all fields
- **Message Types**: AssistantMessage, UserMessage, ToolResultMessage, content block types

### examples.md
Complete, runnable examples (10-20 lines each):
1. Basic Query - extracting text from response
2. Custom System Prompt - using system_prompt option
3. Tool Usage - allowed_tools and trust_all_tools
4. Working Directory - using cwd option
5. Processing Multiple Content Blocks - iterating message.content
6. Custom CLI Path - using cli_path option

### error-handling.md
- Error hierarchy diagram (KiroSDKError base with 6 subclasses)
- Common errors with causes and solutions:
  - CLINotFoundError
  - ProcessError (with exit_code attribute)
  - CLIJSONDecodeError (with raw_output attribute)
- Handling pattern: try/except example

### architecture.md
- Overview: SDK wraps kiro-cli via subprocess
- Components: Three-layer diagram (query/client → transport → CLI)
- Communication flow:
  1. Prompt passed as CLI argument
  2. CLI spawned with --no-interactive --wrap never
  3. Terminal output captured, ANSI codes stripped
  4. Response extracted from "> " prefixed lines
  5. Parsed into AssistantMessage
- Why this design: CLI doesn't support JSON streaming
- Key files reference

### troubleshooting.md
Common issues with solutions:
- Query hangs indefinitely
- "kiro-cli not found"
- Empty response
- Response truncated
- Authentication errors
- Debugging tips (verbose option)

## Design Decisions

1. **Limitations inline**: Document limitations within relevant sections, not separate section
2. **Complete examples**: All code examples include imports, async def main, anyio.run
3. **Six separate files**: Easy navigation for experienced developers
4. **Focus on query()**: Primary API since KiroSDKClient multi-turn is limited
