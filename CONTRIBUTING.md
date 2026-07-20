# Contributing

Thanks for your interest in the Warband Co-op Campaign mod. Issues and
pull requests are welcome.

## Building

See `docs/BUILD.md` for the full build chain:

- **Module system**: Python 2.7, full 27-step build (partial builds
  produce "Invalid Quick String ID" crashes at runtime).
- **C layer**: MSVC x86 — `build/build.bat` (client ASI),
  `build/build_plugin.bat` (host plugin), `build/build_loader.bat`
  (winmm proxy).
- **Engine**: WSE2 pinned at revision 1145 (v1.1.4.5). All hook
  addresses and binary patches (`docs/wse2-binary-patches.md`) are keyed
  to these exact binaries — a different WSE2 build will not work.

## Reporting issues

Multiplayer campaign bugs are hard to reproduce without context. Please
include:

- **WSE2 revision** (must be 1145 — anything else is the bug)
- **Setup**: how many battle-server slots were running, how many
  clients, same machine or LAN/remote
- **Repro steps**: what you did on the campaign map / in battle, and
  what happened vs what you expected
- **Logs**: the campaign server's plugin log (`warband_coop_host.log`
  in the game directory) and any engine console output around the
  failure

## Pull requests

PRs are reviewed against the flow documentation in `docs/flows/` — each
core flow (battle pipeline, siege, XP sync, inventory sync, party-screen
sync) has a dossier describing how it works and where it is anchored in
the code. Please read the relevant dossier before changing a flow.

This public repository is an export of a private working repository.
Accepted PRs are hand-ported into that repository by a maintainer and
credited to you in the port commit; the next sync then carries your
change back out here.

## Contribution license grant

This project intentionally ships **no license file** (the module-system
layer is derived from TaleWorlds' Mount & Blade: Warband module system;
third-party components carry their own licenses in
`THIRD_PARTY_LICENSES.md`).

By submitting a contribution (issue attachment, patch, or pull
request), you certify that you wrote it or otherwise have the right to
submit it, and you grant the project maintainers a perpetual,
worldwide, irrevocable license to use, modify, and redistribute your
contribution as part of this project.
