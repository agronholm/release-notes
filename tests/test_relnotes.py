from __future__ import annotations

from pathlib import Path
from textwrap import dedent

from _pytest.monkeypatch import MonkeyPatch

from relnotes import main


def test_extract(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    input_path = tmp_path / "changelog.rst"
    output_path = tmp_path / "output.txt"
    changelog_path = tmp_path / "changelog.md"
    input_path.write_text(
        dedent(
            """
    Version history
    ===============

    **1.2.4**

    - Blah
    - Bleh

    **1.2.3rc4**

    - Simple item

      - Sub-item ``literal``
    - Second item

    **1.0.0**

    - First release
    """
        )
    )

    monkeypatch.setenv("GITHUB_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("GITHUB_REF_NAME", "1.2.3rc4")
    monkeypatch.setenv("GITHUB_REF_TYPE", "tag")
    monkeypatch.setenv("GITHUB_OUTPUT", str(output_path))
    monkeypatch.setenv("INPUT_PATH", str(input_path))
    monkeypatch.setenv("INPUT_VERSION_PATTERN", r"^\*\*([0-9][^*]*)\*\*")
    main()

    output = output_path.read_text()
    key, _, value = output.partition("=")
    assert key == "path"
    assert value == str(changelog_path)

    changelog = changelog_path.read_text()
    assert changelog == dedent(
        """\
    -   Simple item
        -   Sub-item `literal`
    -   Second item
    """
    )
