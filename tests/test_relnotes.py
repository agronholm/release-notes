from __future__ import annotations

from pathlib import Path
from textwrap import dedent

from _pytest.monkeypatch import MonkeyPatch

from relnotes import main


def test_extract(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    input_path = tmp_path / "changelog.rst"
    output_path = tmp_path / "output.txt"
    tmp_path / "changelog.md"
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
    monkeypatch.setenv("INPUT_HEADER", "Header\n======\n")
    monkeypatch.setenv("INPUT_FOOTER", "Footer\n======\n")
    monkeypatch.setenv("INPUT_VERSION_PATTERN", r"^\*\*([0-9][^*]*)\*\*")
    main()

    assert output_path.read_text() == dedent(
        """\
        changelog<<END_GENERATED_VALUE
        # Header

        -   Simple item
            -   Sub-item `literal`
        -   Second item

        # Footer

        END_GENERATED_VALUE
        """
    )
