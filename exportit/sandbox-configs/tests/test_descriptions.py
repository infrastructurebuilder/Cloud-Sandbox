"""Every file is what the catalogue says: its kind, its role, and whether cloudflow can read it.

The copies are byte-identical to their originals (stage 6, decision 1), so a
description cloudflow cannot read is recorded, not repaired. A change in
either direction, a description that breaks or one that is fixed, fails the
test until the catalogue is written again with
``uv run python tests/descriptions.py --record`` and the difference reviewed.
"""

from __future__ import annotations

import json
import re

import pytest
from descriptions import CATALOGUE, examine, files, schema

RECORDED: dict[str, dict[str, str]] = json.loads(CATALOGUE.read_text())
LINE_REFERENCE = re.compile(r"^cloudflow/(job|cluster)/\w+\.py:[1-9]\d*$")


def test_the_catalogue_lists_every_file() -> None:
    here = set(files())
    assert here == set(RECORDED), (
        f"not catalogued: {sorted(here - set(RECORDED))}; catalogued but gone: {sorted(set(RECORDED) - here)}"
    )


@pytest.mark.parametrize("path", sorted(RECORDED))
def test_a_file_is_as_catalogued(path: str) -> None:
    assert examine(path) == RECORDED[path]


def test_both_directories_hold_descriptions() -> None:
    kinds = {entry["kind"] for entry in RECORDED.values()}
    assert {"job", "cluster"} <= kinds


@pytest.mark.parametrize("name", ["jobs.json", "clusters.json"])
def test_every_key_of_the_schema_names_the_line_that_reads_it(name: str) -> None:
    found = schema(name)
    entries = [found["common"], *(found.get("jobtypes") or found["platforms"]).values()]
    references = [
        ref
        for entry in entries
        for kind in ("required", "optional", "conditional")
        for ref in entry[kind].values()
    ]
    assert references
    bad = [ref for ref in references if not LINE_REFERENCE.match(ref)]
    assert not bad, bad


def test_a_template_and_a_site_description_of_each_kind_exist() -> None:
    roles = {(entry["kind"], entry["role"]) for entry in RECORDED.values()}
    assert {("job", "template"), ("cluster", "template"), ("job", "site"), ("cluster", "site")} <= roles
