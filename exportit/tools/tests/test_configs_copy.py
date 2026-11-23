"""csis-sandbox-configs' copies of cloudflow's schema and rules are written and checked (spec 005)."""

from __future__ import annotations

from pathlib import Path

import pytest

import configs_copy


@pytest.fixture
def export(tmp_path: Path) -> Path:
    for source in configs_copy.COPIES:
        path = tmp_path / "cloudflow" / source
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"cloudflow's {source}\n")
    (tmp_path / "sandbox-configs").mkdir()
    return tmp_path


def test_written_copies_pass_the_check(export: Path) -> None:
    assert configs_copy.problems(export)
    assert len(configs_copy.write(export)) == 3
    assert configs_copy.problems(export) == []
    assert configs_copy.write(export) == []


def test_a_changed_copy_fails_the_check(export: Path) -> None:
    configs_copy.write(export)
    (export / "sandbox-configs" / "schema" / "jobs.json").write_text("edited here\n")
    assert configs_copy.problems(export) == ["sandbox-configs: schema/jobs.json differs from cloudflow's"]
    assert configs_copy.main(["--export", str(export), "check"]) == 1


def test_the_real_copies_are_cloudflows() -> None:
    assert configs_copy.problems(configs_copy.HERE.parent) == []
