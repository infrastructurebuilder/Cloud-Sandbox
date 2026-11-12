"""What the tests share: where things are, and how the scripts are read."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

UNIT = Path(__file__).resolve().parents[1]
LEGACY = UNIT / "legacy"
FUNCS = LEGACY / "funcs-setup-instance.sh"
SETUP = LEGACY / "setup-instance.sh"
ENVIRONMENT = LEGACY / "environment-vars.sh"

# Which function of funcs-setup-instance.sh each role translates.
ROLE_FUNCTIONS = {
    "sandbox_paths": ["setup_paths"],
    "user_shell": ["setup_aliases"],
    "base_system": ["setup_environment"],
    "prefect_server": ["setup_prefect-server"],
    "mpi_ssh": ["setup_ssh_mpi"],
    "efa_driver": ["install_efa_driver"],
    "fsx_lustre_client": ["install_fsx_driver"],
    "python_user_env": ["install_python_modules_user"],
    "spack": ["install_spack"],
    "intel_oneapi": ["install_intel_oneapi_dnf", "add_spack_site_external"],
    "spack_environment": ["create_spack-environment", "build_spack-environment"],
    "hpc_tuning": ["configure_optimizations"],
}

# The name each exported variable of environment-vars.sh has in group_vars/all.yml.
VARIABLES = {
    "PREFECT_VER": "prefect_version",
    "GCC_VER": "gcc_version",
    "GCC_MAJOR": "gcc_major",
    "SPACK_VER": "spack_version",
    "ONEAPI_VER": "oneapi_version",
    "ONEAPI_MAJOR_MINOR": "oneapi_major_minor",
    "INTEL_COMPILER_VER": "intel_compiler_version",
    "INTEL_MPI_VER": "intel_mpi_version",
    "ESMF_VER": "esmf_version",
    "SPACK_DIR": "spack_dir",
    "JOBS": "spack_jobs",
    "SPACKOPTS": "spack_opts",
    "target": "spack_target",
    "SPACKTARGET": "spack_arch",
    "EFA_INSTALLER_VER": "efa_installer_version",
    "SPACK_CACHEONLY": "spack_cache_only",
    "SPACK_MIRROR": "spack_mirror",
    "SPACK_KEY_URL": "spack_key_url",
    "SPACK_KEY": "spack_key",
    "ami_name": "ami_name",
    "project_tag": "project_tag",
}

FUNCTION_START = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*) *\(\) *\{")
LINE_SPEC = re.compile(r"L(\d+)(?:-L(\d+))?")


def lines_of(path: Path) -> list[str]:
    """Read a file as a list in which index 1 is line 1."""
    return ["", *path.read_text().splitlines()]


def functions(path: Path = FUNCS) -> dict[str, range]:
    """Map each shell function to the lines of its body."""
    found: dict[str, range] = {}
    lines = lines_of(path)
    name, start = None, 0
    for number, line in enumerate(lines):
        match = FUNCTION_START.match(line)
        if match:
            name, start = match.group(1), number
        elif line == "}" and name:
            found[name] = range(start + 1, number)
            name = None
    return found


def expand(spec: str) -> set[int]:
    """Turn "L5 L10-L12" into {5, 10, 11, 12}."""
    numbers: set[int] = set()
    for first, last in LINE_SPEC.findall(spec):
        numbers.update(range(int(first), int(last or first) + 1))
    return numbers


def script_values(nproc: int, cache_only: int | None = None) -> dict[str, str]:
    """Let bash work out what the scripts set, on a machine with ``nproc`` processors.

    The first nine lines of funcs-setup-instance.sh are included: that is where
    the cache flag is added to SPACKOPTS.
    """
    override = "" if cache_only is None else f"export SPACK_CACHEONLY={cache_only}"
    names = " ".join(VARIABLES)
    program = f"""
        nproc() {{ echo {nproc}; }}
        cd "{LEGACY}"
        source ./environment-vars.sh >/dev/null
        {override}
        source <(sed -n '1,9p' funcs-setup-instance.sh)
        for name in {names}; do printf '%s=%s\\n' "$name" "${{!name}}"; done
    """
    done = subprocess.run(["bash", "-c", program], capture_output=True, text=True, check=True)
    return dict(line.split("=", 1) for line in done.stdout.splitlines())


def rendered(out: Path, *, nproc: int = 8, kernel: str = "6.12.0-211.1.el10", cache_only: int = -1) -> dict:
    """Let Ansible work out what the playbooks would use."""
    sample = UNIT / "tests" / "fsx-lustre-client.repo.sample"
    command = [
        str(Path(sys.executable).parent / "ansible-playbook"),
        "tests/render.yml",
        "-e",
        json.dumps(
            {
                "sandbox_nproc": nproc,
                "spack_cache_only": cache_only,
                "fsx_lustre_client_kernel": kernel,
                "render_out": str(out),
                "render_repo_sample": str(sample),
            }
        ),
    ]
    done = subprocess.run(command, cwd=UNIT, capture_output=True, text=True, check=False)
    assert done.returncode == 0, done.stdout + done.stderr
    return json.loads(out.read_text())
