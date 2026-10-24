"""Checks that src/tokens_generated.h covers the tokens of every Commander precon.

Independent of the MTGJSON decklists that fetch_tokens.py reads: it starts from Scryfall's own list
of Commander products, takes every card printed in them, and checks that each token those cards make
(Scryfall's "all_parts") and each token printed alongside them is in the catalog. It also reports
MTGJSON precons outside the "Commander Deck" type and Commander products with no MTGJSON decklist,
which would point to a gap in fetch_tokens.py's discovery. Exits with 1 when something is missing:
    %USERPROFILE%\\.platformio\\penv\\Scripts\\python.exe tools\\check_precon_coverage.py --as-of 2026-10-24
"""

import argparse
import datetime
import json
import re
import sys
from collections import Counter

import fetch_tokens as ft

ROW = re.compile(r'^\s*\{("(?:[^"\\]|\\.)*"), ("(?:[^"\\]|\\.)*"), ("(?:[^"\\]|\\.)*"), (true|false), '
                 r'(-?\d+), (-?\d+), (Color::\w+)')
# Card names of the products that hold precon-only cards inside a bigger draft set.
COMMANDER_NAME = re.compile(r"commander|precon", re.IGNORECASE)


def catalog_rows():
    rows = []
    for line in ft.OUTPUT.read_text(encoding="ascii").splitlines():
        match = ROW.match(line)
        if match:
            label, type_line, text = (json.loads(group) for group in match.groups()[:3])
            rows.append((label, type_line, text, match[4] == "true", int(match[5]), int(match[6]), match[7]))
    return rows


def row_of(face):
    return (ft.to_ascii(face["type_line"]).removeprefix("Token ").strip(),
            ft.clean_oracle(face.get("oracle_text", "")), "power" in face,
            ft.stat(face.get("power")), ft.stat(face.get("toughness")), ft.color_enum(face["colors"]))


def is_catalog_face(face):
    # Same filter as fetch_tokens.commander_tokens: Dungeons, the Monarch, the Ring and so on are
    # tracked by the game, not as permanents.
    return any(word in face["type_line"] for word in ("Token", "Creature", "Artifact", "Enchantment", "Emblem"))


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--as-of", default=datetime.date.today().isoformat(),
                        type=lambda s: datetime.date.fromisoformat(s).isoformat())
    parser.add_argument("--refresh", action="store_true", help="refresh cached API data")
    args = parser.parse_args()
    ft.REFRESH_CACHE = args.refresh

    catalog = catalog_rows()
    by_fields = {}
    for label, *fields in catalog:
        by_fields.setdefault(tuple(fields), []).append(label)
    print(f"Catalog: {len(catalog)} entries in {ft.OUTPUT.name}")

    decks = [deck for deck in ft.read_json("https://mtgjson.com/api/v5/DeckList.json")["data"]
             if deck.get("releaseDate") and deck["releaseDate"] <= args.as_of]
    print("\nMTGJSON deck types through", args.as_of)
    for deck_type, count in sorted(Counter(deck["type"] for deck in decks).items()):
        print(f"  {count:4} {deck_type}")
    commander_decks = [deck for deck in decks if deck["type"] == "Commander Deck"]
    other = [deck for deck in decks if deck["type"] != "Commander Deck"
             and COMMANDER_NAME.search(deck["type"] + " " + deck["name"])]
    print(f"\nCommander-like decks outside the 'Commander Deck' type: {len(other)}")
    for deck in other:
        print(f"  {deck['releaseDate']} {deck['code']:5} {deck['type']}: {deck['name']}")

    sets = [item for item in ft.read_json("https://api.scryfall.com/sets")["data"]
            if item["released_at"] <= args.as_of and not item.get("digital")]
    deck_codes = {deck["code"].lower() for deck in commander_decks}
    products = sorted((item for item in sets if item["set_type"] == "commander"
                       or (COMMANDER_NAME.search(item["name"]) and item["set_type"] not in ("token", "memorabilia", "promo"))),
                      key=lambda item: item["released_at"])
    print(f"\nScryfall Commander products: {len(products)}; with MTGJSON Commander decklists: "
          f"{len([item for item in products if item['code'] in deck_codes])}")
    for item in products:
        if item["code"] not in deck_codes:
            print(f"  no MTGJSON Commander decklist: {item['released_at']} {item['code']:5} "
                  f"{item['set_type']}: {item['name']} ({item['card_count']} cards)")
    unknown = sorted(deck_codes - {item["code"] for item in products})
    print(f"MTGJSON Commander decklist codes outside those products: {', '.join(unknown) or 'none'}")

    codes = sorted({item["code"] for item in products} | deck_codes)
    token_sets = sorted(item["code"] for item in sets
                        if item["set_type"] == "token" and item.get("parent_set_code") in codes)
    related = {}
    printed = 0
    for index, code in enumerate(codes):
        try:
            cards = ft.search(f"e:{code} include:extras unique:prints")
        except RuntimeError:
            print(f"  no Scryfall cards in {code}")
            cards = []
        for card in cards:
            printed += 1
            for part in card.get("all_parts", []):
                if part["component"] == "token":
                    related.setdefault(part["id"], set()).add((card["name"], code))
        if index % 20 == 0:
            print(f"Scryfall sets: {index + 1}/{len(codes)}", flush=True)
    sources = {}
    for card in ft.collection(related):
        sources[card["id"]] = (card, related[card["id"]])
    query = "(" + " or ".join(f"e:{code}" for code in token_sets) + ") game:paper"
    for card in ft.search(query):
        sources.setdefault(card["id"], (card, {(f"token set {card['set']}", card["set"])}))
    print(f"\nChecked {printed} printings in {len(codes)} sets, {len(related)} linked token printings "
          f"and {len(token_sets)} token sets")

    # Names of every card in a precon decklist. A Commander product's set also holds cards that were
    # never in its decks (collector-booster extras, Secret Lair drops, Mystery Booster cards).
    precon_cards = set()
    for deck in commander_decks:
        data = ft.read_json(f"https://mtgjson.com/api/v5/decks/{deck['fileName']}.json")["data"]
        for section in ("commander", "mainBoard", "sideBoard"):
            for card in data.get(section) or []:
                precon_cards.add(card["name"])
                precon_cards.update(card["name"].split(" // "))

    def in_precon(source_names):
        return any(name.startswith("token set ") or name in precon_cards for name, _ in source_names)

    missing = {}
    skipped = Counter()
    checked = set()
    for card, source in sources.values():
        if card["layout"] not in ft.TOKEN_LAYOUTS | {"emblem"}:
            skipped[f"{card['name']} ({card['layout']})"] += 1
            continue
        for face in ft.faces_of(card):
            if not is_catalog_face(face):
                skipped[face["type_line"]] += 1
                continue
            fields = row_of(face)
            name = ft.to_ascii(face["name"])
            checked.add((name,) + fields)
            if not any(label.startswith(name) for label in by_fields.get(fields, [])):
                missing.setdefault((name,) + fields, set()).update(source)
    print(f"Distinct token faces checked: {len(checked)}")
    print("Not catalog entries (game designations or cards, not tokens):",
          ", ".join(f"{name} x{count}" for name, count in sorted(skipped.items())) or "none")

    gaps = {key: source for key, source in missing.items() if in_precon(source)}
    extras = {key: source for key, source in missing.items() if not in_precon(source)}
    for title, group in (("Missing tokens made by precon decklist cards", gaps),
                         ("Not in the catalog, made only by cards outside every precon decklist", extras)):
        print(f"\n{title}: {len(group)}")
        for (name, type_line, text, _, power, toughness, color), source in sorted(group.items()):
            made_by = "; ".join(sorted(f"{card} ({code})" for card, code in source))
            print(f"  {name} | {type_line} | {power}/{toughness} {color} | {text[:50]!r} <- {made_by}")
    return 1 if gaps else 0


if __name__ == "__main__":
    sys.exit(main())
