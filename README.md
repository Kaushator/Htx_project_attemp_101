# HTX Cursor Bootstrap

## Copy these into your repo root
- `.vscode/` (tasks + keybindings)
- `.cursorrules`
- `scripts/` (bat files)
- `journal_roadmap/` (logger + md files)
- `githooks/post-commit.sample` → copy to `.git/hooks/post-commit`

## Use in Cursor
- Ctrl+Alt+E → Setup Env
- Ctrl+Alt+P → Git Push + Log
- Ctrl+Alt+J → Log Task

## Optional
- Duplicate `journal_roadmap\.env.template` as `.env` and put `OPENAI_API_KEY=...` to enable future AI summaries.