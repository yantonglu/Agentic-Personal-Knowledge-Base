# File Management Rules

These rules define how an AI agent should classify, format, index, and validate
files in an Obsidian-based personal knowledge base.

## 1. YAML Frontmatter

Every indexed Markdown note must begin with YAML frontmatter.

Required fields:

| Field | Type | Description |
| --- | --- | --- |
| `title` | string | Human-readable title |
| `date` | date | Intake date, `YYYY-MM-DD` |
| `category` | string | Vault-relative category path |
| `tags` | list | At least one `status/*` tag and one content tag |
| `status` | string | Processing status |

Recommended fields:

| Field | Type | Description |
| --- | --- | --- |
| `updated` | date | Last meaningful update date |
| `aliases` | list | Obsidian aliases |
| `source` | string | URL, book, author, or source context |
| `author` | string | Original author |
| `language` | string | Primary language code, such as `en`, `zh`, or `multilingual` |

Status values:

| Value | Meaning | Expected location |
| --- | --- | --- |
| `raw` | Unprocessed source | `00-Inbox/` |
| `needs-review` | Manual classification required | `00-Inbox/` |
| `classified` | Classified but not formatted | Category directory |
| `formatted` | Formatted but not fully indexed | Category directory |
| `indexed` | Ready for normal use | Category directory |
| `archived` | Archived material | Category directory |

## 2. Tags

Tags use slash-separated hierarchy. Each note should contain:

- one status tag, such as `status/indexed`;
- at least one content tag, such as `type/note`, `topic/ai`, `method/rag`, or `model/example`.

Do not use category tags to duplicate the `category` field and folder path.

## 3. File Naming

Use concise names derived from the note title.

Rules:

- Use English letters, numbers, and hyphens by default.
- Technical abbreviations and model names may keep their original casing.
- Avoid spaces, underscores, emoji, and shell-sensitive symbols.
- Keep the stem under 64 characters when possible.
- Do not prefix filenames with category names; the directory already carries that context.

Examples:

- `TransformerNotes.md`
- `RAGChecklist.md`
- `ProjectReview.md`

## 4. Classification

Agents discover categories by scanning root-level directories that match
`NN-CategoryName/`.

Each normal category should contain:

- `README.md` with an `Agent Classification Criteria` section;
- `.TEMPLATE.md` with category-specific fields and sections.

Classification process:

1. Read the complete file content.
2. Read all available category `README.md` files.
3. Choose the most specific matching category.
4. If no category clearly matches, keep the file in `00-Inbox/` and set `status: needs-review`.

Agents must not create new category directories without explicit user approval.

## 5. Multi-format Source Files

All source files should eventually become standard Markdown notes.

For PDF, Word, PowerPoint, Excel, HTML, CSV, JSON, XML, EPUB, image, audio, and
ZIP inputs, prefer converting with Microsoft MarkItDown first:

```bash
markitdown "00-Inbox/source.ext" -o "/tmp/source.converted.md"
```

Then the agent should:

1. Read the converted Markdown and source metadata.
2. Apply the base template and target category template.
3. Preserve readable content, links, tables, code blocks, and captions.
4. Move source attachments into `assets/<category>/<note-or-asset-group>/`.
5. Rewrite attachment links as vault-root paths, such as `![[assets/category/note/image.png]]`.
6. Record conversion limitations in the note's remarks section.

Markdown and plain text sources can be formatted directly without MarkItDown.

## 6. Assets

All local attachments live under `assets/`.

Rules:

- Do not create hidden `.note.assets/` folders beside notes.
- Prefer safe attachment filenames: letters, numbers, dot, underscore, and hyphen.
- Avoid whitespace in asset paths because it can break embeds across tools.
- Use vault-root Obsidian links, for example:

```markdown
![[assets/category/note/image.png]]
```

## 7. Dataview Indexing

`CONTENTS.md` is an automatic index and should not contain hand-maintained tables.

To make a note appear in the index:

- set `status: indexed`;
- set `title`, `date`, `category`, and `tags`;
- place the note in the correct category directory.

## 8. Category Creation

Only create a new category after user approval.

Suggested category structure:

```text
NN-CategoryName/
├── README.md
└── .TEMPLATE.md
```

The category `README.md` should include:

```markdown
# CategoryName

## Category Scope

Describe what belongs here.

## Agent Classification Criteria

- Include files when ...
- Exclude files when ...
```

## 9. Internal Links

Use standard Obsidian wiki links:

```markdown
[[NoteName]]
[[NoteName|Display Text]]
[[Folder/NoteName]]
```

Do not rewrite uncertain links silently. If a target is missing, keep the link and
record the issue in the note's remarks section.

## 10. User Profile (`SOULS.md`)

`SOULS.md` is a private-vault user profile for agent personalization. In a public
skeleton repository it should remain a placeholder.

Update it only when explicitly requested or after a deliberate periodic review.
Every claim in a real `SOULS.md` should be grounded in vault evidence.

## 11. Validation

Run the maintenance validator after structural changes:

```bash
python3 .kb-maintenance/validate_vault.py
```

Use stricter checks when preparing a vault for handoff:

```bash
python3 .kb-maintenance/validate_vault.py --strict-tags --strict-names
```
