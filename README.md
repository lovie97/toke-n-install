# Install Toke-n

**[Open the installation guide](https://lovie97.github.io/toke-n-install/)**

A public, phone-friendly guide and unsigned IPA for Toke-n. No GitHub account is needed to read the guide or download the public edition. The app’s development repository stays private.

- [Download public build 20](https://github.com/lovie97/toke-n-install/releases/tag/v0.1.0-build20)
- [Test status and remaining device checks](TESTING.md)
- [Pinned upstream versions](VERSIONS.md)
- [Privacy and the local signing repair](https://lovie97.github.io/toke-n-install/privacy.html)
- [Review setup](setup.sh), [repair launcher](repair.sh), and [local handoff helper](handoff.py)
- [Checksums](SHA256SUMS.txt)

The public edition preserves Toke-n’s local chats, streaming replies, model/provider settings, and chat export/import. SideStore handles installation and signing renewal. The built-in Apple sign-in, pairing, and signing engine stays in the private full edition and is not part of this public IPA.

## Preview status

The unsigned build and archive checks pass and 22 offline chat tests pass. Public build 20 has **not yet been installed and refreshed through SideStore on a physical device**. iPad is also not physically tested. iOS chooses when background work runs, so refresh manually before the seven-day expiry.

The direct on-phone bootstrap documented here requires iOS 27+, Open Minis 1.16+, LocalDevVPN, Wi-Fi, and Developer Mode. A fresh phone with no Developer Mode toggle is not a verified route. Existing Toke-n installations need a migration check before replacement; do not delete them to make space.

## Privacy

This repository contains only this guide, original helper code, public version/checksum metadata, and the unsigned public release. No provider keys, Apple credentials, profiles, signing keys, pairing records, device identities, or chat exports are published. The site has no analytics or third-party JavaScript. GitHub and linked services apply their own normal logging and privacy policies.

## Hosting

GitHub Pages serves the root of `main`. The IPA lives in GitHub Releases. Site helpers pin their upstream downloads, and `repair.sh` pins `handoff.py`. If the helper changes, update its digest in `repair.sh` and regenerate `SHA256SUMS.txt`.
