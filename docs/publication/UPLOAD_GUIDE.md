# CurseForge upload guide

All project copy is in English. The project is prepared as an initial **Beta**.
The GitHub repository is public; creating/submitting the CurseForge project is a separate step.

## Files to use

| Field or action | File / value |
| --- | --- |
| Name | **Forever Frost Alert** |
| Suggested slug | `forever-frost-alert` — subject to availability |
| Summary | Displays glowing frost arcs while Fingers of Frost is active on your mage in WoW Forever. No aura framework required. |
| Logo | `assets/branding/icon.png` — original square PNG, 1254 × 1254 pixels |
| Description | Paste `docs/publication/CURSEFORGE_DESCRIPTION.md` in Markdown mode |
| Game | World of Warcraft |
| Class | Addons |
| Main category | Buffs & Debuffs |
| Additional categories | Mage, Combat, HUDs; use the matching options offered by the form |
| License | MIT License — same as the repository's `LICENSE` |
| Source | https://github.com/1nd1v1d/Forever_Frost_Alert |
| Issues | https://github.com/1nd1v1d/Forever_Frost_Alert/issues |
| Website | https://github.com/1nd1v1d/Forever_Frost_Alert#readme |
| Upload | `dist/ForeverFrostAlert-0.1.2-forever.zip` |
| File display name | Forever Frost Alert 0.1.2 - Forever (Beta) |
| File type | **Beta** |
| Flavor / supported version | **Forever / 1.60.1** only |
| Changelog | Paste `docs/publication/RELEASE_NOTES.md` |
| Required CurseForge dependencies | None |

`Blizzard_AuraContainer` is a game component and must not be added as a CurseForge project dependency. The ZIP contains the `ForeverIcyVeins` folder with the TOC, Lua source, license and notices. Do not upload GitHub's source ZIP, the publication kit or a backup folder as the addon download.

## Submit the project

1. Sign into the [CurseForge author portal](https://authors.curseforge.com/#/projects/create/choose-game).
2. Select World of Warcraft and fill in the project fields above.
3. Upload the original PNG logo. Paste the English project description and choose MIT License.
4. Enable comments, leave Experimental off, and allow third-party distribution if you want other addon managers to access the file. These are recommended preferences, not mandatory fields.
5. Create the project. Set its Source, Issues and Website links where available.
6. Upload the installable ZIP. Select **Forever**, **1.60.1**, **Beta**, and paste the release notes. Choose your desired publication timing in the release options.
7. Submit the project/file for moderation. Watch the author dashboard for approval or requested changes; approval is controlled by CurseForge.
8. Record the assigned project ID and real CurseForge URL in `project-metadata.json`. Add the real URL to the README; do not use the suggested slug as if it were an approved page.

The initial Beta deliberately does not claim full live validation. CurseForge's guidance says a project needs at least one **Release** file before it syncs to the app. After the live checks below pass, a regular Release can be uploaded. Do not relabel the beta as validated merely to gain app visibility.

## Live checks before a stable release

- Verify that `/fiv test` shows both arcs and ends after five seconds.
- Trigger **Fingers of Frost** in combat; check the alert appears.
- Consume one charge, then the last charge; check the alert remains until the buff is gone.
- Let the buff expire; check the alert disappears.
- Reload with the buff active; verify the native display reconnects.
- Verify scale, position and opacity survive relogging.

The preview was confirmed in game before public preparation; the corrected proc trigger has not yet been confirmed in this chat. The logo is branding only. A real in-game screenshot of the effect would be a useful optional gallery image; label a `/fiv test` capture as a preview. No gameplay screenshot is supplied or fabricated.

## Future releases

Update the version in the TOC and Lua status string, changelog, release notes and metadata. Build and run the tests:

```sh
python scripts/build.py
python tests/run_tests.py
```

Commit and push the reviewed files. Create a version tag and a GitHub release with the installable ZIP and `.sha256` asset. Upload that same ZIP to CurseForge with the matching client flavor, version, release type and changelog. Automated CurseForge publishing is not configured; no API token or project ID has been invented.

## Official references

Requirements were checked on 2026-11-10:

- [Project Submission Guide and Tips](https://support.curseforge.com/support/solutions/articles/9000199552-project-submission-guide-and-tips): distinct name, original square PNG logo of at least 400 × 400 pixels, summary, categories, description and license.
- [Creating and Submitting a Project](https://support.curseforge.com/support/solutions/articles/9000197241): English titles/descriptions, ZIP upload, release type, supported versions and moderation.
