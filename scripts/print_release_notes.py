# Print a version's HISTORY.rst entries as Markdown for a GitHub release body.
import os
import re
import sys

PROJECT_DIRECTORY = os.path.join(os.path.dirname(__file__), "..")
PR_URL = "https://github.com/galaxyproject/gxformat2/pull/"


def main(argv):
    version = argv[1]
    with open(os.path.join(PROJECT_DIRECTORY, "HISTORY.rst")) as f:
        lines = f.read().splitlines()
    header = re.compile(rf"^{re.escape(version)} \(\d{{4}}-\d{{2}}-\d{{2}}\)$")
    try:
        start = next(i for i, line in enumerate(lines) if header.match(line)) + 2
    except StopIteration:
        sys.exit(f"No released section for {version} in HISTORY.rst")
    for line in lines[start:]:
        if line.startswith("---"):
            break
        if line.startswith("*"):
            line = re.sub(r"`(@[^`]+)`_", r"\1", line)
            line = re.sub(r"`Pull Request (\d+)`_", rf"[Pull Request \1]({PR_URL}\1)", line)
            print(line)


if __name__ == "__main__":
    main(sys.argv)
