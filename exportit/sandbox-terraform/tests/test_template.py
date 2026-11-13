"""Both first-boot templates render with what main.tf gives them.

Terraform renders the template when it plans, so a placeholder that main.tf
does not supply is only found then. These tests render each template with
templatefile(), the function main.tf calls, through `tofu console`.
"""

from __future__ import annotations

import json
from pathlib import Path

from support import UNIT, template_variables, tofu

NEW_TEMPLATE = "init_template.ansible.tpl"

# The two values the new template needs that main.tf does not pass yet.
NEW_VALUES = {
    "provisioning_repo": "https://example.invalid/sandbox-provisioning.git",
    "provisioning_version": "v0.1.0",
}


def sample(names: list[str]) -> dict[str, str]:
    return {name: f"SAMPLE-{name}" for name in names}


def render(template: str, values: dict[str, str], cwd: Path) -> tuple[int, str]:
    expression = f"templatefile({json.dumps(str(UNIT / template))}, {json.dumps(values)})"
    done = tofu("console", "-no-color", cwd=cwd, stdin=expression + "\n")
    return done.returncode, done.stdout + done.stderr


def test_main_tf_renders_the_template_that_is_here(tmp_path: Path) -> None:
    template, names = template_variables()
    assert template == "init_template.tpl"
    assert names == ["efs_name", "ami_name", "aws_region", "project", "sandbox_version"]
    code, out = render(template, sample(names), tmp_path)
    assert code == 0, out
    assert "SAMPLE-efs_name" in out
    assert "./setup-instance.sh" in out


def test_the_new_template_renders_with_the_two_new_values(tmp_path: Path) -> None:
    _, names = template_variables()
    code, out = render(NEW_TEMPLATE, {**sample(names), **NEW_VALUES}, tmp_path)
    assert code == 0, out
    for value in [*NEW_VALUES.values(), "SAMPLE-efs_name", "SAMPLE-project", "SAMPLE-ami_name"]:
        assert value in out
    assert "ansible-pull" in out
    assert "setup-instance.sh" not in out.split("--checkout")[1]


def test_the_new_template_needs_exactly_the_two_new_values(tmp_path: Path) -> None:
    _, names = template_variables()
    for missing in NEW_VALUES:
        values = {**sample(names), **{k: v for k, v in NEW_VALUES.items() if k != missing}}
        code, out = render(NEW_TEMPLATE, values, tmp_path)
        assert code != 0
        assert missing in out
