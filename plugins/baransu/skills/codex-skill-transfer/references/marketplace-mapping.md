# Marketplace Mapping (`.claude-plugin/marketplace.json` → `.agents/plugins/marketplace.json`)

⚠️ **Not script-automated.** Codex marketplace path locations are documented (`$REPO_ROOT/.agents/plugins/marketplace.json` for repo-level, `~/.agents/plugins/marketplace.json` for user-level) but the **`source` block variants are not fully spec'd** in current OpenAI public docs (only the per-plugin manifest is). This file documents the inline rules for converting by hand.

For automated layers, see [`skill-mapping.md`](skill-mapping.md) (skill files) and [`plugin-mapping.md`](plugin-mapping.md) (plugin manifests).

## 1. Top-level shape

Both formats use the same skeleton:

```json
{
  "name": "<marketplace-id>",
  "owner": { "name": "...", "email": "..." },
  "plugins": [...]
}
```

These three fields port verbatim. Drop `$schema` — Claude's URL (`anthropic.com/claude-code/marketplace.schema.json`) is not actually published, and Codex has no schema URL.

## 2. Per-plugin entry mapping

Pass-through fields (Claude → Codex, same key, same shape):

- `name` — plugin id
- `description` — human-readable
- `author` — `{ "name": "...", "email": "..." }`
- `category` — Claude uses an open string set (`development`, `security`, `productivity`, `database`, `deployment`, `monitoring`, `design`, `learning`); Codex's recognized values are not enumerated, but reasonable strings appear to work.
- `homepage` — URL string

Set explicitly on the Codex side:

- `version` — Claude infers from git host if absent. Codex's behavior is undocumented; prefer setting it explicitly to whatever is in the plugin's own `plugin.json` `version` field.

## 3. Source-block mapping (the uncertain part)

Claude marketplace `source` accepts four variants in production today:

| Claude `source` variant | Codex equivalent (best-effort) | Confidence |
|----|----|----|
| `"./plugins/foo"` (string, local path) | `"./plugins/foo"` (same) | High — local paths are universal |
| `{ "source": "git-subdir", "url": "...", "path": "...", "ref": "...", "sha": "..." }` | likely the same shape | Medium — verify Codex parser accepts |
| `{ "source": "url", "url": "..." }` | likely the same | Medium |
| `{ "source": "github", "repo": "...", "commit": "..." }` | uncertain; may need conversion to `git-subdir` | Low |

**Recommendation when in doubt**: prefer the local-path string form (`"./plugins/foo"`). It's the form most likely supported across Codex versions, and it works whenever the plugin tree ships in the same repo as the marketplace catalog (which is exactly baransu's monorepo layout).

## 4. Drop these fields

- `$schema` — no published target on either side
- `strict` — Claude-specific (controls plugin manifest authority)
- `tags` — Claude-specific
- `lspServers` (per-plugin) — Codex plugins don't host LSP

## 5. Concrete conversion example

A Claude marketplace entry like:

```json
{
  "name": "baransu",
  "description": "Governance skills for deliberate AI workflows",
  "author": { "name": "ben.tsai" },
  "category": "productivity",
  "source": "./plugins/baransu",
  "homepage": "https://example.com/baransu"
}
```

Becomes a Codex marketplace entry:

```json
{
  "name": "baransu",
  "description": "Governance skills for deliberate AI workflows",
  "author": { "name": "ben.tsai" },
  "category": "productivity",
  "source": "./plugins/baransu-codex",
  "homepage": "https://example.com/baransu",
  "version": "1.1.3"
}
```

Differences: (a) `source` path points to the Codex plugin tree (separate dir if running both Claude and Codex from one repo); (b) `version` set explicitly from the plugin's own `plugin.json`.

## 6. Template asset

[`assets/codex-marketplace.template.json`](../assets/codex-marketplace.template.json) is a minimal Codex marketplace catalog with placeholders (`$marketplace_name`, `$owner_name`, `$owner_email`, `$plugin_name`, `$plugin_description`). Use it as a copy-and-fill starting point rather than writing one from memory. The transfer script does **not** auto-fill this template (because of the source-variant uncertainty above) — it's intended for manual use.

## 7. Why this layer is left manual

Three reasons:

1. **Codex source-block spec is incomplete in public docs.** Auto-converting would risk silently producing non-functional catalogs.
2. **Marketplace publication is a deliberate act**, not a side effect of porting individual plugins. The user should review what gets exposed.
3. **One marketplace catalog covers the whole repo**, so the conversion is a one-time task — automating it has low ROI.

When OpenAI publishes a complete marketplace `source` schema, this section should be promoted to script-automated and folded into [`plugin-mapping.md`](plugin-mapping.md).
