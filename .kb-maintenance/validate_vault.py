#!/usr/bin/env python3
# v1.4 — English-only public-skeleton validator.
# Usage: python3 .kb-maintenance/validate_vault.py [--strict-tags] [--strict-names] [--json]

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


CONFIG = {
    "REQUIRED_ROOT_FILES": [
        "README.md",
        "README_zh.md",
        "RULES.md",
        "CONTENTS.md",
        "SOULS.md",
    ],
    "AGENT_ENTRYPOINTS": ["AGENTS.md"],
    "AGENT_SYMLINKS": {"CLAUDE.md": "AGENTS.md", "GEMINI.md": "AGENTS.md"},
    "SYSTEM_DIRS": {".git", ".obsidian", ".templates", ".kb-maintenance", "assets"},
    "ASSET_DIR": "assets",
    "SYSTEM_NOTE_NAMES": {
        "README.md",
        "README_zh.md",
        "RULES.md",
        "CONTENTS.md",
        "SOULS.md",
        "AGENTS.md",
        "CLAUDE.md",
        "GEMINI.md",
        "progress.md",
        ".TEMPLATE.md",
    },
    "REQUIRED_FRONTMATTER": {"title", "date", "category", "tags", "status"},
    "STATUS_VALUES": {
        "raw",
        "needs-review",
        "classified",
        "formatted",
        "indexed",
        "archived",
    },
    "CONTENT_TAG_PREFIXES": ("type/", "topic/", "method/", "model/"),
    "ALLOWED_FILENAME_RE": r"^[A-Za-z0-9-]+$",
}


@dataclass
class CheckResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    stats: dict[str, int] = field(default_factory=dict)

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def merge(self, other: "CheckResult") -> None:
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        self.stats.update(other.stats)


@dataclass
class Frontmatter:
    fields: dict[str, str]
    tags: list[str]
    raw: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the Obsidian AI knowledge base structure and metadata."
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Vault root path. Defaults to the current working directory.",
    )
    parser.add_argument(
        "--strict-tags",
        action="store_true",
        help="Treat missing content tags as errors.",
    )
    parser.add_argument(
        "--strict-names",
        action="store_true",
        help="Treat legacy filename rule violations as errors.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON output.",
    )
    return parser.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def parse_frontmatter(path: Path) -> Frontmatter | None:
    text = read_text(path)
    if not text.startswith("---"):
        return None

    parts = text.split("---", 2)
    if len(parts) < 3:
        return None

    raw = parts[1]
    fields: dict[str, str] = {}
    tags: list[str] = []
    current_key: str | None = None

    for line in raw.splitlines():
        key_match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if key_match:
            current_key = key_match.group(1)
            value = key_match.group(2).strip().strip('"').strip("'")
            fields[current_key] = value
            continue

        list_match = re.match(r"^\s*-\s*(.+?)\s*$", line)
        if current_key == "tags" and list_match:
            tags.append(list_match.group(1).strip().strip('"').strip("'"))

    return Frontmatter(fields=fields, tags=tags, raw=raw)


def category_dirs(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.iterdir()
        if path.is_dir() and re.match(r"^\d\d-", path.name)
    )


def note_files(root: Path) -> list[Path]:
    notes: list[Path] = []
    for path in root.rglob("*.md"):
        relative_parts = path.relative_to(root).parts
        if any(part in CONFIG["SYSTEM_DIRS"] for part in relative_parts):
            continue
        if path.name in CONFIG["SYSTEM_NOTE_NAMES"]:
            continue
        if relative_parts and re.match(r"^\d\d-", relative_parts[0]):
            notes.append(path)
    return sorted(notes)


def template_files(root: Path) -> list[Path]:
    templates = [root / ".templates" / "BASE_TEMPLATE.md"]
    templates.extend(sorted(root.glob("[0-9][0-9]-*/.TEMPLATE.md")))
    return templates


def has_prefix(values: Iterable[str], prefixes: tuple[str, ...]) -> bool:
    return any(value.startswith(prefixes) for value in values)


def relative_posix(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def validate_root(root: Path) -> CheckResult:
    result = CheckResult()

    for filename in CONFIG["REQUIRED_ROOT_FILES"]:
        if not (root / filename).exists():
            result.error(f"Missing required root file: {filename}")

    for filename in CONFIG["AGENT_ENTRYPOINTS"]:
        path = root / filename
        if not path.exists():
            result.error(f"Missing agent entrypoint: {filename}")
            continue
        text = read_text(path)
        if "RULES.md" not in text and filename == "AGENTS.md":
            result.error("AGENTS.md should reference RULES.md")

    for filename, target in CONFIG["AGENT_SYMLINKS"].items():
        path = root / filename
        if not path.is_symlink():
            result.error(f"{filename} should be a symlink to {target}")
            continue
        if path.readlink().as_posix() != target:
            result.error(f"{filename} should point to {target}")

    inbox = root / "00-Inbox"
    if not inbox.exists():
        result.error("Missing 00-Inbox directory")
    else:
        visible = [
            path.name
            for path in inbox.iterdir()
            if path.name not in {".DS_Store", "Thumbs.db", ".gitkeep"}
        ]
        result.stats["inbox_items"] = len(visible)

    return result


def validate_categories(root: Path) -> CheckResult:
    result = CheckResult()
    dirs = category_dirs(root)
    result.stats["category_dirs"] = len(dirs)

    for directory in dirs:
        if directory.name == "00-Inbox":
            continue

        readme = directory / "README.md"
        if not readme.exists():
            result.error(f"{relative_posix(directory, root)} missing README.md")
            continue

        text = read_text(readme)
        is_special = "do not auto-classify" in text.lower() or "explicit user instruction only" in text.lower()
        template = directory / ".TEMPLATE.md"

        if is_special:
            if template.exists():
                result.warn(
                    f"{relative_posix(directory, root)} is special but has .TEMPLATE.md"
                )
            continue

        if "Agent Classification Criteria" not in text:
            result.error(
                f"{relative_posix(readme, root)} missing Agent Classification Criteria"
            )
        if not template.exists():
            result.error(f"{relative_posix(directory, root)} missing .TEMPLATE.md")

    return result


def validate_template_tags(root: Path, strict_tags: bool) -> CheckResult:
    result = CheckResult()
    templates = template_files(root)
    result.stats["templates_checked"] = len(templates)

    for template in templates:
        if not template.exists():
            result.error(f"Missing template: {relative_posix(template, root)}")
            continue

        frontmatter = parse_frontmatter(template)
        if frontmatter is None:
            result.error(f"{relative_posix(template, root)} missing frontmatter")
            continue

        for field in [
            "title",
            "date",
            "updated",
            "category",
            "tags",
            "aliases",
            "status",
            "source",
            "author",
            "language",
        ]:
            if field not in frontmatter.fields:
                result.error(f"{relative_posix(template, root)} missing field: {field}")

        validate_tags(
            result,
            relative_posix(template, root),
            frontmatter.tags,
            strict_tags=True,
        )

    return result


def validate_tags(
    result: CheckResult,
    label: str,
    tags: list[str],
    strict_tags: bool,
) -> None:
    if not has_prefix(tags, ("status/",)):
        result.error(f"{label} missing status/* tag")

    missing_content_tag = not has_prefix(tags, CONFIG["CONTENT_TAG_PREFIXES"])

    if missing_content_tag:
        message = f"{label} missing content tag"
        result.error(message) if strict_tags else result.warn(message)


def validate_notes(root: Path, strict_tags: bool, strict_names: bool) -> CheckResult:
    result = CheckResult()
    filename_re = re.compile(CONFIG["ALLOWED_FILENAME_RE"])
    notes = note_files(root)
    result.stats["notes_checked"] = len(notes)
    result.stats["notes_missing_content_tags"] = 0
    result.stats["filename_rule_warnings"] = 0

    for note in notes:
        label = relative_posix(note, root)
        frontmatter = parse_frontmatter(note)
        if frontmatter is None:
            result.error(f"{label} missing frontmatter")
            continue

        missing_fields = CONFIG["REQUIRED_FRONTMATTER"] - set(frontmatter.fields)
        for field in sorted(missing_fields):
            result.error(f"{label} missing required field: {field}")

        status = frontmatter.fields.get("status")
        if status and status not in CONFIG["STATUS_VALUES"]:
            result.error(f"{label} has invalid status: {status}")

        category = frontmatter.fields.get("category")
        expected_category = note.parent.relative_to(root).as_posix()
        if category and category != expected_category:
            result.error(
                f"{label} category mismatch: {category!r} != {expected_category!r}"
            )

        root_dir = note.relative_to(root).parts[0]
        if root_dir == "00-Inbox" and status not in {"raw", "needs-review"}:
            result.error(f"{label} in Inbox must be raw or needs-review")
        if root_dir != "00-Inbox" and status in {"raw", "needs-review"}:
            result.error(f"{label} outside Inbox cannot be {status}")

        if not has_prefix(frontmatter.tags, ("status/",)):
            result.error(f"{label} missing status/* tag")

        missing_content_tag = not has_prefix(
            frontmatter.tags, CONFIG["CONTENT_TAG_PREFIXES"]
        )

        if missing_content_tag:
            result.stats["notes_missing_content_tags"] += 1
            if strict_tags:
                result.error(f"{label} missing content tag")

        if not filename_re.match(note.stem):
            result.stats["filename_rule_warnings"] += 1
            if strict_names:
                result.error(f"{label} violates current filename rule")

    return result


def validate_contents(root: Path) -> CheckResult:
    result = CheckResult()
    path = root / "CONTENTS.md"
    if not path.exists():
        result.error("Missing CONTENTS.md")
        return result

    text = read_text(path)
    if "```dataview" not in text:
        result.error("CONTENTS.md must contain Dataview query blocks")
    if "status = \"indexed\"" not in text:
        result.error("CONTENTS.md must query status = \"indexed\"")
    if "| # | File |" in text or "legacy manual index" in text:
        result.error("CONTENTS.md still contains legacy manual index instructions")

    return result


def validate_progress(root: Path) -> CheckResult:
    return CheckResult()


def validate_assets(root: Path) -> CheckResult:
    result = CheckResult()
    assets = root / CONFIG["ASSET_DIR"]

    if not assets.exists():
        result.warn("Missing assets directory")
        return result
    if not assets.is_dir():
        result.error("assets exists but is not a directory")
        return result

    legacy_dirs = [
        path
        for path in root.glob("[0-9][0-9]-*/.*.assets")
        if path.is_dir()
    ]
    result.stats["legacy_dot_asset_dirs"] = len(legacy_dirs)
    for path in legacy_dirs:
        result.error(f"Legacy hidden asset directory remains: {relative_posix(path, root)}")

    asset_files = [
        path for path in assets.rglob("*") if path.is_file() and path.name != ".gitkeep"
    ]
    result.stats["asset_files"] = len(asset_files)
    result.stats["unsafe_asset_filenames"] = 0

    safe_asset_name_re = re.compile(r"^[A-Za-z0-9._-]+$")
    whitespace_re = re.compile(r"\s")
    for path in asset_files:
        if path.name == "README.md":
            continue
        relative = path.relative_to(root).as_posix()
        if not safe_asset_name_re.match(path.name) or whitespace_re.search(relative):
            result.stats["unsafe_asset_filenames"] += 1
            result.error(f"Unsafe asset filename or path: {relative}")

    missing: list[str] = []
    checked = 0
    asset_link_re = re.compile(
        r"!\[\[([^\]]+)\]\]|\[[^\]]+\]\((assets/[^)]+)\)"
    )

    for note in note_files(root):
        text = read_text(note)
        for match in asset_link_re.finditer(text):
            target = match.group(1) or match.group(2)
            target = target.split("|", 1)[0].split("#", 1)[0].strip()
            if target.startswith(".") and ".assets/" in target:
                result.error(
                    f"{relative_posix(note, root)} uses legacy hidden asset link: {target}"
                )
                continue
            if not target.startswith("assets/"):
                continue
            checked += 1
            if not (root / target).exists():
                missing.append(f"{relative_posix(note, root)} -> {target}")

    result.stats["asset_links_checked"] = checked
    for item in missing:
        result.error(f"Missing asset target: {item}")

    return result


def run_validation(root: Path, strict_tags: bool, strict_names: bool) -> CheckResult:
    result = CheckResult()

    for check in [
        validate_root(root),
        validate_categories(root),
        validate_template_tags(root, strict_tags=strict_tags),
        validate_notes(root, strict_tags=strict_tags, strict_names=strict_names),
        validate_contents(root),
        validate_assets(root),
    ]:
        result.merge(check)

    return result


def print_text(result: CheckResult) -> None:
    status = "PASS" if not result.errors else "FAIL"
    print(f"VALIDATION_STATUS={status}")

    for key in sorted(result.stats):
        print(f"{key}={result.stats[key]}")

    if result.errors:
        print("\nERRORS:")
        for error in result.errors:
            print(f"- {error}")

    if result.warnings:
        print("\nWARNINGS:")
        for warning in result.warnings:
            print(f"- {warning}")


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    result = run_validation(
        root=root,
        strict_tags=args.strict_tags,
        strict_names=args.strict_names,
    )

    if args.json:
        print(
            json.dumps(
                {
                    "status": "PASS" if not result.errors else "FAIL",
                    "errors": result.errors,
                    "warnings": result.warnings,
                    "stats": result.stats,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print_text(result)

    return 1 if result.errors else 0


if __name__ == "__main__":
    sys.exit(main())
