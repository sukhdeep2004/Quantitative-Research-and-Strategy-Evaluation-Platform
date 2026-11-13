import os
import subprocess


def _git_version():
    try:
        return subprocess.run(
            ["git", "describe", "--always", "--dirty"],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


# CODE_VERSION can be set explicitly where the code is deployed without its .git folder.
CODE_VERSION = os.getenv("CODE_VERSION") or _git_version()
