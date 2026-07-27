# Codex Stop hook transfer fix — draft

`codex-skill-transfer` 是移植與驗證的關鍵，但實際失效點仍在
`seal-guard.sh` 的 Codex-only 分支。

目前 transfer 的行為是：

- 轉換 `hooks.json` 與 `PLUGIN_ROOT`
- 將 hook scripts 原樣複製到 Codex mirror
- 不解析或改寫 shell script 語意

因此建議這樣改：

1. 在 `seal-guard.sh` 只修改 `PLUGIN_ROOT` 分支，改回傳
   `decision:block`；Claude 的 exit 2 路徑完全不動。
2. 在 `codex-skill-transfer` 更新 Stop 契約文件與 transfer 測試，確保生成結果
   使用正確契約。
3. 將 G11 改成真實 Codex CLI lifecycle 測試，避免只驗 stdout 的假綠。
4. 重新生成 `codex/` mirror，不直接手改 mirror。
5. `commandWindows` 與 PowerShell entrypoint 另開一項；不和這次 Stop 修復綁在一起。

若連 `plugins/baransu/hooks/seal-guard.sh` 都不能修改，就只能讓 transfer 特判並
改寫生成腳本；不採用此方案，因為它會把 baransu-specific shell 語意塞進通用
transfer。

範圍結論：Claude 行為不變，Codex Stop 修復；主要驗收責任放在
`codex-skill-transfer`。
