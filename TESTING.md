# Installation preview — validation status

Updated November 17, 2026. This page documents an experimental installation path; it does not claim a fully verified, indefinite renewal system.

## Observed on a physical iPhone

- Toke-n build 19 launched after an in-place update from build 18 using the original signing identity. A synthetic chat and provider connection survived; chat export was confirmed by the tester. That update used a Mac over Wi-Fi.
- Open Minis and LocalDevVPN were used to bootstrap SideInstaller. SideInstaller opened and displayed a connected tunnel.
- SideInstaller stopped at Apple error 7460 instead of revoking an existing certificate. The missing signing-key handoff was investigated in the pinned source.
- A local key-transfer helper was supplied; the tester subsequently reported SideStore installed. Import receipt, exact installed SideStore identity, and resulting certificate were not independently captured.

## Public build 20

- A separate target builds only the original chat sources and artwork against Apple system frameworks. It does not bundle the full edition’s signing, pairing, Apple authentication libraries, OpenSSL, or GPL/AGPL dependencies.
- The unsigned arm64 iPhone/iPad IPA passed its archive verifier, and 22 offline chat tests passed. Its minimum OS is 26.5; the setup guide targets iOS 27+.
- The available simulator runtime was 26.2, so a simulator launch at the supported minimum was not performed. Xcode emitted a deployment-target/SDK version warning while producing the build. A physical launch and refresh remain required.

## Software checks

- The original build 19 unsigned archive passed the arm64 iPhone/iPad archive checks and contained no profile, signature, pairing file, provider credential, or chat archive.
- The key-transfer format passed the pinned SideInstaller 2.1.0 Rust importer using a public synthetic fixture. The helper has checks for the local account, single-use transfer, loopback Host/Origin, timeout, no HTTP logs, and redirected signing-store paths.
- Public wrapper scripts pin and hash-check upstream downloads. No real Apple Account or signing key is used by local automated tests.

## Still required

- SideStore installation of Toke-n and first launch.
- A SideStore refresh that advances Toke-n’s installed profile expiry while retaining chats and API access, plus refresh of SideStore itself.
- Launch after the original expiry, a second renewal cycle, background/Shortcut refresh, and recovery after Toke-n or SideStore expires.
- A fresh device with no Developer Mode toggle or prior pairing.
- Physical iPad installation.


A successful build or an installed SideStore does not establish those outcomes. Refresh manually before expiry; iOS chooses when background tasks run.
