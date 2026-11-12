# Changelog

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
