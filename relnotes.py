from __future__ import annotations

import os
import re
import sys
from os.path import splitext
from textwrap import dedent

import pandoc


def set_github_action_output(output_name: str, output_value: str) -> None:
    with open(os.path.abspath(os.environ["GITHUB_OUTPUT"]), "a") as f:
        if "\n" in output_value:
            f.write(f"{output_name}<<END_GENERATED_VALUE\n")
            f.write(output_value)
            f.write("\nEND_GENERATED_VALUE\n")
        else:
            f.write(f"{output_name}={output_value}\n")


def main() -> None:
    if os.environ["GITHUB_REF_TYPE"] != "tag":
        print(
            "Error: the workflow was not triggered by a tag being pushed",
            file=sys.stderr,
        )
        raise SystemExit(1)

    path = os.environ["INPUT_PATH"]
    version_re = re.compile(os.environ["INPUT_VERSION_PATTERN"])
    format_ = os.getenv("INPUT_FORMAT")
    header = os.getenv("INPUT_HEADER")
    footer = os.getenv("INPUT_FOOTER")
    target_version = os.environ["GITHUB_REF_NAME"]

    if not format_:
        ext = splitext(path)[1].lower().lstrip(".")
        if splitext(path)[1].lower() == "md":
            format_ = "gfm"
        else:
            format_ = ext

    lines: list[str] = []
    if header:
        lines.extend(header.splitlines())

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

    if footer:
        lines.extend(footer.splitlines())

    snippet = dedent("\n".join(lines)).strip()
    doc = pandoc.read(source=snippet, format=format_)
    converted = pandoc.write(doc, format="gfm", options=["--wrap=none"])
    set_github_action_output("changelog", converted)


if __name__ == "__main__":
    main()
