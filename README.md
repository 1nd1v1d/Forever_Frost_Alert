<p align="center">
  <img src="assets/branding/icon.png" width="180" alt="Forever Frost Alert frost emblem">
</p>

# Forever Frost Alert

**A focused Fingers of Frost proc alert for World of Warcraft: Forever.**

Glowing frost wings show your **Fingers of Frost** charges: one charge lights the left wing, and two charges light both wings. An optional accelerating blink warns you during the last five seconds. Open `/fiv` to adjust the display in a small settings window.

[Download the addon](https://github.com/1nd1v1d/Forever_Frost_Alert/releases) · [Report an issue](https://github.com/1nd1v1d/Forever_Frost_Alert/issues) · [Changelog](CHANGELOG.md)

## Features

- Tracks the **Fingers of Frost** buff, spell ID **400670**.
- Shows the left wing for one charge and adds the right wing for the second charge.
- Optional blinking at five seconds remaining, accelerating from about 1 to 4 flashes per second; enabled by default.
- Uses a native Blizzard aura container to control visibility.
- Settings window with a blink checkbox, 0–100% transparency, size and position sliders; saved per character.
- Five-second preview that ends automatically when combat starts.
- Click-through display with no additional addon dependencies.
- Menu and chat automatically use the WoW client's language: German or English, with English as the fallback for other languages.

This addon tracks the **Fingers of Frost proc and its remaining charges**. Charges are represented by the wings; there is no numeric counter, timer or rotation recommendation.

## Compatibility and release status

Built for **WoW Forever 1.60.1**, interface **16001**. Retail, Classic Era, TBC and MoP clients are not supported.

**Public beta:** the new settings window and native display changes still need live-client verification. Automated tests validate Lua behavior, menu controls, persistence, blink timing and the native API configuration but do not replace an in-game test. Please report any issue with the exact client build and `/fiv status` output.

## Installation

1. Download `ForeverFrostAlert-0.3.0-forever.zip` from [Releases](https://github.com/1nd1v1d/Forever_Frost_Alert/releases).
2. Extract the **ForeverIcyVeins** folder into `World of Warcraft/_forever_/Interface/AddOns/`.
3. Check that `AddOns/ForeverIcyVeins/ForeverIcyVeins.toc` exists.
4. Restart WoW if the new addon folder is not detected. Enable **Forever Frost Alert** in the addon list.
5. On a mage, type `/fiv` outside combat to open settings. Use **Preview** to see your current settings.

The folder keeps its original internal name for compatibility with earlier versions. Do not rename it. Existing settings and the `/fiv` command are preserved. Use the packaged release ZIP rather than GitHub's automatically generated source archive.

## Commands

| Command | Purpose |
| --- | --- |
| `/fiv` or `/fiv options` | Open the settings window |
| `/fiv help` | Show command help |
| `/fiv test` | Preview your settings for five seconds, starting with two charges and then showing one |
| `/fiv blink off` or `/fiv blink on` | Disable or enable the expiry blink |
| `/fiv scale 1.2` | Set scale, from 0.5 to 2; default 1 |
| `/fiv alpha 0.8` | Set opacity, from 0 (invisible) to 1 (opaque); default 0.9 |
| `/fiv pos 0 -50` | Move the alert relative to screen center; positive X is right, positive Y is up |
| `/fiv reset` | Restore the default layout and buff ID |
| `/fiv status` | Print the version, layout and tracked buff ID |
| `/fiv spell ID` | Override the buff ID for troubleshooting |
| `/fiv spell auto` | Restore Fingers of Frost, ID 400670 |

Preview and setting changes are available outside combat. The settings window closes when combat starts; `/fiv status` can also be used in combat. The menu's **Transparency** slider uses the inverse of opacity: 0% is fully visible, 100% is invisible. Turning blinking off keeps the remaining-charge wings steady until the buff is consumed or expires. Existing layout settings are preserved on update.

## Troubleshooting

**Preview works, but the proc does not show:** use `/fiv spell auto`, then `/reload`, and trigger Fingers of Frost. If it still fails, include your client build, `/fiv status`, any Lua error, and whether the issue happens inside or outside combat in a [bug report](https://github.com/1nd1v1d/Forever_Frost_Alert/issues/new?template=bug_report.yml).

**No preview:** confirm that the addon is enabled on a mage and that you are running the Forever client. The native `Blizzard_AuraContainer` component is provided by the game, not a separate CurseForge dependency.

**Unexpected position:** use `/fiv reset`, then adjust `/fiv scale` and `/fiv pos`.

## Development

The addon has no third-party runtime libraries. Two native `CustomAuraContainer` slots follow the same helpful player aura. Native application bars gate the wings at one and two charges. Native duration text bindings render the built-in frost artwork through static numeric-format rules: steady above five seconds, then increasingly short on/off intervals. Blizzard evaluates the real buff time and charges; Lua never reads or compares secret aura values. There is no addon-side aura polling, combat-log trigger or estimated buff timer.

Use Python 3.11+ and the test-only dependency in `requirements-dev.txt`:

```sh
python -m pip install -r requirements-dev.txt
python scripts/build.py
python tests/run_tests.py
python -m unittest discover -s tests -p 'test_curseforge_upload.py'
```

The build creates an installable ZIP and its SHA-256 checksum in `dist/`. The tests run the addon under Lua 5.1 with a restricted WoW API test double. Publisher tests use mocked HTTP and never need a real token. GitHub Actions runs the same checks.

Publishing a GitHub release triggers the **Publish to CurseForge** workflow. It builds and tests the tagged addon before uploading to CurseForge; pre-releases are uploaded as Beta files. Configure the repository secret `CF_API_TOKEN` once using the [step-by-step API setup guide (German)](docs/publication/CURSEFORGE_API_SETUP_DE.md). A manual dry run is available for existing releases. This automation publishes files and changelogs; project descriptions remain managed in the CurseForge author portal.

[Publishing guide](docs/publication/UPLOAD_GUIDE.md) · [CurseForge description](docs/publication/CURSEFORGE_DESCRIPTION.md) · [Project metadata](docs/publication/project-metadata.json)

## License and credits

Project source is licensed under the [MIT License](LICENSE). The in-game texture comes from the installed WoW client and is not included in the download. The original project icon is separate branding, not a gameplay screenshot. See [NOTICE](NOTICE) for asset and development references.

Independent addon; not affiliated with or endorsed by Blizzard Entertainment.
