# CYD MTG Token Tracker

**English** | [Português (Brasil)](README.pt-BR.md)

**Your token board, on a 2.8-inch touchscreen. No phone, Wi-Fi, or account needed during play.**

An offline Magic: The Gathering token tracker for the **CYD ESP32-2432S028R**. Browse tokens, track quantities and tapped copies, add counters, and keep everything saved between sessions.

| At a glance | |
| --- | --- |
| **455 catalog entries + Custom** | Tokens and emblems covering 198 Commander precon decklists in the 2026-10-24 snapshot |
| **Three layouts** | Classic controls, full-screen Overlay, or an unobstructed Card only view |
| **Counters and P/T** | +1/+1, named counters, ability counters, and supported "for each" bonuses |
| **Fast lookup** | Search names, types, rules text, colors, and P/T with the on-screen keyboard |
| **Optional microSD art** | Higher-quality JPEGs, with automatic fallback to embedded artwork |
| **Persistent state** | Quantities, counters, custom token, and display preferences saved in flash |

[UI tour](#ui-tour) · [Quick start](#quick-start) · [Controls](#controls) · [microSD](#high-quality-artwork-on-microsd) · [Settings](#settings) · [Catalog and development](#token-catalog)

## UI tour

| Classic | Overlay | Card only |
| :---: | :---: | :---: |
| <img src="docs/screenshots/layout-classic.png" alt="Classic layout with three custom tokens, counters, and a bottom control bar" width="240"> | <img src="docs/screenshots/layout-overlay.png" alt="Overlay layout with quantity controls over the card" width="240"> | <img src="docs/screenshots/layout-card-only.png" alt="Card only layout after the controls have hidden" width="240"> |
| Bottom control bar | Full-screen card with controls | Controls hide after 4 seconds |

| Counters | Search | Custom token editor |
| :---: | :---: | :---: |
| <img src="docs/screenshots/counters.png" alt="Counters page showing +1/+1, Shield, and Flying counters" width="240"> | <img src="docs/screenshots/search.png" alt="Search keyboard with the query green 3/3 and ten matches" width="240"> | <img src="docs/screenshots/editor.png" alt="Custom token editor with name, type, color, power, toughness, and rules fields" width="240"> |
| Track counters per token type | Combine color, P/T, and text | Make your own token |

*Actual firmware UI rendered by the PC test harness, not photos of the physical display. These captures use a custom token without card artwork; downloaded token illustrations are not included in the repository. Display gamma and viewing-angle effects are only visible on hardware. The device UI is in English in both README versions.*

## Quick start

### 1. Check your board

You need a **CYD ESP32-2432S028R**, with an **ILI9341** display and **XPT2046** resistive touch controller, a USB data cable, and [PlatformIO](https://platformio.org/install/ide?install=vscode) in VS Code. A microSD card is optional.

> **Check the board revision before flashing.** Other CYD variants may use a different display controller or pinout.

### 2. Build and upload

Open the project folder in VS Code. Use **PlatformIO: Build**, then **PlatformIO: Upload**, or run these commands from the project root:

```console
pio run -e esp32dev
pio run -e esp32dev -t upload
pio device monitor -b 115200
```

On Windows **Command Prompt**, if `pio` is not on your PATH:

```bat
"%USERPROFILE%\.platformio\penv\Scripts\pio.exe" run -e esp32dev -t upload -t monitor
```

[platformio.ini](platformio.ini) currently sets both USB ports to **COM7**. Change `upload_port` and `monitor_port` to your board's port if needed. Exit the serial monitor with **Ctrl+C** before another upload.

> **First build:** the catalog is included, but artwork is not. You can flash immediately and use colored placeholders, or [generate the artwork](#regenerating-the-catalog-and-artwork) before building.
>
> **Updating an existing board:** upload normally to preserve saves. Do not run `erase_flash`. The project uses [partitions.csv](partitions.csv), including a dedicated token-save partition.

### 3. Start playing

1. Tap the card's **name** to choose a token, or use the **magnifying glass** to search.
2. Use **+ / -** to change quantity; the center button switches between `QTY`, `TAP`, `POW`, and `TGH`.
3. Tap the **artwork** to tap or untap the group.
4. Tap the **rules box** to add counters. On `Custom`, use the bottom strip instead; the rules box opens its editor.
5. Open the **gear** to choose a layout and adjust the display. Changes are saved automatically.

## Hardware

| Component | Bus | Configured pins |
| --- | --- | --- |
| ILI9341 display | HSPI | SCLK 14, MISO 12, MOSI 13, CS 15, DC 2 |
| Backlight | LEDC / PWM | GPIO 21 |
| XPT2046 touch | VSPI | SCLK 25, MISO 39, MOSI 32, CS 33, IRQ 36 |
| microSD slot | VSPI, shared peripheral with touch | SCLK 18, MISO 19, MOSI 23, CS 5 |

The firmware switches VSPI pins around SD accesses, then restores the touch pins. Brightness is controlled directly by `BACKLIGHT_PIN` in [src/main.cpp](src/main.cpp); `TFT_BL` is intentionally not defined so TFT_eSPI does not control it.

## Controls

The token is displayed as a portrait card. The **Classic** layout (the default) has a bottom bar with these buttons:

- **<** / **>**: previous / next token.
- Center button: switches what **-** and **+** edit: `QTY` (in-play quantity), `TAP` (number tapped), `POW`, and `TGH` (power/toughness modifiers, creatures only). The edited item is highlighted in yellow on the card (P/T or tapped icon); quantity is not highlighted, to avoid framing the artwork, and the current mode is shown on the button. Counters (+1/+1 and others) are on the **counters** screen below.
- Tap the artwork to tap all untapped tokens, or untap all if they are already all tapped.
- Tap the name bar to open the paginated token list. Tap a name to select it; **<** / **>** change pages, **FIND** opens search, **BACK** returns to the card, and **SET** opens settings.
- The gear at the upper-left edge beside the card opens **settings**, and the magnifying glass at the upper-right edge opens **search**. In the other layouts, both icons are between the buttons over the artwork.

On the artwork, "IN PLAY", the quantity, and the untapped/tapped icons appear only when more than one token of that type is in play. With 0 or 1, the quantity appears for 2 seconds after it changes, then disappears to keep the artwork clear. When removing tokens, untapped ones are removed first. The position indicator (for example, `1/76`) appears briefly when changing tokens, then disappears. The mana icon beside the name indicates the color: sun (white), drop (blue), skull (black), flame (red), tree (green), five colored dots (multicolor), and diamond (colorless). The same icons appear in the list and the editor's color selector.

The first item in the list, `Custom`, is an editable token. With it selected, tap the lower part of the card (type and text) to open the editor for its name, type line, rules text, color, and P/T. Text fields use an on-screen keyboard, and **SAVE** stores the token in flash.

Displayed P/T already includes counters and modifiers. Tokens without P/T (such as artifacts) only let you edit quantity and tapped status.

Tokens with variable P/T preserve their printed symbols (`*/*`, `*/1+*`, etc.) instead of displaying them as 0/0. Their modifiers appear beside the symbols; the tracker does not know about zones such as graveyards or players' life totals, so it cannot resolve those abilities by itself. Cragflame is an Equipment: its text appears on the card, but equipping it and applying its bonus to another creature remain manual actions.

## Counters

Tap the card's text box (for `Custom`, tap the lower part where the seals appear) to open the counters screen. Each row has **-** and **+**; **<** / **>** change pages, and **BACK** returns to the card.

- `+1/+1` (creatures only): below zero, it becomes `-1/-1`. The total appears in the status line beside P/T and is included in the displayed P/T.
- `Custom`: one freely named counter per token. Tap its name (the one with the pencil) to rename it with the on-screen keyboard, up to 10 characters.
- Common counters: Shield, Stun, Oil, Charge, and Finality.
- Ability counters (blue): Flying, First strike, Double strike, Deathtouch, Lifelink, Trample, Vigilance, Menace, Reach, Hexproof, and Indestructible.

On the card, counters other than +1/+1 appear as seals at the bottom of the text box (above the status line on creatures). Ability counters show their number only when greater than one. If not all counters fit, their names are abbreviated and the remaining ones are shown as `+N`.

### Ygra's Food

For creatures, the last row on the counters screen is `Food (Ygra)`. **+** enables the marker and **-** removes it (0/1). It applies to all copies of that token, including copies added later, until removed. It does not create a separate Food token or remove the original types.

The marked creature gains `Artifact` and `Food` on its type line and a `Food (Ygra)` seal. It counts once for bonuses that count artifacts/Foods (for example, Construct) and appears in those searches. The marker is saved across restarts. Remove it when Ygra's effect no longer applies. The Food cost (`2, T, sacrifice: gain 3 life`) and sacrificing/gaining life are still handled manually during the game; the tracker does not track life totals.

## Automatic bonuses and rules limits

Tokens with rules text like "gets +1/+1 for each [other] TYPE you control" have their P/T calculated automatically, counting tokens of that type in play across the tracker (from each token's type line):

- `Rat (Vren)`: +1/+1 for each *other* Rat (both Vren's Rats and regular Rats).
- `Construct`: +1/+1 for each artifact, including itself (Treasure, Clue, Food, etc. count).

The current bonus appears as a green seal (for example, `Rats +4/+4`) and is included in P/T. For non-token permanents (Vren himself, actual artifacts), use the `Rat cards` / `Artifact cards` row on that token's counters screen. At quantity 0, the displayed P/T is what the token would have as it enters. Role and Aura abilities are not calculated. `Custom` is also checked, so a custom creature with this text works the same way.

> **A tracker, not a full rules engine.** Rin and Seri's Cat/Dog tokens and Mabel's Cragflame are in the catalog, but triggered abilities, equipping, sacrifices, life totals, and external game zones still require player input. The Ygra marker is manual; it does not detect Ygra entering or leaving the battlefield.

## Artwork

Each token displays the illustration from its Scryfall printing, with the artist's name at the bottom of the card. Artwork is generated by `tools/fetch_tokens.py` into `src/token_art_generated.h` (up to 2.5 MB) and is excluded from version control because it is Wizards of the Coast intellectual property. Without this file, the firmware still compiles, using frame colors instead of artwork.

To fit more than 450 tokens in flash, each token stores a single JPEG at the artwork size used by the full-screen layouts (214x128, 4:2:0 color). The Classic layout scales this image on the board to 164x96. The generator lowers JPEG quality in steps of 5 only as much as needed to fit everything; the selected quality is recorded at the top of `src/token_art_generated.h`. Original quality (85) for every token would require 4 to 8 MB, more than the board's 4 MB of flash.

The script adjusts images for the display: it crops them to the artwork area and darkens the midtones of very bright artwork (`ART_MAX_MEAN`), which can blow out on the CYD's TN panel. Colors on this panel also change significantly with viewing angle: when the board lies flat on the table, the card looks washed out and white cards look overexposed. For this reason, the white frame is cream (rather than the brightest white the panel can show), and **CARD TONE** and **SCREEN** are available on the second settings page. If all colors (not only light ones) look overexposed, see **DISPLAY GAMMA** on the third page. The application has a 3 MiB partition in [partitions.csv](partitions.csv); artwork makes uploads larger and slower.

### High-quality artwork on microSD

The generator also writes every token's artwork at **JPEG quality 90, 4:4:4 color** to `sdcard/mtgart`, in both sizes. Classic uses a native-size image instead of scaling the full-screen version.

1. [Generate the catalog and artwork](#regenerating-the-catalog-and-artwork).
2. Format a microSD card as **FAT32**.
3. Copy the entire generated **`mtgart` folder** to the card's root, keeping this structure:

   ```text
   /mtgart/
     catalog.txt
     artists.txt
     full/
       0001.jpg      # 214 x 128
       ...
     classic/
       0001.jpg      # 164 x 96
       ...
   ```

4. Insert the card in the CYD and **restart**. Card detection and catalog validation happen at boot; images are read on demand. Hot-swapping is not supported.

| Settings label | Meaning / action |
| --- | --- |
| `SD HD ART` | Matching SD artwork is available; individual missing images fall back to flash |
| `SD: NO ART` | Card mounted, but the artwork catalog file is missing or unreadable; copy the folder |
| `SD: OLD ART` | Catalog ID mismatch; regenerate and replace the entire folder |
| No label | No card mounted; embedded art is used |

**No card is required.** The firmware falls back to embedded art when an SD image cannot be opened, or colored placeholders if there is no embedded art either. Generated files in `sdcard/` are excluded from version control. Use `--no-sd-art` to skip generating them.

*SD loading has been exercised in the PC harness and the firmware build passes. Physical microSD operation still needs validation on the CYD.*

Quantities, counters, modifiers, and the selected token are saved in flash (NVS) and restored when the board restarts.

## Settings

The gear (or the **SET** button in the token list) opens settings. There are three pages; **<** / **>** change pages, and **BACK** returns.

| Layout and brightness | Card tone and orientation | Panel gamma |
| :---: | :---: | :---: |
| <img src="docs/screenshots/settings.png" alt="Settings page 1 with brightness, screen timeout, and layout previews" width="240"> | <img src="docs/screenshots/settings-tone.png" alt="Settings page 2 with card tone and screen orientation controls" width="240"> | <img src="docs/screenshots/settings-gamma.png" alt="Settings page 3 with gamma profile and grayscale and RGB test ramps" width="240"> |

### Page 1: brightness, timeout, and layout

- **BRIGHTNESS**: 10 brightness levels, from 10% to 100%. Use **-** / **+** or tap the bars to jump directly to a level.
- **SCREEN OFF AFTER**: idle time before the display turns off: 15 s, 30 s, 1, 2, 5, or 10 min, or `Never` (the default). The touch that wakes the screen only turns it on; it does not activate a button.
- **LAYOUT**: tap one of the thumbnails.
  - **Classic**: card with a button bar below and the gear and magnifying glass in the corners (default).
  - **Overlay**: card fills the screen and controls overlay the artwork: `<`, gear, magnifying glass, and `>` at the top; large **-** / **+** buttons beside the number; and the mode selector (`QTY`, `TAP`, `POW`, `TGH`) below it.
  - **Card only**: like Overlay, but controls disappear after 4 seconds without input, leaving only the card. The first touch brings the controls back without activating anything.

In full-screen layouts, tapping the artwork still taps the tokens, and tapping the name bar still opens the list. **BACK** returns to the card.

### Page 2: card tone and orientation

For when the card looks bright, washed out, or overexposed, such as when the board lies flat on a table:

- **CARD TONE**: darkens the entire card (artwork, frame, text boxes, and mana icon) and lowers the white point to prevent white from blowing out: `ORIGINAL` (default) and `DARKER 1` through `DARKER 5`. The preview between **-** and **+** shows a thumbnail of the current token with the selected tone (grayscale for `Custom`). It applies to the card and layout thumbnails, but not the rest of the interface. If white still looks too bright, also reduce **BRIGHTNESS** on page 1.
- **SCREEN**: `NORMAL` or `FLIPPED`, which rotates the display 180 degrees (touch follows). The TN panel looks much better from one side than the other; when playing on a table, try both orientations by rotating the board.

### Page 3: display gamma

For when all colors look washed out or overexposed, not only light colors:

- **DISPLAY GAMMA**: programs the panel's gamma curve. This board needs color inversion (`TFT_INVERSION_ON`) and often starts up with the wrong gamma, making everything too bright and low-contrast. **-** / **+** switch profiles; the selected profile takes effect immediately and whenever the board powers on:
  - `RECOMMENDED` (default): the manufacturer's gamma tables, with the curve reselected just after the display turns on; this is the adjustment the TFT_eSPI community reports for this board (issue 2985).
  - `NO INVERSION`: disables color inversion. If the display becomes a negative image, return to profile 1/3.
  - `ST7789 GAMMA`: ST7789 gamma tables, used by some clone panels.
- **TEST RAMPS**: grayscale, red, green, and blue gradients from black to full intensity, rendered directly by the panel without **CARD TONE**. On a well-adjusted panel each step differs from its neighbor and the first steps are dark; if bright steps blend together or dark steps already look gray, try another profile. After setting gamma, adjust **CARD TONE** and **BRIGHTNESS** if needed.

Settings are saved in flash (NVS), separately from tokens, and remain in effect when the catalog changes.

## Search

The magnifying glass or **FIND** button in the token list opens an on-screen keyboard. Type a query and confirm with **OK** to show matching tokens:

- Search is case-insensitive and matches substrings (`gob` finds Goblin).
- With multiple space-separated words, every word must match, in any order (`green 3/3` finds green 3/3 tokens).
- Each word is matched against the name, type line, rules text, color name (`white`, `blue`, `black`, `red`, `green`, `multicolor`, `colorless`), and P/T (`3/3`).
- **FIND** in the list refines the search while keeping the entered text; **BACK** on the keyboard cancels. Tapping the card's name bar always opens the full list, and **<** / **>** on the card continue to cycle through all tokens.

## Troubleshooting

| Symptom | What to check |
| --- | --- |
| Upload cannot open the port | Check the USB data cable, board port, and COM7 settings; close any other serial monitor |
| No token illustration | Expected on a fresh checkout; generate artwork before building, or prepare the microSD folder |
| SD art is ignored | Check FAT32, `/mtgart/catalog.txt`, the settings label, and restart after inserting the card |
| Colors look washed out | Try **DISPLAY GAMMA** first, then **CARD TONE**, brightness, and screen orientation |
| Buttons respond at the wrong positions | Check board revision and touch calibration below |

### Touch calibration

The initial limits in `src/main.cpp` are approximate. If buttons respond at the wrong positions, calibrate `TOUCH_X_MIN`, `TOUCH_X_MAX`, `TOUCH_Y_MIN`, and `TOUCH_Y_MAX`. If the axes are swapped, adjust the conversion of `point.x` and `point.y` in `handleTouch()`.

## Token catalog

Tokens come from `src/tokens_generated.h`, generated from the Scryfall API. Do not edit this file by hand. The generator preserves the staples at the start of `SPECS` in `tools/fetch_tokens.py` and adds tokens from precons:

- Discovers physical `Commander Deck` products in MTGJSON, including Secret Lair, up to the selected date.
- Queries the corresponding token sets in Scryfall and tokens linked to each card in those decklists. This also covers Commander 2011/2013 and other products without their own token set.
- Merges printings with the same name, types, colors, P/T, and rules text; different variants remain separate. Shared sets may add tokens not used by the decks.
- Rin and Seri have `Cat (Rin and Seri)`, **green 1/1**, and `Dog (Rin and Seri)`, **white 1/1**. The existing white Cat remains separate. `Cragflame (Mabel)` is the legendary Equipment token.
- Emblems are also included when available. This is not a list of every alternate-art printing, nor an engine that executes all Magic abilities.

### Regenerating the catalog and artwork

Run from the project root. Internet is required; Pillow is required for images. These commands use the PlatformIO Python on Windows Command Prompt:

```bat
"%USERPROFILE%\.platformio\penv\Scripts\python.exe" -m pip install pillow
"%USERPROFILE%\.platformio\penv\Scripts\python.exe" tools\fetch_tokens.py --as-of 2026-10-24
```

On other platforms, use `python -m pip install pillow` and `python tools/fetch_tokens.py --as-of 2026-10-24` with your Python environment.

| Option | Purpose |
| --- | --- |
| `--as-of YYYY-MM-DD` | Limit precon release dates; defaults to today. The included snapshot uses `2026-10-24` |
| `--refresh` | Refresh cached API responses |
| `--no-art` | Generate only the catalog |
| `--no-sd-art` | Generate catalog and embedded art, but skip the microSD folder |

API data is cached in `tools/catalog_cache`; downloaded images are reused from `tools/art_cache`. Without Pillow, only the catalog is generated. The generator processes every page and fails explicitly if it cannot resolve a required entry. JPEG quality is lowered only as far as needed to fit embedded artwork in flash; SD quality stays at 90. Color/tone curves and panel gamma are not changed. Rebuild and upload after regenerating embedded art; replace the SD folder too if the catalog changed.

### Adding an entry

To add a token, add a tuple to `SPECS` in the format `(name, colors, power, toughness, text[, label])` and run the script again:

- `colors`: letters `w`, `u`, `b`, `r`, `g`, or `c` (colorless).
- `power`: `None` for tokens without P/T, such as artifacts.
- `text`: `""` requires a token with no rules text, a string requires that text to appear, and `None` accepts any text.
- `label`: display name in the list when two tokens would otherwise have the same name, such as `Wurm (Deathtouch)` and `Wurm (Lifelink)`.

### Offline tests

```bat
"%USERPROFILE%\.platformio\penv\Scripts\python.exe" -m unittest tools.test_fetch_tokens
```

### Precon coverage audit

[tools/check_precon_coverage.py](tools/check_precon_coverage.py) checks catalog coverage through a path independent of the MTGJSON decklists. It starts from Scryfall's own list of Commander products (sets of type `commander` and products with "Commander" in the name), walks every card printed in them, and verifies that every token they create (and every token in those products' token sets) is in the catalog. It also lists Commander-like decks outside the `Commander Deck` type and products without decklists. The script exits with an error if any token created by a precon card is missing. Internet is required.

```bat
"%USERPROFILE%\.platformio\penv\Scripts\python.exe" tools\check_precon_coverage.py --as-of 2026-10-24
```

<details>
<summary>Coverage audit results: 2026-10-24 snapshot</summary>

Results for the 2026-10-24 snapshot:

- 198 MTGJSON `Commander Deck` decklists, all complete (100 cards). 47 of Scryfall's 52 Commander products have decklists. The five without decklists are not precons: Commander's Arsenal, Commander Collection Green/Black, the Baldur's Gate minigames, and Mystery Booster Commander Edition. Products outside the `Commander Deck` type are digital products (MTGO 2009, Arena Historic Brawl), collector boxes, and old Starter decks.
- 21,807 printings in 54 sets, 1,187 linked tokens, and 46 token sets; 460 distinct token faces.
- **No tokens missing among those created by precon cards.** The 29 tokens absent from the catalog are only made by cards not in any precon: Secret Lair drops, Mystery Booster Commander, and collector-booster extras (Legends Retold from DMC, Realms and Relics from LTC, and Marvel/Final Fantasy/TMNT Eternal extras).
- Game designations (Dungeon, Monarch/Initiative, Ring, Boss, Event, Experience/Poison counters) are not tokens because they are not permanents.

</details>

## Saves and firmware updates

The generated file includes a `CATALOG_ID` and CRCs for list prefixes. If an expansion preserves all existing entries in the same order, quantities, selection, counters, names, and custom cards are preserved. Incompatible catalogs discard only token state, with a serial warning; `Custom` and settings remain preserved.

`partitions.csv` keeps the offsets of the application and original NVS and reserves a 128 KiB `tokenstore` NVS for the expanded catalog. Firmware automatically migrates old saves without erasing the original NVS. Flash normally with PlatformIO to update the partition table as well; do not use `erase_flash` for this update.

## Credits

Catalog data and image references come from [Scryfall](https://scryfall.com/) and [MTGJSON](https://mtgjson.com/). The firmware uses [TFT_eSPI](https://github.com/Bodmer/TFT_eSPI), [XPT2046_Touchscreen](https://github.com/PaulStoffregen/XPT2046_Touchscreen), and [JPEGDEC](https://github.com/bitbank2/JPEGDEC).

Magic: The Gathering and its card artwork belong to Wizards of the Coast and their respective rights holders. This is an unofficial fan project, not affiliated with or endorsed by Wizards of the Coast. Downloaded artwork is not distributed in this repository.
