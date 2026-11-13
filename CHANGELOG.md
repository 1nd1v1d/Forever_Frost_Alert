# Changelog

All project-specific source code was generated exclusively by AI, following the maintainer's instructions.

## 0.3.1 - 2026-11-13

- Adds explicit AI-code provenance to public descriptions, release notes and the English/German addon-list descriptions.
- Includes the AI disclosure in the packaged NOTICE file and documents the scope of the EU AI Act assessment.
- Documents automatic German/English language selection with English fallback.
- Changes release metadata and provenance notices; gameplay behavior is unchanged from 0.3.0.

## 0.3.0 - 2026-11-13

- Adds a small, movable settings window opened with `/fiv` or `/fiv options`.
- Adds a checkbox to disable the five-second expiry blink. Charge indicators remain active when blinking is off.
- Adds transparency (0–100%), size and horizontal/vertical position sliders, with preview and reset buttons.
- Saves all settings per character; preserves existing layouts and enables blinking by default for upgrades.
- Adds `/fiv blink on`, `/fiv blink off` and `/fiv help`; expands `/fiv alpha` to the full 0–1 opacity range.
- Closes the menu at combat start and prevents settings changes in combat.
- Adds automated coverage for menu interaction, persistent blink preferences, full transparency and combat protection.

The menu and native binding changes need live-client verification.

## 0.2.0 - 2026-11-12

- Shows the left frost wing for the first Fingers of Frost charge and the right wing for the second.
- Blinks the visible wings during the last five seconds, accelerating from approximately 1 to 4 flashes per second.
- Uses native application and duration bindings, so refreshes and charge consumption follow the actual buff.
- Updates `/fiv test` to demonstrate two charges, one charge and the accelerating expiry warning.
- Adds regression coverage for charge consumption, expiration, refreshes, blink timing and preview cancellation.

The new native rendering path is a beta and still needs live-client verification.

## 0.1.2 - 2026-11-10

Initial public beta of **Forever Frost Alert**.

- Displays two mirrored frost arcs while Fingers of Frost (buff ID 400670) is active on the player.
- Adds English chat feedback while retaining German messages for German clients.
- Preserves the original addon folder, saved settings and `/fiv` command.
- Adds an original project icon, English documentation, MIT license and distribution notices.
- Packages the addon with license and notice files plus a separate SHA-256 checksum.

The visual preview has been confirmed in game. Corrected proc detection is pending in-game confirmation.

## 0.1.1 - 2026-11-10

- Corrected the tracked buff from Icy Veins to Fingers of Frost.
- Migrated legacy Icy Veins overrides without resetting the layout.

## 0.1.0 - 2026-11-10

- Initial local version with frost artwork, preview, saved layout and native aura integration.
