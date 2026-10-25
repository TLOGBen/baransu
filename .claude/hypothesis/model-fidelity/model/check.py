"""Run every check of the model-fidelity area and print one line per configuration.

usage: python model/check.py <path to tla2tools.jar>
Each configuration is its own TLC run (TLC stops at the first violation), with one
worker so a counterexample is the same on every run; scratch output goes to the
system temp dir.
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

AREA = Path(__file__).resolve().parent.parent
MODULE = "Fidelity.tla"

# (config file relative to the area, what it shows, expected: held | violated)
RUNS = [
    ("model/Facts-R1.cfg",          "8.27.0 照寫的流程：說守住時是真的嗎", "held"),
    ("model/Facts-R2.cfg",          "8.27.0 照寫的流程：說被打破時是真的嗎", "held"),
    ("model/Facts-R3.cfg",          "8.27.0 照寫的流程：重播之後說被打破時", "held"),
    ("model/Compare-R1.cfg",        "8.27.0 程式對程式的比對：說守住時", "held"),
    ("model/Compare-R2.cfg",        "8.27.0 程式對程式的比對：說被打破時", "held"),
    ("model/Compare-R3.cfg",        "8.27.0 程式對程式的比對：重播之後說被打破時", "held"),
    ("model/FactsUser-R1.cfg",      "使用者熟程式、agent 有同樣盲點：說守住時", "held"),
    ("model/Doc-R1.cfg",            "來源是文件：說守住時", "held"),
    ("model/Doc-R2.cfg",            "來源是文件：說被打破時（由 agent 拿原文重播）", "held"),
    ("model/Doc-R3.cfg",            "來源是文件：重播之後說被打破時", "held"),
    ("model/Facts-G1.cfg",          "目標：找到真的問題並成立", "violated"),
    ("model/Facts-G2.cfg",          "目標：沒問題的程式成立為守住", "violated"),
    ("variants/V826-R1.cfg",        "壞掉的版本：8.26.0 的流程（只有兩道門檻）", "violated"),
    ("variants/Blind2-R1.cfg",      "壞掉的版本：只盲抽比對、沒有清單", "violated"),
    ("variants/SharedChecker-R1.cfg", "壞掉的版本：使用者不熟、agent 有同樣盲點", "violated"),
    ("variants/R2-NoReplay.cfg",    "壞掉的版本：不重播就成立（8.27.0 草稿的寫法）", "violated"),
    ("variants/R3-NoReplay.cfg",    "壞掉的版本：不重播", "violated"),
    ("variants/G1-NoGates.cfg",     "拿掉「通過門檻」這一步，目標 1", "held"),
    ("variants/G2-NoGates.cfg",     "拿掉「通過門檻」這一步，目標 2", "held"),
]


def main():
    jar = sys.argv[1]
    out_lines, ok = [], True
    for cfg, what, expected in RUNS:
        cfg_path = AREA / cfg
        meta = Path(tempfile.gettempdir()) / "tlc-model-fidelity" / cfg_path.stem
        # with a transition removed the run stops half-way on purpose: not a deadlock to report
        stop = ["-deadlock"] if "NoGates" in cfg else []
        cmd = ["java", "-cp", jar, "tlc2.TLC", "-workers", "1", *stop, "-metadir", str(meta),
               "-config", str(cfg_path.relative_to(AREA / "model", walk_up=True)), MODULE]
        r = subprocess.run(cmd, cwd=AREA / "model", capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        text = r.stdout + r.stderr
        if re.search(r"Invariant \w+ is violated", text):
            got = "violated"
        elif "No error has been found" in text:
            got = "held"
        else:
            got = "error"
        m = re.findall(r"([\d,]+) distinct states found", text)
        states = m[-1] if m else "?"
        mark = "ok" if got == expected else "UNEXPECTED"
        ok &= got == expected
        line = f"{cfg:<30} {got:<9} {states:>5} states  [{mark}]  {what}"
        print(line)
        out_lines.append(f"===== {cfg} =====\n$ {' '.join(cmd)}\n{text}")
    (AREA / "check.txt").write_text("\n".join(out_lines), encoding="utf-8")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
