# Marketplace Mapping (`.claude-plugin/marketplace.json` → `.agents/plugins/marketplace.json`)

⚠️ **Not script-automated.** Marketplace publication is a deliberate act and the converted catalog should be reviewed by hand. The schema below comes from the Codex `plugin-creator` skill (`~/.codex/skills/.system/plugin-creator/references/plugin-json-spec.md`), not guesswork.

For automated layers, see [`skill-mapping.md`](skill-mapping.md) (skill files) and [`plugin-mapping.md`](plugin-mapping.md) (plugin manifests).

## 1. Marketplace location

| Scope | Path |
|---|---|
| Repo plugin | `<marketplace-root>/.agents/plugins/marketplace.json` |
| Local plugin | `~/.agents/plugins/marketplace.json` |

For the codex variant of a Claude plugin, use the repo form: write to `<codex-root>/.agents/plugins/marketplace.json` where `<codex-root>` is the directory you're treating as a self-contained marketplace (e.g., `codex/` if mirroring a Claude plugin into a sibling tree).

## 2. Top-level shape

```json
{
  "name": "<marketplace-id>",
  "interface": {
    "displayName": "<user-facing title>"
  },
  "plugins": [ ... ]
}
```

| Field | Required | Source from Claude marketplace |
|---|---|---|
| `name` | yes | port verbatim from Claude `name` |
| `interface.displayName` | recommended | derive from Claude `metadata.description` or hand-write |
| `plugins[]` | yes | one entry per Claude plugin |

Drop on the Codex side: `$schema`, `owner`, `metadata`, `strict`. Codex marketplace has no equivalent fields and rejects unknown keys conservatively.

## 3. Per-plugin entry shape

Codex requires this exact shape:

```json
{
  "name": "<plugin-id>",
  "source": {
    "source": "local",
    "path": "./plugins/<plugin-name>"
  },
  "policy": {
    "installation": "AVAILABLE",
    "authentication": "ON_INSTALL"
  },
  "category": "<Capitalized Category>"
}
```

### Field-by-field rules

- **`name`** — Plugin id. Match the plugin folder name and the plugin's own `plugin.json` `name`. Port verbatim from Claude.
- **`source`** — **Object, not string** (this is the most common mistake when porting from Claude).
  - `source.source`: `"local"` for the in-repo workflow. The Codex spec lists this as the only documented value.
  - `source.path`: `./plugins/<plugin-name>`. The path is relative to the marketplace root (the dir containing `.agents/`), not the marketplace.json file.
- **`policy`** — **Required block.** Always include `installation` and `authentication`.
  - `installation`: `NOT_AVAILABLE` | `AVAILABLE` | `INSTALLED_BY_DEFAULT`. Default to `AVAILABLE`.
  - `authentication`: `ON_INSTALL` | `ON_USE`. Default to `ON_INSTALL`.
  - `products`: omit unless the user explicitly asks for product gating.
- **`category`** — Required. Codex spec example uses Capitalized form (`Productivity`). Map Claude's lowercase categories accordingly.

### Drop these Claude fields

- `description` — Codex plugin entry has no `description`; the user-facing copy lives in the plugin's own `plugin.json`.
- `version` — Codex resolves the version from the plugin's `plugin.json`.
- `homepage` — no Codex equivalent at the marketplace layer.
- `tags` — Claude-specific.
- `lspServers` — Codex plugins don't host LSP.
- `strict` — Claude-specific.

## 4. Required structural change: plugin tree must sit under `plugins/<name>/`

Codex's `source.path: "./plugins/<plugin-name>"` is a structural requirement, not a stylistic one. The plugin tree (the dir holding `.codex-plugin/plugin.json`) MUST live at `<marketplace-root>/plugins/<plugin-name>/`. If you ported a Claude plugin tree to the marketplace root directly, move it down one level:

```
codex/                                  ← marketplace root
├── .agents/plugins/marketplace.json
└── plugins/baransu/                    ← plugin tree (was at codex/ root)
    ├── .codex-plugin/plugin.json
    ├── .codex-agents-templates/
    └── skills/
```

## 5. Concrete conversion example

Claude marketplace entry:

```json
{
  "name": "baransu",
  "owner": { "name": "ben.tsai", "email": "ben.tsai@hy-tech.com.tw" },
  "metadata": { "description": "...", "version": "0.2.0" },
  "plugins": [
    {
      "name": "baransu",
      "source": "./plugins/baransu",
      "description": "...",
      "category": "governance",
      "tags": ["planning", "design", "..."]
    }
  ]
}
```

Becomes:

```json
{
  "name": "baransu",
  "interface": { "displayName": "baransu (Codex variant)" },
  "plugins": [
    {
      "name": "baransu",
      "source": { "source": "local", "path": "./plugins/baransu" },
      "policy": { "installation": "AVAILABLE", "authentication": "ON_INSTALL" },
      "category": "Productivity"
    }
  ]
}
```

Notable transformations:
- `owner` + `metadata` → dropped; `displayName` carries the user-facing title.
- `source` string → `source` object with `local` / `path`.
- `policy` block added (required, no Claude analogue).
- `description`, `version`, `tags` → dropped (live in plugin's own `plugin.json`).
- `category` capitalized.

## 6. Template asset

[`assets/codex-marketplace.template.json`](../assets/codex-marketplace.template.json) holds the canonical shape with `$placeholder` markers (`$marketplace_name`, `$marketplace_display_name`, `$plugin_name`, `$plugin_category`). Use it as a copy-and-fill starting point. The transfer script does **not** auto-fill this template — marketplace conversion stays manual because (a) the structural move under `plugins/<name>/` may already be done by an earlier inline edit, and (b) marketplace publication is a deliberate one-shot decision per repo.

## 7. Verification

After writing, sanity-check:

```bash
python3 -c "import json; json.load(open('codex/.agents/plugins/marketplace.json'))"
test -f codex/plugins/<plugin-name>/.codex-plugin/plugin.json || echo "MISSING plugin tree under plugins/<name>/"
```
