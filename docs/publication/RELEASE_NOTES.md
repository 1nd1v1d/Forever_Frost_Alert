# Forever Frost Alert 0.2.0 — Beta

Charge indicators and an accelerating expiry warning for Fingers of Frost on WoW Forever.

- Left wing for one Fingers of Frost charge; both wings for two charges (buff ID 400670).
- Blinking starts at five seconds remaining and accelerates from approximately 1 to 4 flashes per second.
- Native bindings follow the actual remaining duration and charges, including refreshes and consumption.
- Adjustable scale, opacity and position, saved per character.
- Five-second preview with `/fiv test` demonstrates both charges, consumption of one charge and accelerating blinking. It ends on entering combat.
- English chat messages with German messages on German clients.
- No separately installed addon dependencies.
- Includes the MIT license and asset notices.

**Compatibility:** WoW Forever 1.60.1, interface 16001. Extract the `ForeverIcyVeins` folder into `_forever_/Interface/AddOns/` and enable **Forever Frost Alert**. Updating an existing installation preserves its settings; use `/reload` after updating.

**Download:** `ForeverFrostAlert-0.2.0-forever.zip` is the installable addon. The `.sha256` file is its checksum. GitHub's automatic source archives are for development.

**Beta status:** the new native rendering path, charge indicators and accelerating warning need live-client verification. Automated Lua/API-contract tests do not replace in-game testing. Charges are shown by the wings, with no numeric counter or timer.

This release tracks **Fingers of Frost**, not **Icy Veins**. Older local versions that used the Icy Veins buff IDs are migrated automatically.

[Report an issue](https://github.com/1nd1v1d/Forever_Frost_Alert/issues) with your client build, `/fiv status` output and reproduction steps.
