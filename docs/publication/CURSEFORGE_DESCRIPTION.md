# Forever Frost Alert

**Track your Fingers of Frost charges at a glance.**

Forever Frost Alert gives your mage a clear, Retail-style visual cue for **Fingers of Frost** in **World of Warcraft: Forever**. Glowing frost wings show how many charges remain, and an accelerating blink warns you when the buff is about to expire.

## Charge display

| Fingers of Frost charges | Visible wings |
| --- | --- |
| No active buff | Neither wing |
| One charge | Left wing |
| Two charges | Left and right wings |

When you spend a charge, the right wing disappears first. The left wing stays until you spend the last charge or the buff expires.

## Expiry warning

The wings remain steady while more than five seconds remain. During the **last five seconds**, the visible wings begin blinking, accelerating from approximately **one to four flashes per second** as time runs out.

The warning follows the buff's actual remaining duration. If a new proc refreshes the buff to more than five seconds, the wings become steady again. Consuming the buff or letting it expire clears the alert.

## What it does

- Lets you adjust the size, opacity and position.
- Saves your settings per character.
- Includes a five-second preview that demonstrates two charges, one charge and the accelerating blink. The preview ends when combat begins.
- Allows mouse clicks through the display.
- Works as a standalone addon, with no aura framework or other separately installed addon required.
- Provides English chat feedback and German feedback on German clients.

## Compatibility

**WoW Forever 1.60.1 only — interface 16001.**

This addon tracks the **Fingers of Frost proc and its remaining charges** on your mage. The wings indicate charges, and blinking warns you that the proc is about to expire. There is no timer, numeric counter or rotation helper.

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
