# Cloud-Sandbox: the entry point for building and checking this repository.
#
# The original tree (cloudflow/, scripts/, terraform/, models/ ...) has no
# build and no tests of its own. What can be built and tested are the units
# copied into exportit/; each has its own Justfile and this one runs them all.

set shell := ["bash", "-euo", "pipefail", "-c"]

# Projects under exportit/, in dependency order.
units := "tools cloudflow sandbox-provisioning sandbox-terraform sandbox-configs sandbox-ops " + model_units + " cloud-sandbox"

# The model recipes: one unit per model, and what they share (stage 5).
model_units := "model-common model-adcirc-cora model-eccofs model-liveocean model-necofs model-nosofs model-secofs model-ucla-roms model-ufscoastal"

export_tool := "uv run --project exportit/tools python exportit/tools/export.py"

# List the targets.
default:
    @just --list

# Run one target in every project under exportit/.
[private]
each target:
    for unit in {{ units }}; do echo "== $unit: {{ target }}"; just --justfile "exportit/$unit/Justfile" {{ target }}; done

# One-time setup: check out the units kept as submodules, then create every project's environment.
init: submodules-init (each "init")

# Check out every unit that is a repository of its own (exportit/MOVINGDAY.md). Does nothing while there is none.
[private]
submodules-init:
    git submodule update --init

# Build every project's artifacts.
build: (each "build")

# The acceptance tests: the units are checked out, the copies match their sources; lint, type-check and fast tests pass everywhere.
test: submodules-check export-check constitution-check (each "test")

# Everything in test, plus the slow tests and the extraction proof for each copied unit.
full-test: export-check export-baselines sync-rehearse (each "full-test") (export-prove "cloudflow") (export-prove "sandbox-provisioning") (export-prove "sandbox-terraform") (export-prove "sandbox-configs") (export-prove "sandbox-ops") (export-prove "cloud-sandbox")
    for unit in {{ model_units }}; do just export-prove "$unit"; done

# Nothing is published from this repository.
release: full-test
    @echo "Cloud-Sandbox: nothing to release"

# Copy units into exportit/ by their mapping files (all units when none is named).
export *names:
    {{ export_tool }} copy {{ names }}

# Check every copy against its source and its mapping file; source= reads the originals from a clean clone of the original instead of this repository.
export-check source="":
    {{ export_tool }} {{ if source != "" { "--source " + source } else { "" } }} check

# Check every unit against the original as it was at the unit's own baseline (units.toml), read from this repository's history or from a given clone of the original.
export-baselines source="":
    {{ export_tool }} {{ if source != "" { "--source " + source } else { "" } }} check --baselines

# Carry a clean clone of the original's commits since a unit's baseline into the unit's repository, on feature/<branch> there (stage 23). Nothing is pushed.
export-sync unit source branch:
    {{ export_tool }} --source {{ source }} sync {{ unit }} --branch {{ branch }}

# Rehearse a sync from a made-up changed original into throw-away clones of the units: one scenario for each kind of change (stage 23).
sync-rehearse:
    uv run --project exportit/tools python exportit/tools/rehearse_sync.py

# Fail, saying what to do, when a unit kept as a submodule is not checked out (-) or is in conflict (U).
submodules-check:
    #!/usr/bin/env bash
    set -euo pipefail
    status="$(git submodule status)"
    if grep -q '^[-U]' <<<"$status"; then
        grep '^[-U]' <<<"$status" >&2
        echo "PROBLEM: the units above are not checked out, or are in conflict; run: just init" >&2
        exit 1
    fi
    echo "submodules: $(grep -c '^[ +]' <<<"$status" || true) checked out"
    if grep -q '^+' <<<"$status"; then
        echo "note: checked out at a commit other than the one this repository records (not yet added here):"
        grep '^+' <<<"$status"
    fi

# Before this repository is pushed: every commit a submodule is recorded at must be on that unit's remote.
submodules-pushed:
    #!/usr/bin/env bash
    set -euo pipefail
    bad=0
    recorded="$(git ls-tree -r HEAD)"
    while read -r mode _ sha path; do
        [ "$mode" = 160000 ] || continue
        git -C "$path" fetch --quiet origin
        if [ -z "$(git -C "$path" branch -r --contains "$sha" 2>/dev/null)" ]; then
            echo "PROBLEM: $path is recorded at $sha, which is on no branch of its remote; push the unit first" >&2
            bad=1
        fi
    done <<<"$recorded"
    [ "$bad" = 0 ] || exit 1
    echo "submodules: every recorded commit is on its remote"

# Write the shared part of every unit's constitution, and its CLAUDE.md, from exportit/tools/constitution/ (or only the units named).
constitution *units:
    uv run --project exportit/tools python exportit/tools/constitution.py write {{ units }}

# Fail when a unit's shared constitution or CLAUDE.md differs from its source here.
constitution-check:
    uv run --project exportit/tools python exportit/tools/constitution.py check

# Print the git filter-repo directives that would extract a unit with its history.
export-filter name:
    @{{ export_tool }} filter {{ name }}

# Extract a unit from a throw-away clone and compare the result with the copy.
export-prove name:
    {{ export_tool }} prove {{ name }}

# Write sandbox-configs' schema again from cloudflow's code (after a change in what it reads).
configs-schema:
    uv run --project exportit/tools python exportit/tools/configs_schema.py --write
