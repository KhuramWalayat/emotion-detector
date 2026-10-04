"""Save real command output; use --live to also run the Watson checks."""

import argparse
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path
import shlex
import subprocess
import sys


PROJECT = Path(__file__).resolve().parent
EVIDENCE = PROJECT / "evidence"


def record(filename, arguments):
    """Run a command and record its unmodified output and exit status."""
    command = [sys.executable, *arguments]
    completed = subprocess.run(
        command, cwd=PROJECT, text=True, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, check=False,
    )
    output = (
        f"Captured: {datetime.now(timezone.utc).isoformat()}\n"
        f"$ {shlex.join(command)}\n{completed.stdout}\n"
        f"Exit code: {completed.returncode}\n"
    )
    (EVIDENCE / filename).write_text(output, encoding="utf-8")
    print(output, flush=True)
    return completed.returncode


def main():
    """Collect local evidence and optional real-service evidence separately."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Also call Watson NLP")
    arguments = parser.parse_args()
    EVIDENCE.mkdir(exist_ok=True)
    environment = [f"Python: {sys.version}", f"Executable: {sys.executable}"]
    for package in ("Flask", "requests", "pylint"):
        environment.append(f"{package}: {version(package)}")
    (EVIDENCE / "01_environment.txt").write_text(
        "\n".join(environment) + "\n", encoding="utf-8"
    )

    checks = [
        ("04_package_validation.txt", ["-c",
         "from EmotionDetection import emotion_detection, emotion_detector; "
         "print('Package import: OK'); "
         "print('Module:', emotion_detection.__name__); "
         "print('Blank-input result:', emotion_detector(''))"]),
        ("05_isolated_unit_tests.txt", ["-m", "unittest", "discover", "-s", "tests", "-v"]),
        ("08_pylint_server.txt", ["-m", "pylint", "--persistent=n", "server.py"]),
        ("08_pylint_package.txt", ["-m", "pylint", "--persistent=n",
         "--good-names=EmotionDetection", "EmotionDetection"]),
    ]
    if arguments.live:
        checks.extend([
            ("02_03_live_detector.txt", ["-c",
             "from EmotionDetection.emotion_detection import emotion_detector; "
             "print('Import: OK', flush=True); "
             "print(emotion_detector('I am glad this happened'))"]),
            ("05_required_live_tests.txt", ["test_emotion_detection.py"]),
        ])

    failed = False
    for filename, command in checks:
        failed = record(filename, command) != 0 or failed
    return int(failed)


if __name__ == "__main__":
    sys.exit(main())
