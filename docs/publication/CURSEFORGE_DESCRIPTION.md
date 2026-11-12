# Forever Frost Alert

**See your Fingers of Frost proc without building a full aura setup.**

Forever Frost Alert shows glowing frost wings around the center of your screen while **Fingers of Frost** is active on your mage in **World of Warcraft: Forever**. One charge lights the left wing; two charges light both. When only five seconds remain, the visible wings start blinking and blink progressively faster until the buff expires or is consumed.

## What it does

- Tracks Fingers of Frost on your character.
- Shows the left wing for one charge and adds the right wing for the second charge.
- Blinks during the last five seconds, accelerating from about 1 to 4 flashes per second.
- Lets you adjust the size, opacity and position.
- Saves your settings per character.
- Includes a five-second preview, which ends when combat begins.
- Allows mouse clicks through the display.
- Requires no WeakAuras, Musca Auras, SpellActivationOverlay or other separately installed addon.
- Provides English chat feedback and German feedback on German clients.

## Compatibility

**WoW Forever 1.60.1 only — interface 16001.**

This addon is designed for a mage with Fingers of Frost. It tracks **Fingers of Frost**, not the separate **Icy Veins** cooldown. The wings indicate charges; there is no timer, numeric counter or rotation helper.

**Public beta:** the new charge display and accelerating expiry warning still need live-client verification. Please report problems with your exact client build and the output of `/fiv status`.

## Getting started

Install the Forever file, enable **Forever Frost Alert** and log in on your mage. Type `/fiv test` outside combat to see a preview.

For manual installation, extract the **ForeverIcyVeins** folder into:

```text
World of Warcraft/_forever_/Interface/AddOns/
```

The folder keeps its original name for compatibility. Do not rename it. Restart WoW if a newly installed folder is not detected; use `/reload` when updating an existing installation.

## Commands

| Command | What it does |
| --- | --- |
| `/fiv` | Show help |
| `/fiv test` | Preview two charges, then one, with accelerating blinking over five seconds |
| `/fiv scale 1.2` | Change size; range 0.5–2 |
| `/fiv alpha 0.8` | Change opacity; range 0.15–1 |
| `/fiv pos 0 -50` | Move relative to screen center; positive X moves right, positive Y moves up |
| `/fiv reset` | Restore defaults |
| `/fiv status` | Show the installed version and settings |

Change settings outside combat. The default layout is centered, at scale 1 and opacity 0.9.

If preview works but the proc does not appear, use `/fiv spell auto` to restore the default Fingers of Frost buff ID (400670), then `/reload`. The advanced `/fiv spell ID` command is available for troubleshooting a different client buff ID.

## Support and source

[Report a bug](https://github.com/1nd1v1d/Forever_Frost_Alert/issues) · [Source code](https://github.com/1nd1v1d/Forever_Frost_Alert) · [Changelog](https://github.com/1nd1v1d/Forever_Frost_Alert/blob/main/CHANGELOG.md)

MIT-licensed project source. The in-game artwork is referenced from the WoW client and is not bundled. The project icon is original AI-generated branding and is not a gameplay screenshot. This independent addon is not affiliated with or endorsed by Blizzard Entertainment.
