## Contents

- 1. Marketplace location
- 2. Top-level shape
- 3. Per-plugin entry shape
- 4. Required structural change: plugin tree must sit under `plugins/<name>/`
- 5. Concrete conversion example
- 6. Template asset
- 7. Verification
- 8. End-user install (the part you must document)

# Marketplace Mapping (`.claude-plugin/marketplace.json` → `.agents/plugins/marketplace.json`)

⚠️ **Not script-automated.** Marketplace publication is a deliberate act and the converted catalog should be reviewed by hand. The schema below comes from the official Codex plugin build docs ([developers.openai.com/codex/plugins/build](https://developers.openai.com/codex/plugins/build), primary) and the Codex `plugin-creator` system skill (`~/.codex/skills/.system/plugin-creator/references/plugin-json-spec.md`, secondary), not guesswork.

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
  - `source.source`: the official docs document **three** source types — `"local"`, `"url"`, and `"git-subdir"` (the latter taking `url` / `path` / `ref` / `sha` fields). Use `"local"` for the in-repo workflow this file describes.
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

## 8. End-user install (the part you must document)

`codex plugin marketplace add` accepts:

- `owner/repo[@ref]` (GitHub shorthand)
- HTTP(S) Git URLs
- SSH URLs
- local marketplace root directories

Plus options: `--ref <REF>` (pin to branch/tag/commit), `--sparse <PATH>` (filter checkout — see below), `--enable / --disable` (feature flags), `-c key=value` (TOML override).

`marketplace add` is the install — Codex has no separate `plugin install` subcommand.

### Critical: where Codex looks for `marketplace.json`

When the source is a git URL (or git shorthand), Codex clones into a staging dir and treats the **repo root** as the marketplace root. It then looks for:

```
<staging-root>/.agents/plugins/marketplace.json
```

`--sparse <PATH>` filters the checkout but does **NOT** rebase the marketplace root inside `<PATH>`. Empirically (Codex CLI as of 2026-05): even with `--sparse codex`, the staging dir still contains repo-root files, and Codex looks for the manifest at staging root, not at `staging/codex/`. So `--sparse <PATH>` alone is not enough to make a `<repo>/codex/.agents/plugins/marketplace.json` reachable via git install.

> ⚠️ **Unresolved conflict — re-verify before relying on either side.** The official docs' `git-subdir` source type (`url` / `path` / `ref` / `sha`) suggests a repo-subdirectory plugin *may* be reachable without the manual Layout A catalog. That conflicts with the empirical 2026-05 `--sparse` finding above. Re-verify against a current Codex CLI before changing the Layout A/B recommendation; until then this file surfaces the conflict without resolving it.

### Two layouts that actually work

**Layout A — marketplace at repo root (recommended for monorepo)**

The published Claude+Codex monorepo keeps a Codex catalog at repo root pointing into the codex/ subtree:

```
<repo>/.agents/plugins/marketplace.json     ← Codex finds this on git clone
└── plugins[].source.path: "./codex/plugins/<plugin-name>"

<repo>/codex/plugins/<plugin-name>/.codex-plugin/plugin.json
<repo>/codex/plugins/<plugin-name>/skills/...
```

End-user install: just `codex plugin marketplace add <git-url>` — no flags needed.

**Layout B — marketplace inside the variant subtree (local-path or dedicated branch)**

The codex/ subtree is also self-contained as its own marketplace root:

```
<repo>/codex/.agents/plugins/marketplace.json    ← local-path install
<repo>/codex/plugins/<plugin-name>/.codex-plugin/plugin.json
```

End-user install: `codex plugin marketplace add /local/path/to/codex` (or push the codex/ subtree as a dedicated branch and use `--ref <branch>`).

### What transfer.py emits

`transfer.py` outputs Layout B inside `<output>/`. To support Layout A in a monorepo, **manually maintain a second catalog at repo root** (or write tooling that splits/promotes between the two — out of scope for this skill today).

```bash
# Layout A end-user install
codex plugin marketplace add https://example.com/owner/repo.git
codex plugin marketplace add https://example.com/owner/repo.git --ref v1.2.3   # pinned

# Layout B end-user install (requires local clone or codex-only branch)
codex plugin marketplace add /local/path/to/repo/codex
```

Document the chosen layout's exact incantation in the consuming project's README — `codex plugin marketplace add --help` does not describe these path conventions and `--sparse` does not do what its name suggests.
