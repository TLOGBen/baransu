<!-- 此處採預設：合約未經人工確認即釘死 -->
# CONTRACT — Codex plugin hook outcome mirror

## 目標
`codex-skill-transfer` 會把 Claude plugin 可等價的 lifecycle hook 結果帶進 Codex 鏡像，
並對不可等價事件明確拒絕假裝完成。

## 可斷言條文
- [ ] A1: plugin source 有 `hooks/hooks.json` 時，輸出必須有 `hooks/hooks.json` 與 manifest `"hooks": "./hooks/hooks.json"`。
- [ ] A2: Codex 支援且 handler `type` 為 `command` 的事件與 timeout 必須逐值保留。
- [ ] A3: Codex 不支援的 `SessionEnd` 不得被偷換成 `Stop`，且 report 必須逐名列出該事件。
- [ ] A4: 非 `command` handler 不得出現在輸出，且 report 必須逐名列出其 event 與 type。
- [ ] A5: baransu `seal-guard` 在 Claude miss 路徑維持 exit 2 + 繁中 stderr；在 Codex miss 路徑輸出精確 JSON schema 並 exit 0。
- [ ] A6: Codex mirror 的 seal telemetry producer 與 hook consumer 都使用 `~/.codex/baransu/telemetry`，不得讀寫 `~/.claude/baransu/telemetry`。
- [ ] A7: hooks 仍須經 `/hooks` trust；transfer report 不得聲稱安裝即自動受信任。
- [ ] A8: 無 hooks 的 plugin 輸出不得多出 hooks pointer 或 hooks 目錄。

## 錯不起表面（Surface Inventory）
| 表面 | 格式 | 釘死測試 |
|------|------|----------|
| Codex manifest | `"hooks": "./hooks/hooks.json"` | `test_plugin_hooks_are_ported` |
| unsupported event report | `不支援事件：SessionEnd` | `test_plugin_hooks_are_ported` |
| unsupported handler report | `不支援 handler：{event}/{type}` | `test_plugin_hook_drops_non_command_handler` |
| malformed hook report | 必須具名 `hooks/hooks.json` 或 event，並說明 `無法解析` / `不是 array` / `不是 object` | `test_malformed_hook_shapes_are_reported_without_crashing` |
| custom hook source report | 必須含 `自訂來源形狀需人工映射` | `test_manifest_only_hook_shape_is_reported` |
| Codex Stop block | `{"decision":"block","reason":"{message}","systemMessage":"{message}"}`；不得含 `continue` 或 `stopReason` | `G11` |
| Codex telemetry root | `$HOME/.codex/baransu/telemetry`，不得產生 `$HOME/.claude/baransu/telemetry` | `G12` |
| trust notice | 必須含 `/hooks` 與 `trust`，不得含 `預設關閉` | `test_plugin_hooks_are_ported` |

## Verbatim Constants
```text
"hooks": "./hooks/hooks.json"
不支援事件：SessionEnd
{"decision":"block","reason":"{message}","systemMessage":"{message}"}
~/.codex/baransu/telemetry
```
