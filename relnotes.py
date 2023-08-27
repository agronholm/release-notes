from __future__ import annotations

import os
import re
import sys
from os.path import splitext
from pathlib import Path
from textwrap import dedent

import pandoc


def set_github_action_output(output_name: str, output_value: str) -> None:
    with open(os.path.abspath(os.environ["GITHUB_OUTPUT"]), "a") as f:
        f.write(f"{output_name}={output_value}")


def main() -> None:
    path = os.environ["INPUT_PATH"]
    version_re = re.compile(os.environ["INPUT_VERSION_PATTERN"])
    format_ = os.getenv("INPUT_FORMAT")
    if not (target_version := os.getenv("INPUT_VERSION")):
        if os.environ["GITHUB_REF_TYPE"] == "tag":
            target_version = os.environ["GITHUB_REF_NAME"]
        else:
            print(
                "Error: no version was specified, and the workflow was not triggered "
                "by a pushed tag",
                file=sys.stderr,
            )
            raise SystemExit(1)

    if not format_:
        ext = splitext(path)[1].lower().lstrip(".")
        if splitext(path)[1].lower() == "md":
            format_ = "markdown"
        else:
            format_ = ext

    lines: list[str] = []
    with open(path) as f:
        found = False
        for line in f:
            if found:
                if version_re.search(line):
                    break

                lines.append(line.rstrip())
            elif match := version_re.search(line):
                print("Found version:", match.group(1))
                if match.group(1) == target_version:
                    found = True

        if not found:
            print(f"Cannot find version {target_version} in {path}", file=sys.stderr)
            raise SystemExit(1)

    snippet = dedent("\n".join(lines)).strip()
    doc = pandoc.read(source=snippet, format=format_)
    output_path = Path(os.environ["GITHUB_WORKSPACE"]).joinpath("changelog.md")
    with output_path.open("wb") as f:
        pandoc.write(doc, file=f, format="markdown")

    set_github_action_output("path", str(output_path))


if __name__ == "__main__":
    main()
