# CurseForge upload guide

All project copy is in English. The current addon version is a **Beta**.
All project-specific source code was generated exclusively by AI, following the maintainer's instructions. Keep this disclosure in every public description and release announcement. See [AI transparency and scope](AI_TRANSPARENCY.md).
The GitHub repository and CurseForge project are public. GitHub release uploads can be automated after adding the author token; see the [API setup instructions in German](CURSEFORGE_API_SETUP_DE.md).

## Files to use

| Field or action | File / value |
| --- | --- |
| Name | **Forever Frost Alert** |
| Suggested slug | `forever-frost-alert` — subject to availability |
| Summary | Code generated exclusively by AI. Fingers of Frost charge wings for WoW Forever, with optional blinking and settings for transparency, size and position. |
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
| Upload | `dist/ForeverFrostAlert-0.3.1-forever.zip` |
| File display name | Forever Frost Alert 0.3.1 - Forever (Beta) |
| File type | **Beta** |
| Flavor / supported version | **Forever / 1.60.1** only |
| Changelog | Paste `docs/publication/RELEASE_NOTES.md` |
| Required CurseForge dependencies | None |

`Blizzard_AuraContainer` and `Blizzard_UIPanelTemplates` are game components and must not be added as CurseForge project dependencies. The ZIP contains the `ForeverIcyVeins` folder with the TOC, Lua source, license and notices. Do not upload GitHub's source ZIP, the publication kit or a backup folder as the addon download.

The existing CurseForge project is [Forever Frost Alert](https://www.curseforge.com/wow/addons/forever-frost-alert), project ID **1796931**. Upload this update to that project and replace its description with the prepared text; a second project is not needed.

## Update the existing project manually

1. Sign into the [CurseForge author portal](https://authors.curseforge.com/) and open the existing **Forever Frost Alert** project, ID **1796931**.
2. Check the project fields above.
3. Upload the original PNG logo if needed. Paste the English project description and choose MIT License.
4. Enable comments, leave Experimental off, and allow third-party distribution if you want other addon managers to access the file. These are recommended preferences, not mandatory fields.
5. Set its Source, Issues and Website links where available.
6. Upload the installable ZIP. Select **Forever**, **1.60.1**, **Beta**, and paste the release notes. Choose your desired publication timing in the release options.
7. Submit the project/file for moderation. Watch the author dashboard for approval or requested changes; approval is controlled by CurseForge.
8. Check the public project page after approval.

The initial Beta deliberately does not claim full live validation. CurseForge's guidance says a project needs at least one **Release** file before it syncs to the app. After the live checks below pass, a regular Release can be uploaded. Do not relabel the beta as validated merely to gain app visibility.

## Live checks before a stable release

- Verify that `/fiv test` starts with both wings, removes the right wing halfway through, blinks progressively faster and ends after five seconds.
- Trigger **Fingers of Frost** in combat; check the alert appears.
- Consume one charge: only the left wing should remain. Consume the last charge: neither wing should remain.
- Let the buff reach five seconds remaining; verify that the visible wings start blinking and blink increasingly fast.
- Refresh the buff during blinking; verify that the wings become steady again if more than five seconds remain.
- Let the buff expire; check the alert disappears.
- Reload with the buff active; verify the native display reconnects.
- Verify scale, position and opacity survive relogging.
- Open `/fiv`, disable blinking and verify the charge wings remain steady in the last five seconds.
- Move the transparency slider, including both endpoints, and verify the menu remains visible even when the wings are fully transparent.
- Confirm that the blink preference and transparency survive relogging; check Preview and Reset.

The new menu and native binding changes are not yet verified in the live client. The logo is branding only. A real in-game screenshot of the effect would be a useful optional gallery image; label a `/fiv test` capture as a preview. No gameplay screenshot is supplied or fabricated.

## Future releases

Update the version in the TOC and Lua status string, changelog, release notes and metadata. Build and run the tests:

```sh
python scripts/build.py
python tests/run_tests.py
python -m unittest discover -s tests -p 'test_curseforge_upload.py'
```

Commit and push the reviewed files. Create a matching version tag and publish a GitHub release with the installable ZIP and `.sha256` asset. The **Publish to CurseForge** workflow rebuilds and tests that tag, then uploads it to project **1796931** using the repository secret **CF_API_TOKEN**. GitHub pre-releases become CurseForge Beta files; regular releases become Release files. An upload receipt attached to the GitHub release prevents duplicate workflow uploads.

Follow the [API setup instructions](CURSEFORGE_API_SETUP_DE.md) to create the token, store it and run a dry run. Existing releases can be processed with `workflow_dispatch`; dry-run mode is enabled by default. A missing token stops a real upload with a clear error. The upload API sends the file and its changelog; project description, icon and categories still need the author portal. Manual upload remains available as described above, but do not upload the same version both manually and through the workflow.

## Official references

Requirements were checked on 2026-11-10:

- [Project Submission Guide and Tips](https://support.curseforge.com/support/solutions/articles/9000199552-project-submission-guide-and-tips): distinct name, original square PNG logo of at least 400 × 400 pixels, summary, categories, description and license.
- [Creating and Submitting a Project](https://support.curseforge.com/support/solutions/articles/9000197241): English titles/descriptions, ZIP upload, release type, supported versions and moderation.
- [Upload API](https://support.curseforge.com/support/solutions/articles/9000197321-curseforge-upload-api): author tokens, multipart file upload and supported game-version names (checked on 2026-11-13).
