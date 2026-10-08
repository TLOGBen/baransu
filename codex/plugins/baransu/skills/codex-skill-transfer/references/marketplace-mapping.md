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

⚠️ **Maintained by hand.** Marketplace publication is a deliberate act; the script never writes the repo-root catalog. The schema below comes from the official Codex plugin build docs ([developers.openai.com/plugins/build/plugins](https://developers.openai.com/plugins/build/plugins), primary) and the Codex marketplace loader at `rust-v0.161.0` (`codex-rs/core-plugins/src/marketplace.rs`), not guesswork. Where the two differ, the docs state authoring guidance and the loader states what actually fails. Claude side: Claude Code 2.1.293 marketplace reference. Labels: *(inferred)* = derived, not stated officially; *(unpublished)* = not documented.

For the layers below, see [`skill-mapping.md`](skill-mapping.md) (skill files) and [`plugin-mapping.md`](plugin-mapping.md) (plugin manifests).

## 1. Marketplace location and lookup order

| Scope | Path |
|---|---|
| Repo marketplace | `<marketplace-root>/.agents/plugins/marketplace.json` |
| Personal marketplace | `~/.agents/plugins/marketplace.json` |
| Claude marketplace (for comparison) | `<root>/.claude-plugin/marketplace.json` |

Codex reads the **first existing** file of:

1. `.agents/plugins/marketplace.json`
2. `.agents/plugins/api_marketplace.json`
3. `.claude-plugin/marketplace.json`
4. `.cursor-plugin/marketplace.json`

Consequence: a repo that ships a Claude catalog and no `.agents/plugins/marketplace.json` makes Codex load the Claude catalog — Claude-shaped plugins, mods included *(inferred)*. Keep a Codex catalog at every root a user can add, and never delete it while a Claude catalog sits next to it.

For the Codex copy of a Claude plugin, write `<codex-root>/.agents/plugins/marketplace.json` where `<codex-root>` is the directory treated as a self-contained marketplace (e.g., `codex/` when the Codex copy lives in a sibling tree), plus a repo-root catalog when users install from a git URL (§8).

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

Drop on the Codex side: `$schema`, `owner`, `description`, `version`, `metadata`, `forceRemoveDeletedPlugins`, `allowCrossMarketplaceDependenciesOn`, `renames`. Codex has no equivalent top-level fields. (Unknown keys do not fail the load, so dropping them is for a clean catalog.)

## 3. Per-plugin entry shape

The loader requires only `name` and `source` (an entry whose source cannot be resolved is skipped); the build docs say to always include `policy.installation`, `policy.authentication`, and `category`, so every entry carries this shape:

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
- **`source`** — An object, or a plain relative-path string for a local plugin. The transfer always writes the object form.
  - `source.source`: four source types — `"local"` (`path`), `"url"` (`url`, optional `path` / `ref` / `sha`), `"git-subdir"` (`url`, `path`, optional `ref` / `sha`), and `"npm"` (`package`, optional `version` / `registry`). Use `"local"` for the in-repo workflow this file describes.
  - Claude source mapping: relative path → `local`; `github` → `url` with the repository's git URL; `url` → `url`; `git-subdir` → `git-subdir`; `npm` → `npm`; `archive` and `command` have **no** Codex counterpart — host the plugin some other way or leave it out.
  - `source.path`: `./plugins/<plugin-name>`. The path is relative to the marketplace root (the dir containing `.agents/`), not the marketplace.json file.
- **`policy`** — Recommended by the docs (the loader defaults to `AVAILABLE` / `ON_INSTALL`). Always include `installation` and `authentication`.
  - `installation`: `NOT_AVAILABLE` | `AVAILABLE` | `INSTALLED_BY_DEFAULT`. Default to `AVAILABLE`. Claude's `defaultEnabled: true` is the closest match to `INSTALLED_BY_DEFAULT`; Codex has no `defaultEnabled`.
  - `authentication`: `ON_INSTALL` | `ON_USE`. Default to `ON_INSTALL`.
  - `products`: omit unless the user explicitly asks for product gating.
- **`category`** — Recommended by the docs; a marketplace `category` overrides the plugin's own. Codex spec example uses Capitalized form (`Productivity`). Map Claude's lowercase categories accordingly.
- **Other keys** (`displayName`, `interface`, …) are kept by the loader as fallback manifest fields for that plugin; the plugin's own manifest is still the right home for them.
- **Claude-only plugins** (mods, or plugins that are nothing but Claude-only components) get no entry.

### Drop these Claude fields

- `description` — Codex plugin entry has no `description`; the user-facing copy lives in the plugin's own `plugin.json`.
- `version` — Codex resolves the version from the plugin's `plugin.json`.
- `homepage` — no Codex equivalent at the marketplace layer.
- `tags`, `relevance`, `metadata` — Claude-specific.
- `dependencies` — Codex has no plugin dependencies.
- `defaultEnabled` — replaced by `policy.installation` (above).
- `headers`, `headersHelper` — Claude-specific source auth.
- `lspServers` — Codex plugins don't host LSP.
- `strict` — Claude-specific.

## 4. Required structural change: plugin tree must sit under `plugins/<name>/`

Codex's `source.path: "./plugins/<plugin-name>"` is a structural requirement, not a stylistic one. The plugin tree (the dir holding the portable root `plugin.json`) MUST live at `<marketplace-root>/plugins/<plugin-name>/`. If you ported a Claude plugin tree to the marketplace root directly, move it down one level:

```
codex/                                  ← marketplace root
├── .agents/plugins/marketplace.json
└── plugins/<plugin>/                   ← plugin tree (was at codex/ root)
    ├── plugin.json
    ├── .codex-agents/
    ├── rules/
    └── skills/
```

## 5. Concrete conversion example

Claude marketplace entry:

```json
{
  "name": "my-market",
  "owner": { "name": "<owner>" },
  "metadata": { "description": "...", "version": "0.2.0" },
  "plugins": [
    {
      "name": "my-plugin",
      "source": "./plugins/my-plugin",
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
  "name": "my-market",
  "interface": { "displayName": "my-market (Codex variant)" },
  "plugins": [
    {
      "name": "my-plugin",
      "source": { "source": "local", "path": "./plugins/my-plugin" },
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
test -f codex/plugins/<plugin-name>/plugin.json || echo "MISSING plugin tree under plugins/<name>/"
```

## 8. End-user install (the part you must document)

`codex plugin marketplace add` accepts:

- `owner/repo[@ref]` (GitHub shorthand)
- HTTP(S) Git URLs
- SSH URLs
- local marketplace root directories

Plus options: `--ref <REF>` (pin to branch/tag/commit), `--sparse <PATH>` (filter checkout — see below), `--enable / --disable` (feature flags), `-c key=value` (TOML override).

`marketplace add` only registers or refreshes the marketplace source. Install the plugin in a second step with `codex plugin add <plugin>@<marketplace>`.

### Critical: where Codex looks for `marketplace.json`

When the source is a git URL (or git shorthand), Codex clones into a staging dir and treats the **repo root** as the marketplace root. It then looks for:

```
<staging-root>/.agents/plugins/marketplace.json
```

`--sparse <PATH>` filters the checkout but does **NOT** rebase the marketplace root inside `<PATH>`. Empirically (Codex CLI as of 2026-05): even with `--sparse codex`, the staging dir still contains repo-root files, and Codex looks for the manifest at staging root, not at `staging/codex/`. So `--sparse <PATH>` alone is not enough to make a `<repo>/codex/.agents/plugins/marketplace.json` reachable via git install.

> **Resolved (2026-09, loader `rust-v0.156.1`; still true at `rust-v0.161.0`):** `git-subdir` is a source type for a *plugin entry*, not a way to relocate the marketplace root. Marketplace discovery only looks at root-relative paths (the §1 lookup order), so `marketplace add <git-url>` still needs the repo-root Layout A catalog. `git-subdir` is for a *different* catalog repo pointing at `codex/plugins/<plugin>`. Whether `--sparse` rebases the root remains *(unpublished)*; the loader matches the 2026-05 empirical finding above.

### After install: enabling, disabling, updating

- The Codex CLI has `codex plugin add | list | remove` and `codex plugin marketplace add | list | upgrade | remove` — **no enable/disable command**. Toggle a plugin in `config.toml`: `[plugins."<plugin>@<marketplace>"] enabled = true|false`.
- `codex plugin marketplace upgrade <marketplace>` refreshes a git marketplace; the plugin cache is keyed by the manifest version (see [`plugin-mapping.md`](plugin-mapping.md) §8), so publish a version bump with every change.
- Claude's equivalents (`claude plugin install | enable | disable | update`, `claude plugin marketplace add | update`) differ — write the two install sections separately in the README.

### Two layouts that actually work

**Layout A — marketplace at repo root (recommended for monorepo)**

The published Claude+Codex monorepo keeps a Codex catalog at repo root pointing into the codex/ subtree:

```
<repo>/.agents/plugins/marketplace.json     ← Codex finds this on git clone
└── plugins[].source.path: "./codex/plugins/<plugin-name>"

<repo>/codex/plugins/<plugin-name>/plugin.json
<repo>/codex/plugins/<plugin-name>/skills/...
```

End-user install:

```bash
codex plugin marketplace add <git-url>
codex plugin add <plugin-name>@<marketplace-name>
```

**Layout B — marketplace inside the variant subtree (local-path or dedicated branch)**

The codex/ subtree is also self-contained as its own marketplace root:

```
<repo>/codex/.agents/plugins/marketplace.json    ← local-path install
<repo>/codex/plugins/<plugin-name>/plugin.json
```

End-user install:

```bash
codex plugin marketplace add /local/path/to/codex
codex plugin add <plugin-name>@<marketplace-name>
```

Alternatively, push the codex/ subtree as a dedicated branch and register it with `--ref <branch>` before the `plugin add` step.

### Which catalogs to maintain

Both layouts are hand-maintained. A monorepo that installs from a git URL needs Layout A (and must keep it, or Codex falls back to the Claude catalog — §1); Layout B is optional for local-path installs. The optional script draft emits Layout B inside its scratch output only.

```bash
# Layout A end-user install
codex plugin marketplace add https://example.com/owner/repo.git
codex plugin add <plugin>@<marketplace>
codex plugin marketplace add https://example.com/owner/repo.git --ref v1.2.3   # pinned
codex plugin add <plugin>@<marketplace>

# Layout B end-user install (requires local clone or codex-only branch)
codex plugin marketplace add /local/path/to/repo/codex
codex plugin add <plugin>@<marketplace>
```

Document the chosen layout's exact incantation in the consuming project's README — `codex plugin marketplace add --help` does not describe these path conventions and `--sparse` does not do what its name suggests.
