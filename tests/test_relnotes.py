from __future__ import annotations

from os import getuid
from pathlib import Path
from textwrap import dedent

import docker
import pytest


@pytest.fixture(scope="session")
def docker_client() -> docker.DockerClient:
    return docker.from_env()


@pytest.fixture(scope="session")
def docker_image(docker_client: docker.DockerClient) -> docker.Image:
    image, logs = docker_client.images.build(path=str(Path(__file__).parent.parent))
    return image


def test_extract(
    tmp_path: Path, docker_client: docker.DockerClient, docker_image: docker.Image
) -> None:
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

    - Simple item "quotes"

      - Sub-item ``literal``
    - Second item, first line that is well over 72 columns long which is the default
      second line

    **1.0.0**

    - First release
    """
        )
    )

    environment = {
        "GITHUB_REF_NAME": "1.2.3rc4",
        "GITHUB_REF_TYPE": "tag",
        "GITHUB_OUTPUT": "/data/output.txt",
        "INPUT_PATH": "/data/changelog.rst",
        "INPUT_HEADER": "Header\n======\n",
        "INPUT_FOOTER": "Footer\n======\n",
        "INPUT_VERSION_PATTERN": r"^\*\*([0-9][^*]*)\*\*",
    }
    volumes = {str(tmp_path): {"bind": "/data", "mode": "rw"}}
    docker_client.containers.run(
        docker_image, environment=environment, user=getuid(), volumes=volumes
    )

    assert output_path.read_text() == dedent(
        """\
        changelog<<END_GENERATED_VALUE
        # Header

        -   Simple item "quotes"
            -   Sub-item `literal`
        -   Second item, first line that is well over 72 columns long which is the \
default second line

        # Footer

        END_GENERATED_VALUE
        """
    )


def test_extract_from_markdown(
    tmp_path: Path, docker_client: docker.DockerClient, docker_image: docker.Image
) -> None:
    input_path = tmp_path / "changelog.md"
    output_path = tmp_path / "output.txt"
    input_path.write_text(
        dedent(
            """
    # Version history

    ## 1.2.4

    - Blah
    - Bleh

    ## 1.2.3rc4

    - Simple item "quotes"

      - Sub-item `literal`
    - Second item, first line that is well over 72 columns long which is the default
      second line

    ## 1.0.0

    - First release
    """
        )
    )

    environment = {
        "GITHUB_REF_NAME": "1.2.3rc4",
        "GITHUB_REF_TYPE": "tag",
        "GITHUB_OUTPUT": "/data/output.txt",
        "INPUT_PATH": "/data/changelog.md",
        "INPUT_HEADER": "Header\n======\n",
        "INPUT_FOOTER": "Footer\n======\n",
        "INPUT_VERSION_PATTERN": r"^\#\# ([0-9][^*]*)\n",
    }
    volumes = {str(tmp_path): {"bind": "/data", "mode": "rw"}}
    docker_client.containers.run(
        docker_image, environment=environment, user=getuid(), volumes=volumes
    )

    assert output_path.read_text() == dedent(
        """\
        changelog<<END_GENERATED_VALUE
        # Header

        -   Simple item "quotes"

            -   Sub-item `literal`

        -   Second item, first line that is well over 72 columns long which is the \
default second line

        # Footer

        END_GENERATED_VALUE
        """
    )
