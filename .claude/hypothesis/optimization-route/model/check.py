"""Run every check of the optimization-route area and print one line per configuration.

usage: python model/check.py <path to tla2tools.jar>
One TLC run per configuration, one worker, scratch output in the system temp dir.
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

AREA = Path(__file__).resolve().parent.parent
MODULE = "OptRoute.tla"

RUNS = [  # (config relative to the area, what it shows, expected)
    ("model/Strict-R1.cfg",  "讀法 A（最佳要差距 0）：說最佳時有證明", "held"),
    ("variants/R1-LooseWording.cfg", "壞掉的版本：修正前的寫法（寫了任何證明就能說最佳）", "violated"),
    ("variants/R1-AtBoundPerPart.cfg", "壞掉的版本：修正前的寫法（每一部分在自己的下界就說整體最佳）", "violated"),
    ("model/Strict-R2.cfg",  "交出去的版本答案沒變", "held"),
    ("model/Strict-R3.cfg",  "只在被要求時才交出新版本", "held"),
    ("model/Strict-G1.cfg",  "目標：交出並證明最佳", "violated"),
    ("model/Strict-G2.cfg",  "目標：交出並附上誠實的下界", "violated"),
    ("variants/R2-NoRecheck.cfg", "壞掉的版本：不重驗正確性", "violated"),
    ("variants/R3-NoAskGate.cfg", "壞掉的版本：沒被要求也照樣最佳化", "violated"),
    ("variants/G1-NoDeliver.cfg", "拿掉「交出」這一步，目標 1", "held"),
    ("variants/G2-NoDeliver.cfg", "拿掉「交出」這一步，目標 2", "held"),
]


def main():
    jar = sys.argv[1]
    out, ok = [], True
    for cfg, what, expected in RUNS:
        meta = Path(tempfile.gettempdir()) / "tlc-optimization-route" / Path(cfg).stem
        stop = ["-deadlock"] if "NoDeliver" in cfg else []
        cmd = ["java", "-cp", jar, "tlc2.TLC", "-workers", "1", *stop, "-metadir", str(meta),
               "-config", "../" + cfg if cfg.startswith("variants/") else Path(cfg).name, MODULE]
        r = subprocess.run(cmd, cwd=AREA / "model", capture_output=True, text=True, encoding="utf-8", errors="replace")
        text = r.stdout + r.stderr
        got = ("violated" if re.search(r"Invariant \w+ is violated", text)
               else "held" if "No error has been found" in text else "error")
        states = (re.findall(r"([\d,]+) distinct states found", text) or ["?"])[-1]
        ok &= got == expected
        print(f"{cfg:<28} {got:<9} {states:>4} states  [{'ok' if got == expected else 'UNEXPECTED'}]  {what}")
        out.append(f"===== {cfg} =====\n$ {' '.join(cmd)}\n{text}")
    (AREA / "check.txt").write_text("\n".join(out), encoding="utf-8")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
