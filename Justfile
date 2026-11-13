# Cloud-Sandbox: the entry point for building and checking this repository.
#
# The original tree (cloudflow/, scripts/, terraform/, models/ ...) has no
# build and no tests of its own. What can be built and tested are the units
# copied into exportit/; each has its own Justfile and this one runs them all.

set shell := ["bash", "-euo", "pipefail", "-c"]

# Projects under exportit/, in dependency order.
units := "tools cloudflow-plotting cloudflow sandbox-provisioning sandbox-terraform sandbox-configs sandbox-ops " + model_units

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

# One-time setup: create every project's environment.
init: (each "init")

# Build every project's artifacts.
build: (each "build")

# The acceptance bar: the copies match their sources; lint, type-check and fast tests pass everywhere.
test: export-check (each "test")

# Everything in test, plus the slow tests and the extraction proof for each copied unit.
full-test: export-check (each "full-test") (export-prove "cloudflow-plotting") (export-prove "cloudflow") (export-prove "sandbox-provisioning") (export-prove "sandbox-terraform") (export-prove "sandbox-configs") (export-prove "sandbox-ops")
    for unit in {{ model_units }}; do just export-prove "$unit"; done

# Nothing is published from this repository.
release: full-test
    @echo "Cloud-Sandbox: nothing to release"

# Copy units into exportit/ by their mapping files (all units when none is named).
export *names:
    {{ export_tool }} copy {{ names }}

# Check every copy against its source and its mapping file.
export-check:
    {{ export_tool }} check

# Print the git filter-repo directives that would extract a unit with its history.
export-filter name:
    @{{ export_tool }} filter {{ name }}

# Extract a unit from a throw-away clone and compare the result with the copy.
export-prove name:
    {{ export_tool }} prove {{ name }}

# Write sandbox-configs' schema again from cloudflow's code (after a change in what it reads).
configs-schema:
    uv run --project exportit/tools python exportit/tools/configs_schema.py --write
