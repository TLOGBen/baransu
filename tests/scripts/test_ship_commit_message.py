from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SHIP_SKILL = REPO_ROOT / "plugins" / "baransu" / "skills" / "ship" / "SKILL.md"


def step_3() -> str:
    text = SHIP_SKILL.read_text(encoding="utf-8")
    return text.split("## Step 3 — Commit", 1)[1].split(
        "## Step 4 — Push", 1
    )[0]


def test_ship_commit_message_summarizes_the_staged_outcome():
    section = step_3()

    assert "chore: 歸檔工作檔案並提交本次變更" not in section
    assert "git diff --cached --name-status" in section
    assert "git diff --cached --stat" in section
    assert "primary shipped outcome" in section
    assert "archived workflow files" in section
    assert "`feat`, `fix`, `refactor`, `docs`, `test`, or `chore`" in section


def test_ship_uses_one_dynamic_message_for_commit_and_report():
    section = step_3()

    assert 'git commit -m "$COMMIT_MESSAGE"' in section
    assert "已提交：{$COMMIT_MESSAGE}" in section
    assert 'COMMIT_MESSAGE="chore: 收尾本次工作"' in section
