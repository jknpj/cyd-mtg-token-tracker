# MTG Tokens on the CYD 2.8"

**English** | [Português (Brasil)](README.pt-BR.md)

Offline firmware for browsing 455 MTG token/emblem entries (plus `Custom`) and tracking their in-play quantities using the touchscreen. The catalog covers the 198 Commander precons listed by the sources through 2026-10-24, including staples, Rin and Seri's Cat and Dog tokens, and Mabel's Cragflame. It includes three screen layouts, adjustable brightness and automatic screen timeout, and token search.

## Target board

This project targets the CYD ESP32-2432S028R, with an ILI9341 display and XPT2046 resistive touchscreen. The configured pinout is the common one for this variant:

- Display (HSPI): SCLK 14, MISO 12, MOSI 13, CS 15, DC 2, backlight 21 (PWM)
- Touch (dedicated VSPI bus): SCLK 25, MISO 39, MOSI 32, CS 33, IRQ 36

Other CYD revisions may use a different controller or pinout. Check the markings on your board before flashing.

Brightness is controlled with PWM (LEDC) directly on the backlight pin, `BACKLIGHT_PIN` in `src/main.cpp`. For this reason, `platformio.ini` does not define `TFT_BL`: the TFT_eSPI library must not control that pin.

## Build and flash

1. Open this folder in VS Code with the PlatformIO extension installed.
2. Run **PlatformIO: Build** to compile.
3. Connect the board over USB and run **PlatformIO: Upload** to flash it.
4. Open the serial monitor at 115200 baud to follow startup, if desired.

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

## "For each" abilities

Tokens with rules text like "gets +1/+1 for each [other] TYPE you control" have their P/T calculated automatically, counting tokens of that type in play across the tracker (from each token's type line):

- `Rat (Vren)`: +1/+1 for each *other* Rat (both Vren's Rats and regular Rats).
- `Construct`: +1/+1 for each artifact, including itself (Treasure, Clue, Food, etc. count).

The current bonus appears as a green seal (for example, `Rats +4/+4`) and is included in P/T. For non-token permanents (Vren himself, actual artifacts), use the `Rat cards` / `Artifact cards` row on that token's counters screen. At quantity 0, the displayed P/T is what the token would have as it enters. Role and Aura abilities are not calculated. `Custom` is also checked, so a custom creature with this text works the same way.

## Artwork

Each token displays the illustration from its Scryfall printing, with the artist's name at the bottom of the card. Artwork is generated by `tools/fetch_tokens.py` into `src/token_art_generated.h` (up to 2.5 MB) and is excluded from version control because it is Wizards of the Coast intellectual property. Without this file, the firmware still compiles, using frame colors instead of artwork.

To fit more than 450 tokens in flash, each token stores a single JPEG at the artwork size used by the full-screen layouts (214x128, 4:2:0 color). The Classic layout scales this image on the board to 164x96. The generator lowers JPEG quality in steps of 5 only as much as needed to fit everything; the selected quality is recorded at the top of `src/token_art_generated.h`. Original quality (85) for every token would require 4 to 8 MB, more than the board's 4 MB of flash.

The script adjusts images for the display: it crops them to the artwork area and darkens the midtones of very bright artwork (`ART_MAX_MEAN`), which can blow out on the CYD's TN panel. Colors on this panel also change significantly with viewing angle: when the board lies flat on the table, the card looks washed out and white cards look overexposed. For this reason, the white frame is cream (rather than the brightest white the panel can show), and **CARD TONE** and **SCREEN** are available on the second settings page. If all colors (not only light ones) look overexposed, the panel's gamma is usually the cause: see **DISPLAY GAMMA** on the third page. Because the artwork is large, `platformio.ini` uses the `huge_app.csv` partition table, and flashing takes longer.

### High-quality artwork on microSD

The generator also writes every token's artwork at high quality (JPEG quality 90, 4:4:4 color) to `sdcard/mtgart`, in both sizes (`full/` 214x128 and `classic/` 164x96, so the Classic layout needs no scaling), plus `artists.txt` and `catalog.txt`. To use it, copy the `mtgart` folder to the root of a FAT32 microSD card (the result must be `/mtgart/catalog.txt`), insert the card in the CYD's slot, and restart the board. The card is read only at startup.

The firmware reads each token's art from the card when available and falls back to the embedded flash art otherwise, so the board works the same without a card. The top-right corner of the settings pages shows the state: `SD HD ART` (in use), `SD: NO ART` (card without `/mtgart`), or `SD: OLD ART` (art generated for a different catalog, ignored; regenerate and copy it again). Nothing is shown without a card. Use `--no-sd-art` to skip this folder. The `sdcard/` folder is excluded from version control.

The CYD's microSD slot uses the VSPI pins (SCK 18, MISO 19, MOSI 23, CS 5); the touch controller uses the same SPI peripheral on other pins, so the firmware switches the pins around each card access.

Quantities, counters, modifiers, and the selected token are saved in flash (NVS) and restored when the board restarts.

## Settings

The gear (or the **SET** button in the token list) opens settings. There are three pages; **<** / **>** change pages, and **BACK** returns.

Page 1:

- **BRIGHTNESS**: 10 brightness levels, from 10% to 100%. Use **-** / **+** or tap the bars to jump directly to a level.
- **SCREEN OFF AFTER**: idle time before the display turns off: 15 s, 30 s, 1, 2, 5, or 10 min, or `Never` (the default). The touch that wakes the screen only turns it on; it does not activate a button.
- **LAYOUT**: tap one of the thumbnails.
  - **Classic**: card with a button bar below and the gear and magnifying glass in the corners (default).
  - **Overlay**: card fills the screen and controls overlay the artwork: `<`, gear, magnifying glass, and `>` at the top; large **-** / **+** buttons beside the number; and the mode selector (`QTY`, `TAP`, `POW`, `TGH`) below it.
  - **Card only**: like Overlay, but controls disappear after 4 seconds without input, leaving only the card. The first touch brings the controls back without activating anything.

In full-screen layouts, tapping the artwork still taps the tokens, and tapping the name bar still opens the list. **BACK** returns to the card.

Page 2, for when the card looks bright, washed out, or overexposed, such as when the board lies flat on a table:

- **CARD TONE**: darkens the entire card (artwork, frame, text boxes, and mana icon) and lowers the white point to prevent white from blowing out: `ORIGINAL` (default) and `DARKER 1` through `DARKER 5`. The preview between **-** and **+** shows a thumbnail of the current token with the selected tone (grayscale for `Custom`). It applies to the card and layout thumbnails, but not the rest of the interface. If white still looks too bright, also reduce **BRIGHTNESS** on page 1.
- **SCREEN**: `NORMAL` or `FLIPPED`, which rotates the display 180 degrees (touch follows). The TN panel looks much better from one side than the other; when playing on a table, try both orientations by rotating the board.

Page 3, for when all colors look washed out or overexposed, not only light colors:

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

## Touch calibration

The initial limits in `src/main.cpp` are approximate. If buttons respond at the wrong positions, calibrate `TOUCH_X_MIN`, `TOUCH_X_MAX`, `TOUCH_Y_MIN`, and `TOUCH_Y_MAX`. If the axes are swapped, adjust the conversion of `point.x` and `point.y` in `handleTouch()`.

## Token catalog

Tokens come from `src/tokens_generated.h`, generated from the Scryfall API. Do not edit this file by hand. The generator preserves the staples at the start of `SPECS` in `tools/fetch_tokens.py` and adds tokens from precons:

- Discovers physical `Commander Deck` products in MTGJSON, including Secret Lair, up to the selected date.
- Queries the corresponding token sets in Scryfall and tokens linked to each card in those decklists. This also covers Commander 2011/2013 and other products without their own token set.
- Merges printings with the same name, types, colors, P/T, and rules text; different variants remain separate. Shared sets may add tokens not used by the decks.
- Rin and Seri have `Cat (Rin and Seri)`, **green 1/1**, and `Dog (Rin and Seri)`, **white 1/1**. The existing white Cat remains separate. `Cragflame (Mabel)` is the legendary Equipment token.
- Emblems are also included when available. This is not a list of every alternate-art printing, nor an engine that executes all Magic abilities.

To regenerate the catalog and artwork (internet required; artwork generation requires Pillow, `python -m pip install pillow`; without it or with `--no-art`, only the catalog is generated; downloaded images are cached in `tools/art_cache` and are not downloaded again):

```
%USERPROFILE%\.platformio\penv\Scripts\python.exe tools\fetch_tokens.py
```

API data is cached in `tools/catalog_cache`. Use `--refresh` to update the sources; use `--as-of YYYY-MM-DD` to limit precon release dates (the default is today). The included snapshot was generated with `--as-of 2026-10-24`. The generator processes every page and fails explicitly if it cannot resolve a required entry. JPEG quality is automatically lowered only as far as needed to fit all token artwork in the flash budget; color/tone curves and panel gamma are not changed.

To add a token, add a tuple to `SPECS` in the format `(name, colors, power, toughness, text[, label])` and run the script again:

- `colors`: letters `w`, `u`, `b`, `r`, `g`, or `c` (colorless).
- `power`: `None` for tokens without P/T, such as artifacts.
- `text`: `""` requires a token with no rules text, a string requires that text to appear, and `None` accepts any text.
- `label`: display name in the list when two tokens would otherwise have the same name, such as `Wurm (Deathtouch)` and `Wurm (Lifelink)`.

To test the generator without internet:

```
%USERPROFILE%\.platformio\penv\Scripts\python.exe -m unittest tools.test_fetch_tokens
```

### Precon coverage audit

`tools/check_precon_coverage.py` checks catalog coverage through a path independent of the MTGJSON decklists. It starts from Scryfall's own list of Commander products (sets of type `commander` and products with "Commander" in the name), walks every card printed in them, and verifies that every token they create (and every token in those products' token sets) is in the catalog. It also lists Commander-like decks outside the `Commander Deck` type and products without decklists. The script exits with an error if any token created by a precon card is missing:

```
cd tools
%USERPROFILE%\.platformio\penv\Scripts\python.exe check_precon_coverage.py --as-of 2026-10-24
```

Results for the 2026-10-24 snapshot:

- 198 MTGJSON `Commander Deck` decklists, all complete (100 cards). 47 of Scryfall's 52 Commander products have decklists. The five without decklists are not precons: Commander's Arsenal, Commander Collection Green/Black, the Baldur's Gate minigames, and Mystery Booster Commander Edition. Products outside the `Commander Deck` type are digital products (MTGO 2009, Arena Historic Brawl), collector boxes, and old Starter decks.
- 21,807 printings in 54 sets, 1,187 linked tokens, and 46 token sets; 460 distinct token faces.
- **No tokens missing among those created by precon cards.** The 29 tokens absent from the catalog are only made by cards not in any precon: Secret Lair drops, Mystery Booster Commander, and collector-booster extras (Legends Retold from DMC, Realms and Relics from LTC, and Marvel/Final Fantasy/TMNT Eternal extras).
- Game designations (Dungeon, Monarch/Initiative, Ring, Boss, Event, Experience/Poison counters) are not tokens because they are not permanents.

The generated file includes a `CATALOG_ID` and CRCs for list prefixes. If an expansion preserves all existing entries in the same order, quantities, selection, counters, names, and custom cards are preserved. Incompatible catalogs discard only token state, with a serial warning; `Custom` and settings remain preserved.

`partitions.csv` keeps the offsets of the application and original NVS and reserves a 128 KiB `tokenstore` NVS for the expanded catalog. Firmware automatically migrates old saves without erasing the original NVS. Flash normally with PlatformIO to update the partition table as well; do not use `erase_flash` for this update.
