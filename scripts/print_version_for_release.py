import ast
import os
import re
import sys

from packaging.version import Version

DEV_RELEASE = os.environ.get("DEV_RELEASE", None) == "1"
source_dir = sys.argv[1]

_version_re = re.compile(r"__version__\s+=\s+(.*)")

with open(f"{source_dir}/__init__.py", "rb") as f:
    version = str(ast.literal_eval(_version_re.search(f.read().decode("utf-8")).group(1)))

if not DEV_RELEASE:
    # Strip .devN
    v = Version(version)
    print(f"{v.major}.{v.minor}.{v.micro}")
else:
    print(version)
