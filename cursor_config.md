# Cursor Starter Config (Token-savvy)

## Recommended Settings (Cursor → Settings → AI)
- **Custom API key**: ON (use your own OpenAI key)
- **Model defaults**:
  - Chat: `gpt-4.1` (or cost-efficient latest)
  - Code: `gpt-4.1-mini`
  - Quick Fix / Inline: `gpt-4.1-mini`
- **Context window**: disable long-context by default; enable only ad-hoc.
- **Reduce noise**: turn **off** auto-include large unrelated files.
- **Python-only mode** for Python tasks.
- **Auto-truncate history**: ON.

## Prompt Snippets (add to Cursor → Settings → Custom Prompts)
- **/plan-small** — 3–5 tiny steps plan, token-light.
- **/implement-unit** — minimal change, single-file diff.
- **/tests-min** — tests: happy + edge + error, ≤30 lines.
- **/doc-1liner** — one-line docstrings only.
- **/push** — remind to run task “Git Push + Log” + suggest short commit message (≤8 words).