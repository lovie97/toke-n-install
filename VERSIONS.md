# Pinned preview components

The setup wrapper downloads from the official upstream GitHub projects, verifies bytes, then runs the pinned bootstrap. It does not use a moving latest bootstrap.

| Component | Version / revision | SHA-256 |
| --- | --- | --- |
| siboot installer | 0.19.0, `92e049ffdbe32cc9d67298ea141c85c68fb7bb95` | `4273a0b0f3a0b02bf0928e2d2e76861e82a4eaab77d95414a3b5afeedcd2419d` |
| siboot ARM64 binary | same revision | `30c1cd25483ecdec45323febc0c350818afd065ed34c6c330b59fbcb7208581b` |
| SideInstaller IPA | 2.1.0 | `5b69089fa88d00d18c4ae8ce8ed5d665d8a15220e06aad953b13446cb3d4a529` |
| SideStore IPA | nightly `0.7.0-20261027.1507+cd260851` | `3423b6296158713d9497cd6c0816c3214e2369abf40d772e1249d7c2096316fc` |
| Toke-n public unsigned IPA | 0.1.0 build 20 | `1bebefba0243c63c98608d6c80331983c39110f3af8c62f5257de5e13fc31650` |

SideStore’s Nightly selector uses a moving upstream URL. Its asset matched this digest on November 16, 2026; do not treat a later Nightly as the same tested candidate. Record the version shown after installation. The public Toke-n edition omits the built-in signing engine and bundles no third-party renewal libraries. The full edition remains private.

Open Minis must be at least 1.16. LocalDevVPN 1.3.0 was observed during the test. Toke-n’s base app supports iOS 26.5+, but this guide’s direct on-device bootstrap requires iOS 27+.

## Upstream

- [siboot pinned source](https://github.com/FrizzleM/siboot/tree/92e049ffdbe32cc9d67298ea141c85c68fb7bb95)
- [SideInstaller 2.1.0](https://github.com/FrizzleM/SideInstaller/releases/tag/v2.1.0)
- [SideStore](https://github.com/SideStore/SideStore)

These projects and Apple are separate from Toke-n. This repository hosts a guide and helper code; it does not relicense their software.
