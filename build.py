"""Build the console application: uv run --group build build.py build_exe."""

import os
import platform
import sys
import tomllib
from pathlib import Path

from cx_Freeze import Executable, setup

PROJECT_ROOT = Path(__file__).resolve().parent
os.chdir(PROJECT_ROOT)
with (PROJECT_ROOT / "pyproject.toml").open("rb") as stream:
    project = tomllib.load(stream)["project"]

output_name = (
    f"{project['name']}-{project['version']}-"
    f"{platform.system().lower()}_{platform.machine().lower()}-"
    f"py{sys.version_info.major}.{sys.version_info.minor}"
)

include_files = [(str(PROJECT_ROOT / "README.md"), "README.md")]
if sys.platform == "win32":
    # uv-managed Python DLLs may not be discovered automatically from .venv.
    python_home = Path(sys.base_prefix)
    for name in ("python3.dll", f"python{sys.version_info.major}{sys.version_info.minor}.dll",
                 "vcruntime140.dll", "vcruntime140_1.dll"):
        source = python_home / name
        if source.is_file():
            include_files.append((str(source), name))

setup(
    name=project["name"],
    version=project["version"],
    description=project["description"],
    options={
        "build_exe": {
            "build_exe": str(PROJECT_ROOT / "build" / output_name),
            "packages": ["cv2", "numpy"],
            "include_files": include_files,
            "optimize": 1,
        }
    },
    executables=[
        Executable(
            str(PROJECT_ROOT / "camera.py"),
            target_name=project["name"] + (".exe" if sys.platform == "win32" else ""),
            base="console",
        )
    ],
)
