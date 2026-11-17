#!/usr/bin/env python3
"""On-device siboot -> SideInstaller key handoff. Never run against Mac keys.

Only reads the one local siboot key. No Apple requests, writes, revocations,
passwords or certificate creation. SideInstaller performs the account/cert
check and asks for approval. The local app-scheme payload is sensitive;
never copy it, open it in Safari, or share the local page/terminal session.
"""
import base64
import hashlib
import hmac
import http.server
import os
from pathlib import Path
import re
import secrets
import shutil
import stat
import subprocess
import time
from urllib.parse import quote


def der(tag, data):
    n = len(data)
    size = (n.bit_length() + 7) // 8
    length = bytes([n]) if n < 128 else bytes([128 + size]) + n.to_bytes(size, "big")
    return bytes([tag]) + length + data


def archive(key):
    # PKCS#12 v3: unencrypted keyBag, accepted by pinned SI p12::plain_keys.
    # SI derives the public key and finds its certificate on the active team.
    seq = lambda data: der(48, data)
    content = lambda data: seq(bytes.fromhex("06092a864886f70d010701") + der(160, der(4, data)))
    bag = seq(bytes.fromhex("060b2a864886f70d010c0a0101") + der(160, key))
    return seq(bytes.fromhex("020103") + content(seq(content(seq(bag)))))


def read_key(root):
    # Open Minis uses this private local store; never follow redirected paths.
    for component in (root, *root.parents):
        if component.is_symlink():
            raise ValueError("Refusing a linked signing-store directory.")
    keys = []
    for folder in root.iterdir():
        if folder.is_symlink():
            raise ValueError("Refusing a linked account directory.")
        if folder.is_dir():
            candidate = folder / "key"
            if candidate.exists() or candidate.is_symlink():
                keys.append(candidate)
    if len(keys) != 1:
        raise ValueError("Expected exactly one siboot signing key. Nothing was transferred.")
    path = keys[0]
    if not re.fullmatch(r"[0-9a-f]{64}", path.parent.name) or path.parent.is_symlink():
        raise ValueError("Unexpected signing-store layout.")
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or not 256 <= info.st_size <= 16384:
            raise ValueError("Unexpected signing-key file.")
        key = os.read(fd, 16385)
    finally:
        os.close(fd)
    # Minimal PKCS#8 shape only. SideInstaller validates the RSA key fully.
    if key[:1] != b"\x30" or bytes.fromhex("06092a864886f70d010101") not in key[:64]:
        raise ValueError("Not an expected RSA PKCS#8 signing key.")
    return key, path.parent.name


PAGE = """<!doctype html><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Reuse your signing key</title>
<style>body{font:18px system-ui;padding:24px;line-height:1.5;background:#101820;color:white}
button{font:inherit;padding:16px;background:#287bff;color:white;border:0;border-radius:12px}
input{font:inherit;padding:12px;box-sizing:border-box;width:100%;margin:12px 0}</style>
<h1>Reuse your existing signing key</h1>
<p>Enter the Apple Account email used in both siboot and SideInstaller. This checks the
local account folder. The email stays on this iPhone and is not saved.</p>
<input id="email" type="email" autocomplete="off" autocapitalize="none" spellcheck="false">
<button id="go">Send key to SideInstaller</button><p id="status"></p>
<p>SideInstaller will ask permission and check the key against your Apple team.
This helper does not install apps, create certificates, or revoke anything.</p>
<p>Do not share this page or copy the transfer link. After importing, close this
Minis sheet and stop the helper with Ctrl+C if it is still running.</p>
<script>
const go=document.getElementById('go'),status=document.getElementById('status');
go.onclick=async()=>{go.disabled=true;status.textContent='Checking local account…';
try{const email=document.getElementById('email').value.trim().toLowerCase();
const r=await fetch(location.pathname+'transfer',{method:'POST',headers:{'Content-Type':'text/plain'},body:email,cache:'no-store',credentials:'omit'});
document.getElementById('email').value='';
if(!r.ok){status.textContent='Account did not match, or transfer expired. Nothing changed.';return;}
let link=await r.text();status.textContent='Opening SideInstaller. Confirm the import there.';
window.location.replace(link);link='';
}catch(e){status.textContent='Transfer stopped. Return to Minis and restart the helper.';}};
</script>""".encode()


def make_server(key, account_hash):
    nonce = secrets.token_urlsafe(32)
    page_path = "/" + nonce + "/"
    class Handler(http.server.BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def handle(self):
            self.connection.settimeout(5)
            try:
                super().handle()
            except (TimeoutError, ConnectionError, OSError):
                pass

        def headers_ok(self):
            return (self.headers.get("Host") == self.server.authority
                    and time.monotonic() < self.server.deadline)

        def reply(self, code, body, content_type):
            self.send_response(code)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store, max-age=0")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Content-Security-Policy", "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            allowed = self.headers_ok() and self.path == page_path and not self.server.consumed
            self.reply(200 if allowed else 404, PAGE if allowed else b"Unavailable", "text/html; charset=utf-8")

        def do_POST(self):
            allowed = (self.headers_ok() and self.path == page_path + "transfer"
                       and self.headers.get("Origin") == "http://" + self.server.authority
                       and self.headers.get("Content-Type") == "text/plain"
                       and not self.server.consumed)
            try:
                length = int(self.headers.get("Content-Length", "0"))
                allowed = allowed and 3 <= length <= 254
            except ValueError:
                allowed = False
                length = 0
            if not allowed:
                self.reply(403, b"Denied", "text/plain")
                return
            entered = self.rfile.read(length)
            match = hmac.compare_digest(hashlib.sha256(entered).hexdigest(), self.server.account_hash)
            if not match:
                self.reply(403, b"Account did not match", "text/plain")
                return
            self.server.consumed = True
            encoded = quote(base64.b64encode(archive(self.server.key)).decode(), safe="")
            self.server.key = b""
            self.reply(200, ("sideinstaller://certificate?data=" + encoded + "&password=").encode(), "text/plain")

    server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
    server.authority = "127.0.0.1:" + str(server.server_port)
    server.key, server.account_hash = key, account_hash
    server.deadline = time.monotonic() + 300
    server.consumed = False
    server.timeout = 1
    return server, "http://" + server.authority + page_path


def main():
    opener = shutil.which("minis-open")
    if not opener or not Path("/root/.siboot/isideload").is_dir():
        raise ValueError("Run this only in Open Minis on the iPhone that ran siboot.")
    key, account_hash = read_key(Path("/root/.siboot/isideload"))
    server, url = make_server(key, account_hash)
    key = b""
    print("Opening a private page inside Minis. No signing key is printed or uploaded.", flush=True)
    # Only the random local page address enters the terminal's Minis escape.
    # The signing payload is generated in memory after the user's button tap.
    proc = subprocess.Popen([opener, url], stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        while not server.consumed and time.monotonic() < server.deadline:
            server.handle_request()
    finally:
        server.key = b""
        server.server_close()
    print("Local handoff closed. Check SideInstaller for the import result; nothing was revoked.", flush=True)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Cancelled. No certificate was revoked.")
    except Exception:
        # Do not leak keys, URLs, emails or sensitive filesystem paths.
        print("Handoff stopped before completion. Check that Minis has one signing key and restart.")
        raise SystemExit(1)
