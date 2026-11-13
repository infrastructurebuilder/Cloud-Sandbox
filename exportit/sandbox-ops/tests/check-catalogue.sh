#!/usr/bin/env bash
# Check that CATALOGUE.tsv and the unit's files agree.
#
# Every file in bin/ and keys/ has exactly one row, every row names a file
# that is here, and every row is a tool in use, in bin/ or keys/, with its
# evidence. The superseded and dead files do not travel with this unit: they
# stay with the original repository, in the umbrella's attic/ (the operator's
# decision of 2026-11-13), which has a catalogue and a check of its own.
set -euo pipefail

cd "$(dirname "$0")/.."
catalogue=CATALOGUE.tsv
problems=0
problem() {
  echo "PROBLEM $*" >&2
  problems=$((problems + 1))
}

expected_header=$'source\tcopy\tstatus\tgroup\tsuperseded_by\tevidence\tsensitive'
[[ $(head -n 1 "$catalogue") == "$expected_header" ]] || problem "$catalogue: the header is not: $expected_header"

declare -A listed=()
rows=0
# Tabs are whitespace to read, which would merge empty fields; a unit
# separator is not.
while IFS=$'\x1f' read -r source copy status group _superseded_by evidence _; do
  rows=$((rows + 1))
  [[ -z ${listed[$copy]+set} ]] || problem "$copy is listed twice"
  listed[$copy]=$status
  [[ -f $copy ]] || problem "$copy (from $source) is listed but not here"
  [[ -n $evidence ]] || problem "$copy has no evidence"
  [[ -n $group ]] || problem "$copy has no group"
  case $status in
    in-use) [[ $copy == bin/* || $copy == keys/* ]] || problem "$copy is in use but not in bin/ or keys/" ;;
    superseded | dead) problem "$copy is $status: it belongs in the umbrella's attic, not here" ;;
    *) problem "$copy has an unknown status: $status" ;;
  esac
done < <(tail -n +2 "$catalogue" | tr '\t' '\037')

while IFS= read -r path; do
  [[ -n ${listed[$path]+set} ]] || problem "$path is here but not in $catalogue"
done < <(find bin keys -type f | LC_ALL=C sort)

if ((problems)); then
  echo "$problems problems" >&2
  exit 1
fi
echo "$rows files catalogued, all in use"
