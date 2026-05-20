# Agent Entrypoint

This repository is an Obsidian vault skeleton for an agent-managed personal
knowledge base.

Before changing files:

1. Read `README.md` for the public project overview and repository layout.
2. Read `RULES.md` for the authoritative classification and formatting rules.
3. Use `.templates/BASE_TEMPLATE.md` and category `.TEMPLATE.md` files when creating notes.
4. Run `python3 .kb-maintenance/validate_vault.py` after structural changes.

Keep vault-specific content and local runtime state out of public releases unless
the user explicitly asks to publish a downstream vault.
