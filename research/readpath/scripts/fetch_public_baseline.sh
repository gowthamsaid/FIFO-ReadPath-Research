#!/usr/bin/env bash
# Restore ONLY the original public FIFO baseline as a generated, ignored experiment input.
# Public repo content is not duplicated in the research history.
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
pin="b909ff13dcda0a323e598220b9b24ef47a9a4029"
blob="02e181419acccd9a7b2e1313ffa18ac8fcbf942c"
dest="$root/rtl/fifo_sync.v"

if [[ -f "$dest" ]]; then
  got="$(git hash-object "$dest")"
  if [[ "$got" == "$blob" ]]; then
    echo "Verified pinned public baseline: $dest ($got)"
    exit 0
  fi
  echo "ERROR: Existing $dest does not match public baseline blob $blob; refusing to overwrite" >&2
  exit 1
fi

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
git clone --quiet --filter=blob:none --no-checkout "https://github.com/gowthamsaid/FIFO-RTL-to-GDS.git" "$tmp/public-fifo"
mkdir -p "$root/rtl"
git -C "$tmp/public-fifo" show "$pin:rtl/fifo_sync.v" > "$dest.tmp"
if [[ "$(git hash-object "$dest.tmp")" != "$blob" ]]; then
  rm -f "$dest.tmp"
  echo "ERROR: Public FIFO blob integrity verification failed" >&2
  exit 1
fi
mv "$dest.tmp" "$dest"
echo "Restored pinned public FIFO RTL from gowthamsaid/FIFO-RTL-to-GDS@${pin} (blob $blob)"
