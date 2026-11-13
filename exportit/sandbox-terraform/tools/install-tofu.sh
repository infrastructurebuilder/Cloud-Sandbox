#!/usr/bin/env bash
# Put one version of OpenTofu in .tofu/<version>/tofu, for this project only.
#
#   tools/install-tofu.sh 1.13.9
#
# The release's zip for this machine is downloaded from GitHub and checked
# against the release's SHA256SUMS before it is unpacked. Nothing outside
# this directory is changed, and a version already in place is left alone.
set -euo pipefail

version=${1:?usage: $0 <version>}
cd "$(dirname "$0")/.."
target=.tofu/$version
if [[ -x $target/tofu ]] && "$target/tofu" version | grep -qx "OpenTofu v$version"; then
  echo "OpenTofu $version is in $target"
  exit 0
fi

case "$(uname -s)" in
  Darwin) os=darwin ;;
  Linux) os=linux ;;
  *)
    echo "no OpenTofu build for $(uname -s)" >&2
    exit 1
    ;;
esac
case "$(uname -m)" in
  x86_64 | amd64) arch=amd64 ;;
  arm64 | aarch64) arch=arm64 ;;
  *)
    echo "no OpenTofu build for $(uname -m)" >&2
    exit 1
    ;;
esac

zip=tofu_${version}_${os}_${arch}.zip
sums=tofu_${version}_SHA256SUMS
base=https://github.com/opentofu/opentofu/releases/download/v$version
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

curl --fail --silent --show-error --location --output "$work/$zip" "$base/$zip"
curl --fail --silent --show-error --location --output "$work/$sums" "$base/$sums"
expected=$(awk -v name="$zip" '$2 == name { print $1 }' "$work/$sums")
if [[ -z $expected ]]; then
  echo "$sums does not list $zip" >&2
  exit 1
fi
if command -v sha256sum >/dev/null; then
  actual=$(sha256sum "$work/$zip" | cut -d' ' -f1)
else
  actual=$(shasum -a 256 "$work/$zip" | cut -d' ' -f1)
fi
if [[ $actual != "$expected" ]]; then
  echo "$zip: checksum $actual, expected $expected" >&2
  exit 1
fi

mkdir -p "$target"
unzip -q -o "$work/$zip" tofu -d "$target"
chmod 755 "$target/tofu"
"$target/tofu" version | head -n 1
