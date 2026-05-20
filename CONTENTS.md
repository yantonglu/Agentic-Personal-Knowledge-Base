# Contents Index

This file is rendered by the Obsidian Dataview community plugin.

Do not manually maintain index tables here. Keep note frontmatter correct and let
Dataview build the views.

## Indexed Notes

```dataview
TABLE WITHOUT ID
  file.link AS "File",
  title AS "Title",
  category AS "Category",
  dateformat(date, "yyyy-MM-dd") AS "Date",
  status AS "Status",
  file.tags AS "Tags"
FROM ""
WHERE status = "indexed"
  AND !startswith(file.folder, ".")
  AND !startswith(file.folder, "assets")
  AND file.name != "README"
  AND !contains(file.name, "TEMPLATE")
SORT category ASC, date DESC, file.name ASC
```

## Inbox Review

```dataview
TABLE WITHOUT ID
  file.link AS "File",
  title AS "Title",
  status AS "Status",
  category AS "Suggested Category",
  file.tags AS "Tags"
FROM "00-Inbox"
WHERE status = "raw" OR status = "needs-review"
SORT status ASC, file.name ASC
```

## Recently Updated

```dataview
TABLE WITHOUT ID
  file.link AS "File",
  title AS "Title",
  category AS "Category",
  dateformat(updated, "yyyy-MM-dd") AS "Updated"
FROM ""
WHERE status = "indexed"
  AND updated
  AND !startswith(file.folder, ".")
  AND !startswith(file.folder, "assets")
  AND file.name != "README"
  AND !contains(file.name, "TEMPLATE")
SORT updated DESC, file.name ASC
LIMIT 20
```

## Agent Maintenance Notes

- Keep this page query-driven.
- Do not append manual rows.
- If results look wrong, inspect note frontmatter first, then run `.kb-maintenance/validate_vault.py`.
