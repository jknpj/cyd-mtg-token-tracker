"""Builds src/tokens_generated.h and the token art in src/token_art_generated.h from Scryfall.

Run with the PlatformIO Python. The art needs Pillow (python -m pip install pillow); without it, or
with --no-art, only the catalog is written:
    %USERPROFILE%\\.platformio\\penv\\Scripts\\python.exe tools\\fetch_tokens.py
"""

import argparse
import datetime
import hashlib
import io
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import zlib
from pathlib import Path

try:
    from PIL import Image, ImageEnhance, ImageFilter
except ImportError:
    Image = None

API = "https://api.scryfall.com/cards/search"
HEADERS = {"User-Agent": "CYDTokenDisplay/1.0", "Accept": "application/json"}
ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "src" / "tokens_generated.h"
ART_OUTPUT = ROOT / "src" / "token_art_generated.h"
ART_CACHE = Path(__file__).resolve().parent / "art_cache"
CATALOG_CACHE = Path(__file__).resolve().parent / "catalog_cache"
REQUEST_DELAY = 0.2  # Scryfall asks for at least 50-100 ms between requests.
RETRIES = 5  # Attempts per query when Scryfall answers 429 Too Many Requests.

# Art box sizes of FULL_GEO and CLASSIC_GEO in src/main.cpp. Each token gets one JPEG per size, so
# the firmware never has to scale.
ART_SIZES = {"full": (214, 128), "classic": (164, 96)}
# Only the full layout's art is stored; the firmware scales it down for the classic layout, which
# halves the flash the art needs. Chroma at half resolution (4:2:0) saves another fifth.
ART_SIZE = ART_SIZES["full"]
JPEG_QUALITY = 85
ART_BYTE_BUDGET = 2_500_000  # Leave room for the program and expanded rules in the 3 MiB app.
REFRESH_CACHE = False
# Scryfall art crops are taller than the art boxes. Where the crop keeps its window, from 0 (top)
# to 1 (bottom); subjects tend to sit a little above the middle.
ART_FOCUS_Y = 0.4
# The CYD's TN panel washes out light pictures. Art brighter than this average luminance (0-255) gets
# its midtones darkened with a gamma curve until it gets there; darker art is left alone.
ART_MAX_MEAN = 112
TOKEN_LAYOUTS = {"token", "double_faced_token", "flip"}  # Role tokens use the flip layout.
# A Role card prints two Roles, the second upside down, each with a small portrait illustration
# beside its rules text; Scryfall's art crop shows the top half of the frame instead. Where the
# illustration of each half sits on the "large" card image, as (left, top, right, bottom) fractions.
FLIP_WINDOWS = ((0.070, 0.178, 0.364, 0.474), (0.636, 0.495, 0.930, 0.792))

# (name, colors, power, toughness, oracle[, label]) - power None means a noncreature token.
# oracle: "" requires no rules text, a string requires it to appear, None accepts any.
# label replaces the Scryfall name for tokens that would otherwise look identical in the picker.
SPECS = [
    # Commander staples come first, in the order they are listed here.
    ("Soldier", "w", 1, 1, ""),
    ("Spirit", "w", 1, 1, "Flying"),
    ("Zombie", "b", 2, 2, ""),
    ("Goblin", "r", 1, 1, ""),
    ("Saproling", "g", 1, 1, ""),
    ("Beast", "g", 3, 3, ""),
    ("Thopter", "c", 1, 1, "Flying"),
    ("Treasure", "c", None, None, "any color"),
    ("Food", "c", None, None, "gain 3 life"),
    ("Clue", "c", None, None, "Draw a card"),
    ("Blood", "c", None, None, "Discard a card"),
    ("Map", "c", None, None, "Explore"),
    ("Powerstone", "c", None, None, "nonartifact"),
    ("Incubator", "c", None, None, "Transform"),
    ("Phyrexian", "c", 0, 0, ""),
    ("Servo", "c", 1, 1, ""),
    ("Eldrazi Spawn", "c", 0, 1, "Sacrifice"),
    ("Eldrazi Scion", "c", 1, 1, "Sacrifice"),
    ("Construct", "c", 0, 0, "for each artifact"),
    ("Wurm", "c", 3, 3, "Deathtouch", "Wurm (Deathtouch)"),
    ("Wurm", "c", 3, 3, "Lifelink", "Wurm (Lifelink)"),
    ("Elf Warrior", "g", 1, 1, ""),
    ("Squirrel", "g", 1, 1, ""),
    ("Wolf", "g", 2, 2, ""),
    ("Elephant", "g", 3, 3, ""),
    ("Insect", "g", 1, 1, "Deathtouch", "Insect (Deathtouch)"),
    ("Angel", "w", 4, 4, "Flying"),
    ("Dragon", "r", 4, 4, "Flying"),
    ("Rat", "b", 1, 1, "for each other Rat", "Rat (Vren)"),
    # Everything else, by color.
    ("Human", "w", 1, 1, ""),
    ("Human Soldier", "w", 1, 1, ""),
    ("Cat", "w", 1, 1, ""),
    ("Bird", "w", 1, 1, "Flying"),
    ("Knight", "w", 2, 2, "Vigilance"),
    ("Pegasus", "w", 2, 2, "Flying"),
    ("Bird", "u", 1, 1, "Flying"),
    ("Faerie", "u", 1, 1, "Flying"),
    ("Merfolk", "u", 1, 1, ""),
    ("Homunculus", "u", 0, 1, ""),
    ("Drake", "u", 2, 2, "Flying"),
    ("Octopus", "u", 8, 8, ""),
    ("Rat", "b", 1, 1, ""),
    ("Bat", "b", 1, 1, "Flying"),
    ("Vampire", "b", 1, 1, "Lifelink"),
    ("Skeleton", "b", 1, 1, None),
    ("Germ", "b", 0, 0, ""),
    ("Zombie Army", "b", 0, 0, ""),
    ("Demon", "b", 5, 5, "Flying"),
    ("Devil", "r", 1, 1, "When this"),
    ("Elemental", "r", 1, 1, None),
    ("Insect", "g", 1, 1, ""),
    ("Snake", "g", 1, 1, ""),
    ("Plant", "g", 0, 1, ""),
    ("Spider", "g", 1, 2, "Reach"),
    ("Bear", "g", 2, 2, ""),
    ("Rhino", "g", 4, 4, "Trample"),
    ("Wurm", "g", 6, 6, ""),
    ("Citizen", "gw", 1, 1, ""),
    ("Spirit", "wb", 1, 1, "Flying"),
    ("Inkling", "wb", 2, 1, "Flying"),
    ("Pest", "bg", 1, 1, "dies"),
    ("Fractal", "gu", 0, 0, None),
    ("Myr", "c", 1, 1, ""),
    ("Gnome", "c", 1, 1, ""),
    ("Golem", "c", 3, 3, ""),
    ("Gold", "c", None, None, "Sacrifice"),
    ("Junk", "c", None, None, "Exile the top card"),
    ("Shard", "c", None, None, "Scry 1"),
    # Scryfall names the faces of the two-sided Role tokens without the word "Role".
    ("Young Hero", "c", None, None, None, "Young Hero Role"),
    ("Monster", "c", None, None, None, "Monster Role"),
    ("Royal", "c", None, None, None, "Royal Role"),
    ("Sorcerer", "c", None, None, None, "Sorcerer Role"),
    ("Wicked", "c", None, None, None, "Wicked Role"),
    ("Cursed", "c", None, None, None, "Cursed Role"),
    ("Virtuous", "c", None, None, None, "Virtuous Role"),
    ("Cat", "g", 1, 1, "", "Cat (Rin and Seri)"),
    ("Dog", "w", 1, 1, "", "Dog (Rin and Seri)"),
    ("Cragflame", "c", None, None, "Equipped creature", "Cragflame (Mabel)"),
]

COLOR_ENUM = {"W": "White", "U": "Blue", "B": "Black", "R": "Red", "G": "Green"}

ASCII_REPLACEMENTS = {
    "\u2014": "-", "\u2013": "-", "\u2212": "-", "\u2019": "'", "\u2018": "'",
    "\u201c": '"', "\u201d": '"', "\u2022": "*", "\u2026": "...",
}


def to_ascii(text):
    for source, target in ASCII_REPLACEMENTS.items():
        text = text.replace(source, target)
    return text.encode("ascii", "ignore").decode("ascii")


def ascii_name(name):
    """Artist names keep their letters without the accents the display font lacks (Nestor, not Nstor)."""
    return to_ascii(unicodedata.normalize("NFKD", name))


def clean_oracle(text):
    text = re.sub(r"\s*\([^)]*\)", "", text)  # Reminder text does not fit the card.
    text = re.sub(r"\{([^}]+)\}", r"\1", text)
    return to_ascii(text).strip()


def read_url(url, accept="application/json", data=None):
    """Returns the body of url, or None on 404. Retries on 429 Too Many Requests and network hiccups."""
    headers = {**HEADERS, "Accept": accept}
    if data is not None:
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, headers=headers, data=data)
    for attempt in range(RETRIES):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return response.read()
        except urllib.error.HTTPError as error:
            if error.code == 404:
                return None
            if error.code != 429 or attempt == RETRIES - 1:
                raise
            retry_after = error.headers.get("Retry-After", "")
            time.sleep(int(retry_after) if retry_after.isdigit() else 10 * (attempt + 1))
        except (urllib.error.URLError, TimeoutError, ConnectionError) as error:
            if attempt == RETRIES - 1:
                raise
            print(f"retrying after a network error: {error}", file=sys.stderr)
            time.sleep(5 * (attempt + 1))
        finally:
            time.sleep(REQUEST_DELAY)


def read_json(url, data=None):
    payload = json.dumps(data, sort_keys=True).encode() if data is not None else None
    key = url.encode() + (payload or b"")
    path = CATALOG_CACHE / (hashlib.sha256(key).hexdigest() + ".json")
    if path.exists() and not REFRESH_CACHE:
        return json.loads(path.read_text(encoding="utf-8"))
    body = read_url(url, data=payload)
    if body is None:
        raise RuntimeError(f"No data at {url}")
    data = json.loads(body)
    CATALOG_CACHE.mkdir(exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")
    return data


def search(query):
    url = API + "?" + urllib.parse.urlencode({"q": query, "order": "released", "dir": "desc"})
    cards = []
    while url:
        page = read_json(url)
        cards.extend(page["data"])
        url = page.get("next_page") if page.get("has_more") else None
    return cards


def faces_of(card):
    for half, face in enumerate(card.get("card_faces") or [card]):
        inherited = {key: card.get(key) for key in ("image_uris", "artist", "image_status")}
        face = {"colors": card.get("colors", []), **inherited,
                **{key: value for key, value in face.items() if value is not None}}
        face["flip_half"] = half if card.get("layout") == "flip" else None
        yield face


def commander_tokens(as_of):
    decks = read_json("https://mtgjson.com/api/v5/DeckList.json")["data"]
    decks = [deck for deck in decks if deck["type"] == "Commander Deck"
             and deck.get("releaseDate") and deck["releaseDate"] <= as_of]
    codes = {deck["code"].lower() for deck in decks}
    sets = read_json("https://api.scryfall.com/sets")["data"]
    # Include the dedicated Commander releases as well as precons sold with other sets.
    codes.update(item["code"] for item in sets
                 if item["set_type"] == "commander" and item["released_at"] <= as_of)
    token_sets = sorted(item["code"] for item in sets
                        if item["set_type"] == "token" and item.get("parent_set_code") in codes
                        and item["released_at"] <= as_of)
    if not decks or not token_sets:
        raise RuntimeError("Commander deck/token discovery returned no results")
    print(f"Commander source: {len(decks)} decks, {len(token_sets)} token sets, through {as_of}")
    query = "(" + " or ".join(f"e:{code}" for code in token_sets) + ") game:paper"
    faces = []
    for card in search(query):
        if card["layout"] not in TOKEN_LAYOUTS | {"emblem"}:
            continue
        faces.extend(faces_of(card))
    card_ids = set()
    for index, deck in enumerate(decks):
        data = read_json(f"https://mtgjson.com/api/v5/decks/{deck['fileName']}.json")["data"]
        for section in ("commander", "mainBoard", "sideBoard"):
            for card in data.get(section) or []:
                card_id = card.get("identifiers", {}).get("scryfallId")
                if not card_id:
                    raise RuntimeError(f"No Scryfall ID for {card['name']} in {deck['name']}")
                card_ids.add(card_id)
        if index % 25 == 0:
            print(f"Decklists: {index + 1}/{len(decks)}", flush=True)
    related = set()
    for card in collection(card_ids):
        related.update(part["id"] for part in card.get("all_parts", [])
                       if part["component"] == "token")
    for card in collection(related):
        faces.extend(faces_of(card))
    faces = [face for face in faces if any(word in face["type_line"]
                                          for word in ("Token", "Creature", "Artifact", "Enchantment", "Emblem"))]
    print(f"Checked {len(card_ids)} deck cards and {len(related)} linked token printings")
    return faces, len(decks), token_sets


def collection(ids):
    cards = []
    ids = sorted(ids)
    for start in range(0, len(ids), 75):
        print(f"Scryfall collection: {start + 1}/{len(ids)}", flush=True)
        page = read_json("https://api.scryfall.com/cards/collection",
                         {"identifiers": [{"id": card_id} for card_id in ids[start:start + 75]]})
        if page.get("not_found"):
            raise RuntimeError(f"Scryfall could not resolve {page['not_found']}")
        cards.extend(page["data"])
    return cards


def face_key(face):
    return (to_ascii(face["name"]), to_ascii(face["type_line"]).removeprefix("Token ").strip(),
            clean_oracle(face.get("oracle_text", "")), tuple(sorted(face["colors"])),
            face.get("power"), face.get("toughness"))


def matching_face(card, spec):
    name, colors, power, toughness, oracle = spec[:5]
    wanted_colors = set(colors.upper()) - {"C"}
    # Two-faced tokens (Incubator // Phyrexian, the Roles) keep stats and rules text on each face.
    for face in faces_of(card):
        if face["name"].lower() != name.lower():
            continue
        if set(face["colors"]) != wanted_colors:
            continue
        if ("Creature" in face["type_line"]) != (power is not None):
            continue
        if power is not None and (face.get("power"), face.get("toughness")) != (str(power), str(toughness)):
            continue
        text = clean_oracle(face.get("oracle_text", ""))
        if oracle == "" and text:
            continue
        if oracle and oracle.lower() not in text.lower():
            continue
        return face, text
    return None, None


def fetch(spec):
    name, colors, power, toughness = spec[:4]
    query = f't:token !"{name}" c={colors} game:paper'
    if power is not None:
        query += f" pow={power} tou={toughness}"

    matches = []
    for card in search(query):
        if card.get("layout") not in TOKEN_LAYOUTS:
            continue
        face, text = matching_face(card, spec)
        if face is not None:
            matches.append((face, text))
    # Prefer the plainest printing (shortest type line, then shortest rules text). min() keeps
    # Scryfall's newest-first order on ties.
    return min(matches, key=lambda match: (len(match[0]["type_line"]), len(match[1])), default=(None, None))


def c_string(value):
    return json.dumps(value)


def color_enum(card_colors):
    if not card_colors:
        return "Color::Colorless"
    if len(card_colors) > 1:
        return "Color::Multicolor"
    return "Color::" + COLOR_ENUM[card_colors[0]]


def stat(value):
    return int(value) if value and value.lstrip("-").isdigit() else 0


def download(url):
    """Returns the image bytes for a Scryfall image URL, from tools/art_cache when possible."""
    path = urllib.parse.urlparse(url).path.split("/")  # /art_crop/front/6/d/<id>.jpg
    cached = ART_CACHE / f"{path[1]}-{path[2]}-{path[-1]}"
    if cached.exists():
        return cached.read_bytes()
    data = read_url(url, accept="image/*")
    if data is None:
        return None
    ART_CACHE.mkdir(exist_ok=True)
    cached.write_bytes(data)
    return data


def cover(image, size):
    """Crops the image to the box's aspect ratio and scales it to fill the box."""
    width, height = size
    source_w, source_h = image.size
    if source_w * height > source_h * width:
        crop_w = source_h * width / height
        left = (source_w - crop_w) / 2
        box = (left, 0, left + crop_w, source_h)
    else:
        crop_h = source_w * height / width
        top = (source_h - crop_h) * ART_FOCUS_Y
        box = (0, top, source_w, top + crop_h)
    return image.resize(size, Image.Resampling.LANCZOS, box=box)


def fit_over_blur(image, size):
    """Fits a portrait illustration whole into the box, over a blurred and darkened fill of itself."""
    width, height = size
    scaled = cover(image, size).filter(ImageFilter.GaussianBlur(6))
    scaled = ImageEnhance.Brightness(scaled).enhance(0.55)
    scale = min(width / image.width, height / image.height)
    front = image.resize((round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS)
    scaled.paste(front, ((width - front.width) // 2, (height - front.height) // 2))
    return scaled


def flip_illustration(card_image, half):
    """Cuts one Role's illustration out of the card, turning the upside-down half around."""
    left, top, right, bottom = FLIP_WINDOWS[half]
    width, height = card_image.size
    region = card_image.crop((round(left * width), round(top * height), round(right * width), round(bottom * height)))
    return region.rotate(180) if half else region


def tame_bright(image):
    """Brings very light art down to ART_MAX_MEAN with one gamma curve, keeping black and white."""
    histogram = image.convert("L").histogram()
    total = sum(histogram)

    def mean(gamma):
        return sum(count * 255 * (level / 255) ** gamma for level, count in enumerate(histogram)) / total

    if mean(1.0) <= ART_MAX_MEAN:
        return image
    low, high = 1.0, 3.0
    for _ in range(20):
        middle = (low + high) / 2
        if mean(middle) > ART_MAX_MEAN:
            low = middle
        else:
            high = middle
    curve = [round(255 * (level / 255) ** high) for level in range(256)]
    return image.point(curve * 3)


def encode_art(image, whole=False, quality=JPEG_QUALITY):
    """Scales the art to the box (cropping it, or fitting it whole) and encodes a baseline JPEG."""
    scaled = tame_bright(fit_over_blur(image, ART_SIZE) if whole else cover(image, ART_SIZE))
    output = io.BytesIO()
    # Baseline (not progressive) JPEG: the decoder on the board only reads baseline.
    scaled.save(output, "JPEG", quality=quality, optimize=True, progressive=False, subsampling=2)
    return output.getvalue()


def art_url(face):
    if face.get("image_status") in ("missing", "placeholder"):
        return None
    uris = face.get("image_uris") or {}
    return uris.get("large" if face.get("flip_half") is not None else "art_crop")


def write_art(faces, catalog_id, quality=JPEG_QUALITY):
    """Writes ART_OUTPUT: one JPEG of the full layout's art box for each catalog entry, in catalog order."""
    blob = bytearray()
    entries = []
    encoded = {}  # Tokens that share an illustration share its bytes.
    for label, face in faces:
        url = art_url(face)
        data = download(url) if url else None
        if data is None:
            print(f"warning: no art for {label}", file=sys.stderr)
            entries.append((0, 0, ""))
            continue
        half = face.get("flip_half")
        key = (url, half)
        if key not in encoded:
            image = Image.open(io.BytesIO(data)).convert("RGB")
            if half is not None:
                image = flip_illustration(image, half)
            jpeg = encode_art(image, whole=half is not None, quality=quality)
            encoded[key] = [len(blob), len(jpeg)]
            blob += jpeg
        entries.append((*encoded[key], ascii_name(face.get("artist") or "")))

    if len(blob) > ART_BYTE_BUDGET:
        if quality <= 15:
            raise RuntimeError(f"Art exceeds the {ART_BYTE_BUDGET}-byte flash budget even at quality {quality}")
        print(f"Art: {len(blob)} bytes at quality {quality}; compressing to fit flash", flush=True)
        return write_art(faces, catalog_id, quality - (1 if quality <= 25 else 5))

    full_w, full_h = ART_SIZES["full"]
    classic_w, classic_h = ART_SIZES["classic"]
    lines = [
        "// Generated by tools/fetch_tokens.py from Scryfall art crops. Do not edit by hand.",
        "// The art is copyright Wizards of the Coast; the card shows each illustrator's name.",
        "#pragma once",
        "",
        "#include <stdint.h>",
        "",
        f"constexpr uint32_t ART_CATALOG_ID = 0x{catalog_id:08X}u;  // CATALOG_ID this art was made for.",
        f"// JPEG quality {quality}; art budget {ART_BYTE_BUDGET} bytes.",
        f"constexpr int ART_FULL_W = {full_w};",
        f"constexpr int ART_FULL_H = {full_h};",
        f"constexpr int ART_CLASSIC_W = {classic_w};",
        f"constexpr int ART_CLASSIC_H = {classic_h};",
        "",
        "// Offset and size of a baseline JPEG of the full layout's art box in ART_DATA; a zero size",
        "// means the token has no art. The classic layout scales it down.",
        "struct TokenArt {",
        "  uint32_t offset, size;",
        "  const char *artist;",
        "};",
        "",
        "const TokenArt TOKEN_ART[] = {",
    ]
    for offset, size, artist in entries:
        lines.append(f"    {{{offset}, {size}, {c_string(artist)}}},")
    lines += ["};", "", f"const uint8_t ART_DATA[{len(blob)}] = {{"]
    for start in range(0, len(blob), 32):
        lines.append(",".join(str(byte) for byte in blob[start:start + 32]) + ",")
    lines += ["};", ""]
    ART_OUTPUT.write_text("\n".join(lines), encoding="ascii", newline="\n")
    print(f"art for {sum(1 for entry in entries if entry[1])} tokens, {len(blob)} bytes, written to {ART_OUTPUT}")


def drop_stale_art(catalog_id):
    """Removes art made for another catalog: the firmware would refuse to build with it."""
    if not ART_OUTPUT.exists():
        return
    match = re.search(r"ART_CATALOG_ID = 0x([0-9A-F]{8})u", ART_OUTPUT.read_text(encoding="ascii"))
    if not match or int(match.group(1), 16) != catalog_id:
        ART_OUTPUT.unlink()
        print(f"removed {ART_OUTPUT}: it was made for another catalog", file=sys.stderr)


def main():
    global REFRESH_CACHE
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--no-art", action="store_true", help="only write the catalog, not the art")
    parser.add_argument("--refresh", action="store_true", help="refresh cached API data")
    parser.add_argument("--as-of", default=datetime.date.today().isoformat(), type=lambda s: datetime.date.fromisoformat(s).isoformat(),
                        help="include Commander precons released by this date (YYYY-MM-DD)")
    args = parser.parse_args()
    REFRESH_CACHE = args.refresh

    rows = []
    faces = []
    for spec in SPECS:
        face, text = fetch(spec)
        if face is None:
            raise RuntimeError(f"No Scryfall match for {spec}")
        label = spec[5] if len(spec) > 5 else face["name"]
        faces.append((label, face))

    discovered, deck_count, token_sets = commander_tokens(args.as_of)
    seen = {face_key(face) for _, face in faces}
    extras = {}
    for face in discovered:
        key = face_key(face)
        if key not in seen:
            extras.setdefault(key, face)
    names = {face["name"] for _, face in faces}
    used_labels = {label for label, _ in faces}
    for key, face in sorted(extras.items(), key=lambda item: item[0]):
        label = face["name"]
        if label in names:
            detail = "".join(face["colors"]) or "C"
            if "power" in face:
                detail += f" {face['power']}/{face['toughness']}"
            if face.get("keywords"):
                detail += " " + face["keywords"][0]
            label += f" ({detail})"
        base = label
        variant = 2
        while label in used_labels:
            label = f"{base} #{variant}"
            variant += 1
        used_labels.add(label)
        names.add(face["name"])
        faces.append((label, face))

    for label, face in faces:
        text = clean_oracle(face.get("oracle_text", ""))
        type_line = to_ascii(face["type_line"]).removeprefix("Token ").strip()
        row = (
            to_ascii(label), type_line, text, "power" in face,
            stat(face.get("power")), stat(face.get("toughness")), color_enum(face["colors"]),
        )
        symbols = tuple(value if value is not None and not str(value).lstrip("-").isdigit() else None
                        for value in (face.get("power"), face.get("toughness")))
        rows.append(row + symbols if any(symbols) else row)
        print(f"{label:<20} {type_line}")

    catalog_id = zlib.crc32(json.dumps(rows).encode()) & 0xFFFFFFFF
    lines = [
        "// Generated by tools/fetch_tokens.py from the Scryfall API. Do not edit by hand.",
        "#pragma once",
        "",
        '#include "token_types.h"',
        "",
        f"// {deck_count} Commander decklists and {len(token_sets)} token sets, released through {args.as_of}.",
        f"constexpr uint32_t CATALOG_ID = 0x{catalog_id:08X}u;",
        "// A saved catalog can migrate when its entries are an unchanged prefix of this one.",
        "const uint32_t CATALOG_PREFIX_IDS[] = {",
        *[f"    0x{zlib.crc32(json.dumps(rows[:end]).encode()) & 0xFFFFFFFF:08X}u,"
          for end in range(1, len(rows) + 1)],
        "};",
        "",
        "const Token CATALOG[] = {",
    ]
    for row in rows:
        name, type_line, text, has_pt, power, toughness, color = row[:7]
        symbols = (", " + ", ".join(c_string(value) if value is not None else "nullptr" for value in row[7:])
                   if len(row) > 7 else "")
        lines.append(
            f"    {{{c_string(name)}, {c_string(type_line)}, {c_string(text)}, "
            f"{'true' if has_pt else 'false'}, {power}, {toughness}, {color}{symbols}}},"
        )
    lines += ["};", ""]
    OUTPUT.write_text("\n".join(lines), encoding="ascii", newline="\n")
    print(f"\n{len(rows)} tokens written to {OUTPUT}")

    if args.no_art:
        drop_stale_art(catalog_id)
    elif Image is None:
        print("Pillow is not installed, so the art was not updated: python -m pip install pillow", file=sys.stderr)
        drop_stale_art(catalog_id)
    else:
        write_art(faces, catalog_id)


if __name__ == "__main__":
    main()
