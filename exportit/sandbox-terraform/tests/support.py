"""What the tests share: where the module is, and how OpenTofu is run."""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

UNIT = Path(__file__).resolve().parents[1]

# The version the Justfile pins and `just init` puts in .tofu/.
TOFU_VERSION = "1.13.9"
TOFU = Path(os.environ.get("TOFU_BIN", str(UNIT / ".tofu" / TOFU_VERSION / "tofu")))

# Directories that hold .tf files and are expected to validate.
MODULES = [".", "remote-state"]

# Directories that hold .tf files and do not validate on their own, and why.
# They are copied as they are (stage 4, decision 4).
FRAGMENTS = {
    "pipeline": "a sketch of an Image Builder pipeline: it refers to variables and resources "
    "that are defined nowhere",
    "modules": "an older copy of main.tf: it refers to variables that it does not declare",
}

# Files that `tofu fmt -check` (1.13.9) would rewrite. They are byte-identical
# copies of the originals, so they keep the originals' formatting. Terraform
# 1.9.8, which the tests used before, gives the same nine; OpenTofu 1.12 left
# out variables.tf.
UNFORMATTED = {
    "main.tf",
    "modules/orig.main.tf",
    "mysettings.tfvars",
    "outputs.tf",
    "remote-state/main.tf",
    "remote-state/s3.defaults.tfvars",
    "remote-state/variables.tf",
    "security.tf",
    "variables.tf",
}


def environment() -> dict[str, str]:
    """Give the environment OpenTofu runs in, the same as the Justfile's."""
    env = dict(os.environ)
    env.setdefault("TF_IN_AUTOMATION", "1")
    env.setdefault("TF_PLUGIN_CACHE_DIR", str(UNIT / ".terraform-plugins"))
    Path(env["TF_PLUGIN_CACHE_DIR"]).mkdir(exist_ok=True)
    return env


def tofu(*args: str, cwd: Path = UNIT, stdin: str | None = None) -> subprocess.CompletedProcess[str]:
    """Run the pinned OpenTofu and return what happened, without raising."""
    assert TOFU.is_file(), f"no OpenTofu at {TOFU}; run `just init` first"
    return subprocess.run(
        [str(TOFU), *args],
        cwd=cwd,
        env=environment(),
        input=stdin,
        capture_output=True,
        text=True,
        check=False,
    )


def directories_with_terraform() -> set[str]:
    """List the directories of the unit that contain .tf files."""
    found = {
        str(path.parent.relative_to(UNIT))
        for path in UNIT.rglob("*.tf")
        if not any(part.startswith(".") for part in path.relative_to(UNIT).parts)
    }
    return found


# The call is on one line in main.tf; its values contain ${...}, so the map
# is taken to the last "})" on the line.
TEMPLATE_CALL = re.compile(r'templatefile\("(?P<file>[^"]+)",\s*\{(?P<vars>.*)\}\)\s*$', re.MULTILINE)


def template_variables() -> tuple[str, list[str]]:
    """Give the template main.tf renders, and the names of the values it passes."""
    match = TEMPLATE_CALL.search((UNIT / "main.tf").read_text())
    assert match, "main.tf no longer calls templatefile()"
    names = re.findall(r"(?:^|,)\s*(\w+)\s*=", match["vars"])
    return match["file"], names
