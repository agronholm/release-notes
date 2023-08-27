.. image:: https://github.com/agronholm/release-notes/actions/workflows/test.yml/badge.svg
  :target: https://github.com/agronholm/release-notes/actions/workflows/test.yml
  :alt: Build Status

.. highlight:: yaml

This is a GitHub action that extracts release notes from a changelog file, converts them
to the Markdown format and outputs the result.

Here's what it does:

#. Reads the input file line by line until it finds a line that matches the version
   pattern regex, and the matched version is the one it's looking for
#. Reads lines to memory until it encounters another version or the end of the file
#. Joins the lines together as a snippet and converts it to the Markdown format
#. Exports the Markdown document as the ``changelog`` output

Configuration options:

* ``path`` (required): the path to the changelog to parse
* ``version_pattern``: the regular expression to use for finding lines that contain
  version numbers. The first group within the expression is used to capture the version
  itself. The default value is ``^\*\*([0-9][^*]*)\*\*`` which would match a line like
  ``**1.2.3**`` or ``**4.0.1a7**`` at the beginning of the line.

The following example is triggered by pushing a version tag (``X.Y.Z``).
It assumes a changelog file names ``CHANGES.rst`` in the project root.
Sample configuration (``.github/workflows/release.yml``)::

    name: Create a release

    on:
      push:
        tags:
          - "[0-9]+.[0-9]+.[0-9]+"
          - "[0-9]+.[0-9]+.[0-9]+.post[0-9]+"
          - "[0-9]+.[0-9]+.[0-9]+[a-b][0-9]+"
          - "[0-9]+.[0-9]+.[0-9]+rc[0-9]+"

    jobs:
      release:
        runs-on: ubuntu-latest
        permissions:
          contents: write
        steps:
        - uses: actions/checkout@v3
        - id: changelog
          uses: agronholm/release-notes@v1
          with:
            path: CHANGES.rst
        - uses: ncipollo/release-action@v1
          with:
            body: |
              ${{ steps.changelog.outputs.changelog }}
