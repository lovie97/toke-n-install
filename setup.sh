#!/bin/sh
# Pinned on-phone bootstrap for Open Minis. No Apple credentials live here.
set -eu
umask 077
BASE=https://raw.githubusercontent.com/FrizzleM/siboot/92e049ffdbe32cc9d67298ea141c85c68fb7bb95/minis
INSTALLER_SHA=4273a0b0f3a0b02bf0928e2d2e76861e82a4eaab77d95414a3b5afeedcd2419d
IPA_SHA=5b69089fa88d00d18c4ae8ce8ed5d665d8a15220e06aad953b13446cb3d4a529
BINARY_SHA=30c1cd25483ecdec45323febc0c350818afd065ed34c6c330b59fbcb7208581b
fail() { printf '%s\n' "$1" >&2; exit 1; }
command -v minis-open >/dev/null 2>&1 || fail 'Open Minis → Shell Terminal is required.'
case "$(uname -m)" in aarch64|arm64) ;; *) fail 'Run this on your iPhone in Open Minis.' ;; esac
case "${1:-}" in ''|developer-mode) ;; *) fail 'Unrecognized setup option.' ;; esac
work_dir=$(mktemp -d /tmp/toke-setup.XXXXXX)
trap 'rm -rf "$work_dir"' EXIT HUP INT TERM
fetch() { wget -qO "$2" "$1" || fail 'Download failed. Check Wi-Fi and retry.'; }
verify() { printf '%s  %s\n' "$1" "$2" | sha256sum -c - >/dev/null || fail 'Download checksum mismatch. Nothing was run.'; }
printf '%s\n' 'Downloading pinned siboot 0.19.0 and checking its checksum…'
fetch "$BASE/install.sh" "$work_dir/install.sh"
verify "$INSTALLER_SHA" "$work_dir/install.sh"
# The pinned upstream installer verifies BINARY_SHA itself before execution.
if [ "${1:-}" = developer-mode ]; then
    SIBOOT_BASE="$BASE" sh "$work_dir/install.sh" developer-mode
    exit
fi
printf '%s\n' 'Downloading SideInstaller 2.1.0 and checking its checksum…'
fetch https://github.com/FrizzleM/SideInstaller/releases/download/v2.1.0/SideInstaller.ipa "$work_dir/SideInstaller.ipa"
verify "$IPA_SHA" "$work_dir/SideInstaller.ipa"
printf '%s\n' 'Follow the pairing prompts. Keep the silent player open.' 'Stop if any step proposes revoking an existing certificate.'
SIBOOT_BASE="$BASE" sh "$work_dir/install.sh" --ipa "$work_dir/SideInstaller.ipa"
