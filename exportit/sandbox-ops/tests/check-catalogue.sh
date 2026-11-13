#!/usr/bin/env bash
# Check that CATALOGUE.tsv and the unit's files agree.
#
# Every file in bin/, keys/ and attic/ has exactly one row, every row names a
# file that is here, and each file sits where its status says: tools in use in
# bin/ or keys/, the others in attic/superseded/ or attic/dead/. Every row
# gives its evidence, and a superseded file says what superseded it.
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
while IFS=$'\x1f' read -r source copy status group superseded_by evidence _; do
  rows=$((rows + 1))
  [[ -z ${listed[$copy]+set} ]] || problem "$copy is listed twice"
  listed[$copy]=$status
  [[ -f $copy ]] || problem "$copy (from $source) is listed but not here"
  [[ -n $evidence ]] || problem "$copy has no evidence"
  [[ -n $group ]] || problem "$copy has no group"
  case $status in
    in-use) [[ $copy == bin/* || $copy == keys/* ]] || problem "$copy is in use but not in bin/ or keys/" ;;
    superseded)
      [[ $copy == attic/superseded/* ]] || problem "$copy is superseded but not in attic/superseded/"
      [[ -n $superseded_by ]] || problem "$copy is superseded but does not say by what"
      ;;
    dead) [[ $copy == attic/dead/* ]] || problem "$copy is dead but not in attic/dead/" ;;
    *) problem "$copy has an unknown status: $status" ;;
  esac
done < <(tail -n +2 "$catalogue" | tr '\t' '\037')

while IFS= read -r path; do
  [[ -n ${listed[$path]+set} ]] || problem "$path is here but not in $catalogue"
done < <(find bin keys attic -type f | LC_ALL=C sort)

if ((problems)); then
  echo "$problems problems" >&2
  exit 1
fi
declare -A count=()
for status in "${listed[@]}"; do count[$status]=$((${count[$status]:-0} + 1)); done
echo "$rows files catalogued: ${count[in-use]:-0} in use, ${count[superseded]:-0} superseded, ${count[dead]:-0} dead"
