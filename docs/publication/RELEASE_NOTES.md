# Forever Frost Alert 0.1.2 — Beta

The first public beta of a small, standalone Fingers of Frost alert for WoW Forever.

- Two mirrored frost arcs while Fingers of Frost (buff ID 400670) is active.
- Adjustable scale, opacity and position, saved per character.
- Five-second preview with `/fiv test`; the preview ends on entering combat.
- English chat messages with German messages on German clients.
- No separately installed addon dependencies.
- Includes the MIT license and asset notices.

**Compatibility:** WoW Forever 1.60.1, interface 16001. Extract the `ForeverIcyVeins` folder into `_forever_/Interface/AddOns/` and enable **Forever Frost Alert**. Updating an existing installation preserves its settings; use `/reload` after updating.

**Download:** `ForeverFrostAlert-0.1.2-forever.zip` is the installable addon. The `.sha256` file is its checksum. GitHub's automatic source archives are for development.

**Beta status:** the visual preview has been confirmed in game. Corrected proc detection is pending in-game confirmation. Automated Lua/API-contract tests do not replace live-client testing. Both arcs show while the proc is active; there is no separate charge counter or timer.

This release tracks **Fingers of Frost**, not **Icy Veins**. Older local versions that used the Icy Veins buff IDs are migrated automatically.

[Report an issue](https://github.com/1nd1v1d/Forever_Frost_Alert/issues) with your client build, `/fiv status` output and reproduction steps.
