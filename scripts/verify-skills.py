#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify-skills.py — baransu 結構驗證器（一條命令證明 C1/C2/C3/C6）。

Repo mode（無參數）執行全部檢查：
  1. plugins/baransu/skills/ 技能目錄數 = 15（_shared/ 除外，且每目錄有 SKILL.md）
  2. SKILL.md frontmatter 可解析（think 極簡式 / read-learn 完整式皆容納）
     ＋官方細目：name ≤64 字元小寫連字符、name == 目錄名、name 無保留字
     （anthropic/claude）、description 非空 ≤1024、第三人稱啟發式、
     description/when_to_use 無 XML tags、兩者合計 ≤1536 字元（listing 預算）
  3. SKILL.md 引用的 references/ 檔存在，且 references/ 內不得再巢狀 references/
  4. 被裁名稱（grade/triage/bridge/dev）word-boundary 零功能殘留
     （掃描面與排除規則內嵌於本腳本，見 RESIDUE_* 常數；git 歷史不掃）
  5. 三發行面（plugin.json / marketplace.json / codex 鏡像）version 一致
  6. Outcome Contract 四行（Outcome / Done when / Evidence / Output）齊備且值非空
  7. 契約區塊第五行 Automation 標注存在且值非空
  8. README「核心理念」理念表逐條錨點存在（條款綁機制）
  9. plugins/baransu/agents/*.md frontmatter 不得含被靜默忽略欄位
     （hooks / mcpServers / permissionMode — plugin agent 官方忽略，寫了即
     silent no-op）
 10. loop-pauses 註冊表完備（loop=drivable/assisted 技能須出貨
     references/loop-pauses.md 且在 _shared/loop-contract.md §4 註冊；
     無孤兒檔、無死鏈；變體見 check_loop_pauses docstring）
 11. green_proof 欄位名跨檔一致（四鍵 × 四發行面；stale 變體
     run_command 全面禁、passed/collected 僅在 green_proof 語境內禁）

Advisory（不影響 exit code）：SKILL.md 本文 >500 行清單（官方上限）；repo mode 另印 15 skill description+when_to_use
總量，超過 LISTING_TOTAL_ADVISORY 時印警示行（見 LISTING_* 常數註記）。

Skills-root mode（一個位置參數 = 含技能目錄的根目錄）：只跑 per-skill 檢查
（2/3/6/7）。供負向 fixture 測試證明可證偽性
（tests/scripts/test_verify_skills.py）。

Agents mode（--agents <目錄>）：只跑檢查 9。同樣供負向 fixture 測試。

Loop-registry mode（--loop-registry <skills 根目錄>）：只跑檢查 10。
Green-proof mode（--green-proof <repo 根目錄>）：只跑檢查 11。
兩者皆供負向 fixture 測試（tests/scripts/test_verify_skills_gates.py）。

Exit 語義（沿用倉內 gate 慣例）：
  0 = pass
  1 = violation（收集後一次輸出全部，不 fail-fast）
  2 = structural（檔案無法解析，指名路徑）

標準函式庫 only。
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = REPO_ROOT / "plugins" / "baransu" / "skills"
AGENTS_DIR = REPO_ROOT / "plugins" / "baransu" / "agents"
PLUGIN_MANIFEST = REPO_ROOT / "plugins" / "baransu" / ".claude-plugin" / "plugin.json"
MARKETPLACE_MANIFEST = REPO_ROOT / ".claude-plugin" / "marketplace.json"
CODEX_MANIFEST = REPO_ROOT / "codex" / "plugins" / "baransu" / ".codex-plugin" / "plugin.json"

EXPECTED_SKILL_COUNT = 15
BODY_LINE_ADVISORY_LIMIT = 500

# 官方 frontmatter 細目
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
NAME_MAX = 64
DESCRIPTION_MAX = 1024
# name 保留字與 description/when_to_use XML tag：官方驗證直接拒收
NAME_RESERVED_WORDS = ("anthropic", "claude")
XML_TAG_RE = re.compile(r"<[^>]+>")
# listing 預算（來源版本 v2.1.x，兩數皆 settings 可調、非絕對真理：per-skill
# 上限為 skillListingMaxDescChars 預設 1536；總量門檻取 200k context 預設 1%
# listing 預算 ≈2,000 tokens ≈7,000 字元）。動工基線總量 7,198 字元
# （2026-07-02；B1 角括號修復後實測 7,190）——總量警示立即觸發屬刻意設計，
# advisory 不影響 exit code。
LISTING_COMBINED_MAX = 1536
LISTING_TOTAL_ADVISORY = 7000
# plugin agent frontmatter 被官方靜默忽略的欄位（出現即 silent no-op 回歸）
AGENT_IGNORED_KEYS = ("hooks", "mcpServers", "permissionMode")
# 第三人稱啟發式：description 不得以第一人稱開頭（引文中的 "I want to build X"
# 屬觸發例句，不算）。
FIRST_PERSON_RE = re.compile(r"^(?:I|I'm|I've|My|We|We're|Our)\b")

# Outcome Contract 四行 + 第五行 Automation 標注
CONTRACT_KEYS = ("Outcome", "Done when", "Evidence", "Output")
AUTOMATION_KEY = "Automation"

# ---------------------------------------------------------------------------
# 檢查 10：loop-pauses 註冊表（常數）
# ---------------------------------------------------------------------------
# Automation 行的 loop= 值（drivable / assisted / not-drivable）
LOOP_VALUE_RE = re.compile(r"\*\*Automation\*\*:[^\n]*\bloop=([a-z-]+)")
# §4 註冊表列的唯一合法格式：| /<name> | `../<name>/references/loop-pauses.md` |
LOOP_ROW_CANON_RE = re.compile(
    r"^\|\s*/([a-z0-9-]+)\s*\|\s*`\.\./([a-z0-9-]+)/references/loop-pauses\.md`\s*\|\s*$"
)
# 無豁免：所有 loop=drivable/assisted 技能一律須出貨 loop-pauses.md＋§4 註冊列
# （codex-skill-transfer 的歷史豁免已於補齊該檔＋註冊列後移除）。

# ---------------------------------------------------------------------------
# 檢查 11：green_proof 欄位名跨檔一致（常數）
# ---------------------------------------------------------------------------
GREEN_PROOF_KEYS = ("test_command", "exit_code", "output_tail", "tests_correspondence")
GREEN_PROOF_FILES = (
    "plugins/baransu/agents/review-agent.md",
    "plugins/baransu/skills/analyze/references/green-proof-verify.md",
    "plugins/baransu/skills/analyze/references/orchestration-interface.md",
    "plugins/baransu/skills/analyze/references/output-formats.md",
)
# stale 變體：run_command 夠特定 → 四檔內任何位置皆禁；passed / collected 太
# 泛用（output-formats.md 的 e2e_evidence 區塊合法使用、green-proof-verify.md
# 有 "a passed review" 散文）→ 僅在 green_proof 語境內禁：
#   (a) `green_proof:` 區塊（YAML 縮排範圍）內的 key 行；
#   (b) `green_proof.<stale>` 點記法引用。
GREEN_PROOF_STALE_ANYWHERE_RE = re.compile(r"\brun_command\b")
GREEN_PROOF_STALE_BLOCK_KEYS = frozenset({"run_command", "passed", "collected"})
GREEN_PROOF_BLOCK_HEADER_RE = re.compile(r"^(\s*)green_proof:\s*$")
GREEN_PROOF_KEY_LINE_RE = re.compile(r"^\s*([A-Za-z_]+)\s*:")
GREEN_PROOF_DOTTED_STALE_RE = re.compile(r"\bgreen_proof\.(run_command|passed|collected)\b")

# SKILL.md 內 references/ 路徑 token（排除常見定界與 CJK 標點；含 {*$<} 之類
# 模板字樣的 token 略過不查）
REF_TOKEN_RE = re.compile(r"references/[^\s`'\"()\[\]{}<>,;|，。：、」（）]+")
# 行內含廢除/移除字樣 → 該行的 references/ 提及屬歷史說明，不查存在性
# （如 design SKILL.md 對 v1.2 已廢除目錄 references/cores/ 的說明句）
REF_DEPRECATION_LINE_RE = re.compile(r"已廢除|已移除|deprecated|removed")

# ---------------------------------------------------------------------------
# 殘留掃描（C2）：被裁名稱 word-boundary 零功能殘留
#
# 掃描面（內嵌，不外部設定）：
#   plugins/**/*.{md,py,json} + tests/**/*.{md,py,json} + CLAUDE.md +
#   README.md + 雙 manifest；git 歷史不掃。
#   副檔名集合 {md,py,json} 同樣適用於 tests/ —— .sh gate 腳本（如
#   tests/integration/test-distribution-metadata.sh）以字面列舉被裁名稱來
#   「檢查其不存在」，屬 meta-checker 而非殘留。
#   tests/**/fixtures/** 整體排除：fixture 為刻意構造的測試輸入
#   （含本驗證器自己的 bad-skill stub，以及 TASK-verify-02 排程修剪的
#   tdd-trigger dogfood 文件），非發行面。
#
# 白名單（residue-scan-classification.md 與兩輪 review 已落盤的同形/歷史例）：
#   命中行若符合任一規則即排除並計數；分類計數隨輸出落盤，
#   不以「grep 無輸出」單獨作為 C2 證據。
# ---------------------------------------------------------------------------
REMOVED_NAMES_RE = re.compile(r"\b(?:grade|triage|bridge|dev)\b")
RESIDUE_SCAN_EXTS = {".md", ".py", ".json"}

# (label, path-suffix 或 None=不限路徑, line regex)
RESIDUE_WHITELIST = (
    ("shell 裝置路徑 /dev/*", None, re.compile(r"/dev/")),
    (".dev 網域外部 URL", None, re.compile(r"\.dev\b")),
    ("support-triage 一般詞", None, re.compile(r"support-triage")),
    ("color grade 攝影詞", None, re.compile(r"color grade")),
    ("可變字型 grade 軸", None, re.compile(r"\bgrade \(")),
    ("Codex CLI bridge 一般詞", None, re.compile(r"Codex CLI bridge")),
    (
        "agent-mapping.md 歷史例句",
        "codex-skill-transfer/references/agent-mapping.md",
        re.compile(r"investigator-agent"),
    ),
    (
        "transfer.py 歷史註解",
        "codex-skill-transfer/scripts/transfer.py",
        re.compile(r"CRON\.md"),
    ),
)


class Structural(Exception):
    """檔案無法解析 — exit 2，指名路徑。"""


# ---------------------------------------------------------------------------
# frontmatter 解析（無第三方依賴的最小 YAML 子集：inline scalar、引號 scalar、
# block scalar（> | >- |- 等）、巢狀 mapping（如 metadata: 只收不驗））
# ---------------------------------------------------------------------------
def parse_skill_md(path: Path):
    """回傳 (frontmatter dict, body 行列表)。無法解析 → Structural。"""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise Structural(f"{path}: 無法讀取（{exc}）")

    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise Structural(f"{path}: 缺少 frontmatter 起始 '---'")
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        raise Structural(f"{path}: 缺少 frontmatter 結束 '---'")

    fm_lines = lines[1:end]
    body = lines[end + 1:]
    data: dict[str, str] = {}
    i = 0
    while i < len(fm_lines):
        line = fm_lines[i]
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue
        if line[0] in (" ", "\t"):
            # 上一個 key 的巢狀 mapping 子行（如 metadata: 下的 author:）—
            # 收下不驗。
            i += 1
            continue
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if m is None:
            raise Structural(f"{path}: frontmatter 第 {i + 2} 行無法解析：{line!r}")
        key, val = m.group(1), m.group(2).strip()
        if val in (">", "|", ">-", "|-", ">+", "|+"):
            block: list[str] = []
            i += 1
            while i < len(fm_lines) and (
                not fm_lines[i].strip() or fm_lines[i][0] in (" ", "\t")
            ):
                if fm_lines[i].strip():
                    block.append(fm_lines[i].strip())
                i += 1
            data[key] = " ".join(block)
            continue
        if len(val) >= 2 and val[0] == val[-1] and val[0] in ("'", '"'):
            val = val[1:-1]
        data[key] = val
        i += 1
    return data, body


# ---------------------------------------------------------------------------
# per-skill 檢查（2/3/6/7 + advisory）
# ---------------------------------------------------------------------------
def check_frontmatter(skill: Path, fm: dict) -> list[str]:
    v = []
    name = fm.get("name", "")
    desc = fm.get("description", "")
    wtu = fm.get("when_to_use", "")
    if not name:
        v.append(f"{skill.name}: frontmatter 缺 name")
    else:
        if len(name) > NAME_MAX:
            v.append(f"{skill.name}: name 超過 {NAME_MAX} 字元（{len(name)}）")
        if not NAME_RE.match(name):
            v.append(f"{skill.name}: name 非小寫連字符格式：{name!r}")
        if name != skill.name:
            v.append(
                f"{skill.name}: frontmatter name ≠ 目錄名：{name!r} ≠ {skill.name!r}"
            )
        for word in NAME_RESERVED_WORDS:
            if word in name.lower():
                v.append(f"{skill.name}: name 含保留字 {word!r}（官方驗證拒收）")
    if not desc:
        v.append(f"{skill.name}: description 空白或缺漏")
    else:
        if len(desc) > DESCRIPTION_MAX:
            v.append(
                f"{skill.name}: description 超過 {DESCRIPTION_MAX} 字元（{len(desc)}）"
            )
        if FIRST_PERSON_RE.match(desc):
            v.append(f"{skill.name}: description 以第一人稱開頭（須第三人稱）")
    for field, value in (("description", desc), ("when_to_use", wtu)):
        m = XML_TAG_RE.search(value)
        if m:
            v.append(
                f"{skill.name}: {field} 含 XML tag：{m.group(0)!r}（官方驗證拒收）"
            )
    combined = len(desc) + len(wtu)
    if combined > LISTING_COMBINED_MAX:
        v.append(
            f"{skill.name}: description+when_to_use 合計 {combined} 字元 > "
            f"{LISTING_COMBINED_MAX}（listing 預算硬上限，v2.1.x 預設）"
        )
    return v


def check_references(skill: Path, body: list[str]) -> list[str]:
    v = []
    siblings = [d for d in skill.parent.iterdir() if d.is_dir()] if skill.parent.is_dir() else []
    seen: set[str] = set()
    for line in body:
        if REF_DEPRECATION_LINE_RE.search(line):
            continue  # 廢除說明句中的歷史路徑，不查存在性
        for tok in REF_TOKEN_RE.findall(line):
            tok = tok.rstrip(".,:;")
            if any(c in tok for c in "{*$<") or tok == "references/" or tok in seen:
                continue  # 模板字樣 / 純目錄提及 / 已查過
            seen.add(tok)
            # 先以本技能目錄解析；落空時容許跨技能 anchor-cite
            # （如 learn 引用 read 的 references/acquisition/*.md）
            exists_somewhere = any(
                (d / tok).is_dir() if tok.endswith("/") else (d / tok).exists()
                for d in [skill] + siblings
            )
            if not exists_somewhere:
                kind = "目錄" if tok.endswith("/") else "檔案"
                v.append(f"{skill.name}: SKILL.md 引用的{kind}不存在：{tok}")
    refs_dir = skill / "references"
    if refs_dir.is_dir():
        for p in refs_dir.rglob("references"):
            if p.is_dir():
                v.append(
                    f"{skill.name}: references/ 內巢狀 references/："
                    f"{p.relative_to(skill)}"
                )
    return v


def check_contract(skill: Path, body: list[str]) -> list[str]:
    idx = next(
        (i for i, l in enumerate(body) if l.strip() == "## Outcome Contract"), None
    )
    if idx is None:
        return [f"{skill.name}: SKILL.md 缺 '## Outcome Contract' 區塊"]
    section: list[str] = []
    for l in body[idx + 1:]:
        if l.startswith("## "):
            break
        section.append(l)
    v = []
    for key in CONTRACT_KEYS + (AUTOMATION_KEY,):
        pat = re.compile(r"^\s*-\s*\*\*" + re.escape(key) + r"\*\*:\s*(.*)$")
        hit = next((m for l in section if (m := pat.match(l))), None)
        if hit is None:
            v.append(f"{skill.name}: Outcome Contract 缺 '{key}' 行")
        elif not hit.group(1).strip():
            v.append(f"{skill.name}: Outcome Contract '{key}' 值為空")
    return v


def check_skill(skill: Path):
    """回傳 (violations, body_line_count, listing_chars)。"""
    skill_md = skill / "SKILL.md"
    if not skill_md.is_file():
        return [f"{skill.name}: 缺 SKILL.md"], 0, 0
    fm, body = parse_skill_md(skill_md)
    v = []
    v += check_frontmatter(skill, fm)
    v += check_references(skill, body)
    v += check_contract(skill, body)
    listing = len(fm.get("description", "")) + len(fm.get("when_to_use", ""))
    return v, len(body), listing


# ---------------------------------------------------------------------------
# repo-level 檢查（1/4/5）
# ---------------------------------------------------------------------------
def iter_residue_files():
    for base in ("plugins", "tests"):
        root = REPO_ROOT / base
        if not root.is_dir():
            continue
        for p in sorted(root.rglob("*")):
            if not p.is_file() or p.suffix not in RESIDUE_SCAN_EXTS:
                continue
            rel = p.relative_to(REPO_ROOT).as_posix()
            if "/__pycache__/" in rel or "/node_modules/" in rel:
                continue
            if base == "tests" and "/fixtures/" in rel:
                continue
            yield p
    for extra in ("CLAUDE.md", "README.md"):
        p = REPO_ROOT / extra
        if p.is_file():
            yield p
    if MARKETPLACE_MANIFEST.is_file():
        yield MARKETPLACE_MANIFEST


def line_whitelisted(rel: str, line: str):
    for label, suffix, pat in RESIDUE_WHITELIST:
        if suffix is not None and not rel.endswith(suffix):
            continue
        if pat.search(line):
            return label
    return None


def check_residue():
    v = []
    excluded: dict[str, int] = {}
    for path in iter_residue_files():
        rel = path.relative_to(REPO_ROOT).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            raise Structural(f"{path}: 無法讀取（{exc}）")
        for n, line in enumerate(text.splitlines(), 1):
            m = REMOVED_NAMES_RE.search(line)
            if m is None:
                continue
            label = line_whitelisted(rel, line)
            if label is not None:
                excluded[label] = excluded.get(label, 0) + 1
            else:
                v.append(f"殘留：{rel}:{n}: '{m.group(0)}' → {line.strip()[:80]}")
    return v, excluded


def check_manifest_versions():
    versions = {}
    for path in (PLUGIN_MANIFEST, MARKETPLACE_MANIFEST):
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise Structural(f"{path}: 無法解析（{exc}）")
        if path is PLUGIN_MANIFEST:
            versions["plugin.json"] = doc.get("version")
        else:
            # marketplace.json 的 version 位於 metadata.version；
            # plugin entry 若另帶 version 欄則優先比對該欄
            entry = next(
                (e for e in doc.get("plugins", []) if e.get("name") == "baransu"),
                {},
            )
            versions["marketplace.json"] = entry.get("version") or doc.get(
                "metadata", {}
            ).get("version")
    # 第三發行面：codex 鏡像 manifest（由 transfer.py 重產；缺檔即違規，
    # 因為鏡像是發行物的一部分，不可在 bump 後遺留舊版）
    try:
        codex_doc = json.loads(CODEX_MANIFEST.read_text(encoding="utf-8"))
        versions["codex"] = codex_doc.get("version")
    except (OSError, json.JSONDecodeError) as exc:
        return [f"codex 鏡像 manifest 無法讀取（{CODEX_MANIFEST}: {exc}）"], None
    distinct = {repr(v) for v in versions.values()}
    if len(distinct) > 1:
        return [
            "三發行面 version 不一致："
            f"plugin.json={versions['plugin.json']!r} vs "
            f"marketplace.json={versions['marketplace.json']!r} vs "
            f"codex={versions['codex']!r}"
        ], None
    return [], versions["plugin.json"]


def check_agents(agents_dir: Path) -> list[str]:
    """agents/*.md frontmatter 不得含被靜默忽略欄位（檢查 9）。

    hooks / mcpServers / permissionMode 對 plugin agent 為官方忽略欄位——
    寫了不生效也不報錯，屬 silent no-op 回歸，故在此擋下。
    """
    if not agents_dir.is_dir():
        raise Structural(f"{agents_dir}: agents 目錄不存在")
    v = []
    for path in sorted(agents_dir.glob("*.md")):
        fm, _ = parse_skill_md(path)
        for key in AGENT_IGNORED_KEYS:
            if key in fm:
                v.append(
                    f"{path.name}: agent frontmatter 含被靜默忽略欄位 {key!r}"
                    "（plugin agent 官方忽略 hooks/mcpServers/permissionMode）"
                )
    return v


# ---------------------------------------------------------------------------
# 檢查 10：loop-pauses 註冊表完備
# ---------------------------------------------------------------------------
def check_loop_pauses(skills_root: Path) -> list[str]:
    """loop-pauses 註冊表完備（檢查 10）。

    編碼變體（校準至 2026-07-10 HEAD 現狀，取「能通過現狀的最嚴規則」）：
      a. loop=drivable / loop=assisted 技能 MUST 出貨
         references/loop-pauses.md 且在 _shared/loop-contract.md §4 有
         canonical 註冊列 —— 無豁免。
      b. loop=not-drivable 免出貨，但「若出貨即須註冊」（think 現狀：
         not-drivable、有檔、有註冊列 —— 故孤兒規則適用於所有技能）。
      c. 反向：每一註冊列必須指向存在的檔案（無死鏈），列內 /<name> 與
         路徑 <name> 必須一致，且列格式必須完全符合
         `| /<name> | ../<name>/references/loop-pauses.md |`（反引號路徑）。
    """
    contract = skills_root / "_shared" / "loop-contract.md"
    try:
        contract_text = contract.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise Structural(f"{contract}: 無法讀取（{exc}）")

    v: list[str] = []
    registered: set[str] = set()
    for n, line in enumerate(contract_text.splitlines(), 1):
        if "loop-pauses.md" not in line or not line.lstrip().startswith("|"):
            continue
        m = LOOP_ROW_CANON_RE.match(line.strip())
        if m is None:
            v.append(
                f"loop-contract.md:{n}: 註冊列格式不符 canonical "
                f"`| /<name> | ../<name>/references/loop-pauses.md |`：{line.strip()[:80]}"
            )
            continue
        row_name, path_name = m.group(1), m.group(2)
        if row_name != path_name:
            v.append(
                f"loop-contract.md:{n}: 註冊列 /{row_name} 與路徑技能名 "
                f"{path_name!r} 不一致"
            )
            continue
        registered.add(row_name)
        if not (skills_root / path_name / "references" / "loop-pauses.md").is_file():
            v.append(
                f"loop-contract.md:{n}: 註冊列 /{row_name} 指向不存在的檔案"
                f"（死鏈）：{path_name}/references/loop-pauses.md"
            )

    for skill in discover_skills(skills_root):
        skill_md = skill / "SKILL.md"
        if not skill_md.is_file():
            continue  # 缺 SKILL.md 由檢查 1 負責
        try:
            text = skill_md.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            raise Structural(f"{skill_md}: 無法讀取（{exc}）")
        m = LOOP_VALUE_RE.search(text)
        loop = m.group(1) if m else None
        has_file = (skill / "references" / "loop-pauses.md").is_file()
        required = loop in ("drivable", "assisted")
        if required and not has_file:
            v.append(
                f"{skill.name}: loop={loop} 但缺 references/loop-pauses.md"
                "（drivable/assisted 必須出貨 PAUSE 分類表）"
            )
        if required and skill.name not in registered:
            v.append(
                f"{skill.name}: loop={loop} 但 _shared/loop-contract.md §4 "
                "無註冊列"
            )
        if has_file and skill.name not in registered:
            v.append(
                f"{skill.name}: 出貨了 references/loop-pauses.md 但未在 "
                "_shared/loop-contract.md §4 註冊（孤兒檔）"
            )
    return v


# ---------------------------------------------------------------------------
# 檢查 11：green_proof 欄位名跨檔一致
# ---------------------------------------------------------------------------
def check_green_proof(repo_root: Path) -> list[str]:
    """green_proof 欄位名跨檔一致（檢查 11）。

    四鍵（GREEN_PROOF_KEYS）必須逐一出現在全部四個發行面
    （GREEN_PROOF_FILES）；stale 變體按 GREEN_PROOF_STALE_* 常數註記的
    範圍禁用（run_command 全面禁；passed/collected 僅 green_proof 語境）。
    """
    v: list[str] = []
    for rel in GREEN_PROOF_FILES:
        path = repo_root / rel
        if not path.is_file():
            v.append(f"green_proof 發行面檔案不存在：{rel}")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            raise Structural(f"{path}: 無法讀取（{exc}）")
        short = Path(rel).name
        for key in GREEN_PROOF_KEYS:
            if re.search(rf"\b{key}\b", text) is None:
                v.append(f"{short}: green_proof 鍵 {key!r} 未出現（四鍵四檔一致性）")
        block_indent: int | None = None
        for n, line in enumerate(text.splitlines(), 1):
            if GREEN_PROOF_STALE_ANYWHERE_RE.search(line):
                v.append(f"{short}:{n}: stale green_proof 欄位名 'run_command'")
            dm = GREEN_PROOF_DOTTED_STALE_RE.search(line)
            if dm:
                v.append(
                    f"{short}:{n}: stale green_proof 點記法引用 "
                    f"'green_proof.{dm.group(1)}'"
                )
            hm = GREEN_PROOF_BLOCK_HEADER_RE.match(line)
            if hm:
                block_indent = len(hm.group(1))
                continue
            if block_indent is None or not line.strip():
                continue
            indent = len(line) - len(line.lstrip())
            if indent <= block_indent:
                block_indent = None
                continue
            km = GREEN_PROOF_KEY_LINE_RE.match(line)
            if km and km.group(1) in GREEN_PROOF_STALE_BLOCK_KEYS:
                v.append(
                    f"{short}:{n}: green_proof 區塊內 stale 欄位名 "
                    f"{km.group(1)!r}"
                )
    return v


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def check_philosophy_anchors() -> list[str]:
    """README「核心理念」段：理念表每列須含 ≥1 個存在於倉內的機制錨點路徑。

    條款綁機制（v2.1.0 KD4）：無錨點的理念條不入冊；錨點以反引號路徑表示，
    存在性在此機器驗證 — 防止理念段退化為口號。
    """
    readme = REPO_ROOT / "README.md"
    try:
        text = readme.read_text(encoding="utf-8")
    except OSError as exc:
        raise Structural(f"{readme}: 無法讀取（{exc}）")
    lines = text.splitlines()
    try:
        start = next(i for i, l in enumerate(lines) if l.strip() == "## 核心理念")
    except StopIteration:
        return ["README.md 缺「## 核心理念」段（理念成文為 v2.1.0 驗收項）"]
    end = next(
        (i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")),
        len(lines),
    )
    v: list[str] = []
    rows = 0
    for line in lines[start:end]:
        s = line.strip()
        if not s.startswith("|"):
            continue
        if set(s.replace("|", "").strip()) <= {"-", " ", ":"}:
            continue  # separator row
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) < 3 or cells[0] in ("理念", ""):
            continue
        rows += 1
        anchors = re.findall(r"`([^`]+)`", s)
        paths = [a for a in anchors if "/" in a or a.endswith(".py") or a.endswith(".md")]
        if not paths:
            v.append(f"理念條「{cells[0]}」無機制錨點路徑（條款綁機制：無錨點不入冊）")
            continue
        if not any((REPO_ROOT / p).exists() for p in paths):
            v.append(f"理念條「{cells[0]}」錨點不存在於倉內：{paths}")
    if rows == 0:
        v.append("README「核心理念」段無理念表列（預期 ≥1 列、每列含機制錨點）")
    return v


def discover_skills(root: Path) -> list[Path]:
    if not root.is_dir():
        raise Structural(f"{root}: 技能根目錄不存在")
    return sorted(
        d for d in root.iterdir() if d.is_dir() and d.name != "_shared"
    )


def main(argv: list[str]) -> int:
    agents_mode = len(argv) >= 3 and argv[1] == "--agents"
    loop_mode = len(argv) >= 3 and argv[1] == "--loop-registry"
    green_mode = len(argv) >= 3 and argv[1] == "--green-proof"
    flag_mode = agents_mode or loop_mode or green_mode
    repo_mode = len(argv) < 2
    skills_root = SKILLS_DIR if (repo_mode or flag_mode) else Path(argv[1]).resolve()

    violations: list[str] = []
    oversize: list[tuple[str, int]] = []
    listing_total = 0

    try:
        skills = [] if flag_mode else discover_skills(skills_root)

        if repo_mode and len(skills) != EXPECTED_SKILL_COUNT:
            violations.append(
                f"技能目錄數 {len(skills)} ≠ {EXPECTED_SKILL_COUNT}："
                f"{', '.join(d.name for d in skills)}"
            )

        for skill in skills:
            sv, body_count, listing_chars = check_skill(skill)
            listing_total += listing_chars
            if sv:
                violations += sv
            else:
                print(f"✅ {skill.name} — frontmatter / references / 契約四行＋Automation 通過")
            if body_count > BODY_LINE_ADVISORY_LIMIT:
                oversize.append((skill.name, body_count))

        if agents_mode:
            violations += check_agents(Path(argv[2]).resolve())

        if loop_mode:
            violations += check_loop_pauses(Path(argv[2]).resolve())

        if green_mode:
            violations += check_green_proof(Path(argv[2]).resolve())

        if repo_mode:
            rv, excluded = check_residue()
            violations += rv
            if not rv:
                detail = (
                    "、".join(f"{k} ×{n}" for k, n in sorted(excluded.items()))
                    or "無白名單命中"
                )
                print(f"✅ 殘留掃描（被裁名稱 word-boundary）零功能命中；白名單排除：{detail}")
            mv, version = check_manifest_versions()
            violations += mv
            if not mv:
                print(f"✅ 三發行面 version 一致：{version}")
            pv = check_philosophy_anchors()
            violations += pv
            if not pv:
                print("✅ README 理念段逐條錨點存在（條款綁機制）")
            av = check_agents(AGENTS_DIR)
            violations += av
            if not av:
                print(
                    "✅ agents frontmatter 無被靜默忽略欄位"
                    "（hooks/mcpServers/permissionMode）"
                )
            lv = check_loop_pauses(SKILLS_DIR)
            violations += lv
            if not lv:
                print(
                    "✅ loop-pauses 註冊表完備"
                    "（drivable/assisted 檔案＋註冊列、無孤兒、無死鏈）"
                )
            gv = check_green_proof(REPO_ROOT)
            violations += gv
            if not gv:
                print(
                    "✅ green_proof 欄位名跨檔一致"
                    "（4 鍵 × 4 發行面；無 stale 變體）"
                )
            if len(skills) == EXPECTED_SKILL_COUNT:
                print(f"✅ 技能目錄數 = {EXPECTED_SKILL_COUNT}")

    except Structural as exc:
        print(f"STRUCTURAL: {exc}", file=sys.stderr)
        return 2

    for name, count in oversize:
        print(
            f"⚠️ ADVISORY（不影響 exit code）：{name}/SKILL.md 本文 "
            f"{count} 行 > {BODY_LINE_ADVISORY_LIMIT}（官方上限，列入瘦身清單）"
        )

    if repo_mode:
        print(
            f"listing 總量：description+when_to_use 合計 {listing_total} 字元"
            f"（警示門檻 {LISTING_TOTAL_ADVISORY}）"
        )
        if listing_total > LISTING_TOTAL_ADVISORY:
            print(
                f"⚠️ listing 預算警示（不影響 exit code）：總量 {listing_total} 字元 > "
                f"{LISTING_TOTAL_ADVISORY}（200k context 預設 1% ≈2,000 tokens；"
                "v2.1.x settings 可調）"
            )

    if violations:
        print(f"\n❌ 共 {len(violations)} 項違規：")
        for item in violations:
            print(f"  - {item}")
        return 1

    print("\nPASS: verify-skills 全部檢查通過")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
