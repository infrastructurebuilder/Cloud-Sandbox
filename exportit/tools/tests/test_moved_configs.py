"""The templates and examples moved from csis-sandbox-configs to cloudflow are exactly those (spec 005).

A check between units, kept here, where both are checked out: the moved lines
of sandbox-configs.map name every file cloudflow's examples catalogue lists,
at examples/configs/ and the same path, and nothing that was retired.
"""

from __future__ import annotations

import json
from pathlib import Path

import export

ROOT = Path(__file__).resolve().parents[3]
EXPORT = ROOT / "exportit"
DESTINATION = "examples/configs/"


def moves() -> list[export.Move]:
    return export.parse_map(EXPORT / "sandbox-configs.map").moves


def test_every_moved_line_goes_to_cloudflows_examples_at_the_same_path() -> None:
    found = moves()
    assert found, "sandbox-configs.map moves nothing"
    wrong = [m for m in found if m.to != "cloudflow" or m.dest != DESTINATION + m.source]
    assert not wrong, wrong


def test_the_moved_files_are_exactly_cloudflows_templates_and_examples() -> None:
    catalogue = json.loads((EXPORT / "cloudflow" / "examples" / "configs" / "catalogue.json").read_text())
    assert {m.source for m in moves()} == set(catalogue)
    assert {entry["role"] for entry in catalogue.values()} == {"template", "example"}


def test_nothing_retired_is_moved() -> None:
    retired = set(json.loads((EXPORT / "sandbox-configs" / "attic" / "REASONS.json").read_text()))
    assert not retired & {m.source for m in moves()}
