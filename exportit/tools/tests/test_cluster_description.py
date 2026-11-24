"""csis-sandbox-terraform's cluster_description is a fragment cloudflow reads (spec 005, FR-004).

A check between units, kept here, where both are checked out: every key of
the output (its fixture, which the unit's tofu test holds the output to) is
one cloudflow's cluster schema reads for the AWS platform, and the only
required keys it leaves out are those a cluster description adds itself.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EXPORT = ROOT / "exportit"
FIXTURE = EXPORT / "sandbox-terraform" / "tests" / "fixtures" / "cluster_description.json"
SCHEMA = EXPORT / "cloudflow" / "schema" / "clusters.json"
# What only a cluster description can say: how many nodes of which type, and its tags.
ITS_OWN = {"nodeType", "nodeCount", "tags"}


def aws_keys() -> tuple[set[str], set[str]]:
    schema = json.loads(SCHEMA.read_text())
    entries = [schema["common"], schema["platforms"]["AWS"]]
    required = {key for entry in entries for key in entry["required"]}
    read = {
        key for entry in entries for kind in ("required", "optional", "conditional") for key in entry[kind]
    }
    return required, read


def test_every_key_of_the_fragment_is_one_cloudflow_reads() -> None:
    _, read = aws_keys()
    assert set(json.loads(FIXTURE.read_text())) <= read


def test_the_fragment_and_a_descriptions_own_keys_are_all_a_description_needs() -> None:
    required, _ = aws_keys()
    assert required - set(json.loads(FIXTURE.read_text())) == ITS_OWN
