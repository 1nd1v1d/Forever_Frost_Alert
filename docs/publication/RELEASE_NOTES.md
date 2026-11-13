# Forever Frost Alert 0.3.1 — Beta

**AI disclosure: All project-specific source code was generated exclusively by AI, following the maintainer's instructions.** Documentation and the project icon were also AI-generated. The addon itself does not run an AI model.

This update adds the AI-code provenance notice to the addon-list descriptions and packaged notices. It also makes the automatic German/English language selection explicit in the documentation. Gameplay behavior is unchanged from 0.3.0.

A settings menu and an optional expiry blink for Fingers of Frost on WoW Forever.

- Open `/fiv` or `/fiv options` for a small, movable settings window.
- Disable the five-second expiry blink with a checkbox while keeping the charge wings visible.
- Set transparency from 0% (fully visible) to 100% (invisible).
- Adjust size and position with sliders; preview settings and reset to defaults.
- Settings save immediately per character. Existing layouts are preserved, and blinking is enabled by default.
- The menu closes when combat starts; changes are blocked during combat.
- Slash alternatives: `/fiv blink off`, `/fiv blink on`, `/fiv alpha 0–1` and `/fiv help`.

- Left wing for one Fingers of Frost charge; both wings for two charges (buff ID 400670).
- When enabled, blinking starts at five seconds remaining and accelerates from approximately 1 to 4 flashes per second.
- Native bindings follow the actual remaining duration and charges, including refreshes and consumption.
- Adjustable scale, opacity and position, saved per character.
- Five-second preview with `/fiv test` demonstrates both charges, consumption of one charge and your chosen blink setting. It ends on entering combat.
- Menu and chat messages follow the WoW client language: German or English, with English fallback for other languages.
- No separately installed addon dependencies.
- Includes the MIT license and asset notices.

**Compatibility:** WoW Forever 1.60.1, interface 16001. Extract the `ForeverIcyVeins` folder into `_forever_/Interface/AddOns/` and enable **Forever Frost Alert**. Updating an existing installation preserves its settings; use `/reload` after updating.

**Download:** `ForeverFrostAlert-0.3.1-forever.zip` is the installable addon. The `.sha256` file is its checksum. GitHub's automatic source archives are for development.

**Beta status:** the menu and native binding changes need live-client verification. Automated Lua/API-contract tests do not replace in-game testing. Charges are shown by the wings, with no numeric counter or timer.

This release tracks the **Fingers of Frost proc and its remaining charges**. Old buff-ID overrides from the initial local version are migrated automatically.

[Report an issue](https://github.com/1nd1v1d/Forever_Frost_Alert/issues) with your client build, `/fiv status` output and reproduction steps.
