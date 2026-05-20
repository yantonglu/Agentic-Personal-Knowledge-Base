# Maintenance

This directory contains scripts and records used to maintain the vault.

Run the validator from the vault root:

```bash
python3 .kb-maintenance/validate_vault.py
```

For stricter handoff checks:

```bash
python3 .kb-maintenance/validate_vault.py --strict-tags --strict-names
```
