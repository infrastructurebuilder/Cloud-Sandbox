#!/usr/bin/env bash
# Check the shell scripts of this unit without running them.
#
#   tests/check-scripts.sh            compare with the record; exit 1 on any change
#   tests/check-scripts.sh --record   rewrite tests/shellcheck.counts from what is here
#
# A script is a text file whose first line is a #! line naming sh or bash, or
# whose name ends in .sh. Every script must pass `bash -n`, except the files
# listed in tests/templates.txt: those are templates with <placeholders> in
# them, and they must still fail it, so that the list stays true.
#
# The findings of shellcheck are counted per script and compared with
# tests/shellcheck.counts. The scripts are byte-identical copies of their
# originals (stage 5, decision 2), so their findings are recorded, not fixed:
# the check fails when a count changes, in either direction, and says which.
#
# This file is the same in every model-* unit.
set -euo pipefail

cd "$(dirname "$0")/.."
record=0
if [[ ${1:-} == --record ]]; then
  record=1
elif [[ $# -gt 0 ]]; then
  echo "usage: $0 [--record]" >&2
  exit 2
fi

counts_file=tests/shellcheck.counts
templates_file=tests/templates.txt
version=$(shellcheck --version | sed -n 's/^version: //p')

# Print the scripts of the unit, one path per line, in a fixed order.
list_scripts() {
  local path first
  find . -type f ! -path './tests/*' ! -path './.git/*' | sed 's|^\./||' | LC_ALL=C sort |
    while IFS= read -r path; do
      LC_ALL=C grep -qI '' "$path" || continue # binary, or empty
      first=$(head -n 1 "$path")
      if [[ $first =~ ^\#!.*(^|[/ ])(ba)?sh([[:space:]]|$) || $path == *.sh ]]; then
        printf '%s\n' "$path"
      fi
    done
}

# Count shellcheck's findings for one script.
count_findings() {
  local path=$1 first
  first=$(head -n 1 "$path")
  local -a shell=()
  [[ $first == '#!'* ]] || shell=(--shell=bash)
  { shellcheck "${shell[@]}" --format=gcc "$path" || true; } | wc -l | tr -d ' '
}

# Read a list file: one path per line; '#' starts a comment.
read_list() {
  [[ -f $1 ]] || return 0
  sed -e 's/#.*//' -e 's/[[:space:]]*$//' "$1" | grep -v '^$' || true
}

mapfile -t scripts < <(list_scripts)
mapfile -t templates < <(read_list "$templates_file")

problems=0
problem() {
  echo "PROBLEM $*" >&2
  problems=$((problems + 1))
}

is_template() {
  local item
  for item in "${templates[@]}"; do [[ $item == "$1" ]] && return 0; done
  return 1
}

for path in "${templates[@]}"; do
  [[ -f $path ]] || problem "$templates_file names $path, which is not here"
done

declare -A found=()
total=0
for path in "${scripts[@]}"; do
  if bash -n "$path" 2>/dev/null; then
    is_template "$path" && problem "$path passes bash -n now: take it out of $templates_file"
  else
    is_template "$path" || problem "$path fails bash -n: $(bash -n "$path" 2>&1 | head -n 1)"
  fi
  found[$path]=$(count_findings "$path")
  total=$((total + found[$path]))
done

if ((record)); then
  {
    echo "# Findings of shellcheck per script, written by tests/check-scripts.sh --record."
    echo "# Recorded with shellcheck version $version"
    for path in "${scripts[@]}"; do printf '%s\t%s\n' "${found[$path]}" "$path"; done
  } >"$counts_file"
  echo "recorded ${#scripts[@]} scripts, $total shellcheck findings, in $counts_file"
  exit $((problems > 0))
fi

[[ -f $counts_file ]] || {
  echo "PROBLEM no $counts_file: run tests/check-scripts.sh --record" >&2
  exit 1
}
recorded_version=$(sed -n "s/^# Recorded with shellcheck version //p" "$counts_file")
if [[ $recorded_version != "$version" ]]; then
  problem "the counts were recorded with shellcheck $recorded_version; this is $version." \
    "Review the difference, then run tests/check-scripts.sh --record"
fi

declare -A recorded=()
while IFS=$'\t' read -r count path; do
  [[ -z $count || $count == '#'* ]] && continue
  recorded[$path]=$count
done <"$counts_file"

for path in "${scripts[@]}"; do
  if [[ -z ${recorded[$path]+set} ]]; then
    problem "$path is a script that $counts_file does not list (${found[$path]} findings)"
  elif [[ ${recorded[$path]} != "${found[$path]}" ]]; then
    problem "$path: ${found[$path]} shellcheck findings, ${recorded[$path]} recorded"
  fi
done
for path in "${!recorded[@]}"; do
  [[ -n ${found[$path]+set} ]] || problem "$counts_file lists $path, which is not a script here"
done

if ((problems)); then
  echo "$problems problems" >&2
  exit 1
fi
echo "${#scripts[@]} scripts: syntax as recorded (${#templates[@]} templates);" \
  "$total shellcheck findings, as recorded (shellcheck $version)"
