#!/bin/sh
# Local signing-key handoff. Downloads only nonsecret helper code.
set -eu
umask 077
fail() { printf '%s\n' "$1" >&2; exit 1; }
command -v minis-open >/dev/null 2>&1 || fail 'Run this in Open Minis → Shell Terminal on the phone that ran siboot.'
[ -d /root/.siboot/isideload ] || fail 'No siboot signing store found. Complete the SideInstaller bootstrap first.'
case "$(uname -m)" in aarch64|arm64) ;; *) fail 'Run this on the iPhone in Open Minis.' ;; esac
work_dir=$(mktemp -d /tmp/toke-repair.XXXXXX)
trap 'rm -rf "$work_dir"' EXIT HUP INT TERM
wget -qO "$work_dir/handoff.py" https://lovie97.github.io/toke-n-install/handoff.py || fail 'Download failed. Check Wi-Fi and retry.'
printf '%s  %s\n' '7af2f96dd9969b5ff364772e50e4a2dbdda15ca2797cb2f3db438af2300ed55c' "$work_dir/handoff.py" | sha256sum -c - >/dev/null || fail 'Helper checksum mismatch. Nothing was run.'
if ! command -v python3 >/dev/null 2>&1; then
    command -v apk >/dev/null 2>&1 || fail 'Python is missing and this Minis environment has no apk package manager.'
    printf '%s\n' 'Installing Python from Minis’s configured Alpine package repository…'
    apk add --no-cache python3 || fail 'Python installation failed.'
fi
printf '%s\n' 'The next page sends your existing signing key only to SideInstaller on this phone.' 'It does not revoke certificates or install apps. Do not copy or share the transfer page.'
python3 "$work_dir/handoff.py"
