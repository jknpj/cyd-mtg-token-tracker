import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zlib

from tools import fetch_tokens as tokens


def face(name="Cat", type_line="Token Creature - Cat", power="1", toughness="1"):
    return {"name": name, "type_line": type_line, "colors": ["W"], "oracle_text": "",
            "power": power, "toughness": toughness, "layout": "token"}


class TokenCatalogTests(unittest.TestCase):
    def test_partition_layout_preserves_saves_and_fits_flash(self):
        partitions = {}
        for line in (tokens.ROOT / "partitions.csv").read_text().splitlines():
            if not line or line.startswith("#"):
                continue
            name, _, _, offset, size, *_ = [field.strip() for field in line.split(",")]
            partitions[name] = (int(offset, 0), int(size, 0))
        self.assertEqual(partitions["nvs"], (0x9000, 0x5000))
        self.assertEqual(partitions["app0"], (0x10000, 0x300000))
        self.assertGreaterEqual(partitions["tokenstore"][1], 128 * 1024)
        end = 0x9000
        for offset, size in sorted(partitions.values()):
            self.assertGreaterEqual(offset, end)
            end = offset + size
        self.assertLessEqual(end, 4 * 1024 * 1024)

    def test_search_reads_every_page(self):
        pages = [{"data": [{"name": "first"}], "has_more": True, "next_page": "next"},
                 {"data": [{"name": "last"}], "has_more": False}]
        with patch.object(tokens, "read_json", side_effect=pages) as read:
            self.assertEqual([card["name"] for card in tokens.search("tokens")], ["first", "last"])
            self.assertEqual(read.call_args_list[1].args, ("next",))

    def test_collection_batches_and_rejects_missing_cards(self):
        with patch.object(tokens, "read_json", side_effect=[{"data": ["first"]}, {"data": ["last"]}]) as read:
            self.assertEqual(tokens.collection(str(i) for i in range(76)), ["first", "last"])
            self.assertEqual(len(read.call_args_list[0].args[1]["identifiers"]), 75)
            self.assertEqual(len(read.call_args_list[1].args[1]["identifiers"]), 1)
        with patch.object(tokens, "read_json", return_value={"data": [], "not_found": [{"id": "missing"}]}):
            with self.assertRaisesRegex(RuntimeError, "could not resolve"):
                tokens.collection(["missing"])

    def test_flip_faces_inherit_images_and_keep_rotation(self):
        card = {"layout": "flip", "colors": [], "artist": "Artist", "image_uris": {"large": "image"},
                "card_faces": [{"name": "Royal"}, {"name": "Sorcerer"}]}
        faces = list(tokens.faces_of(card))
        self.assertEqual([face["flip_half"] for face in faces], [0, 1])
        self.assertTrue(all(face["image_uris"] == {"large": "image"} and face["artist"] == "Artist" for face in faces))

    def test_token_key_keeps_rules_types_and_variable_stats_distinct(self):
        original = face()
        for change in ({"type_line": "Token Artifact Creature - Cat"}, {"oracle_text": "Lifelink"},
                       {"colors": ["G"]}, {"power": "*"}, {"toughness": "1+*"}):
            self.assertNotEqual(tokens.face_key(original), tokens.face_key({**original, **change}))
        self.assertEqual(tokens.face_key(original), tokens.face_key({**original, "artist": "Other"}))

    def test_missing_source_fails_explicitly(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(tokens, "CATALOG_CACHE", Path(directory)), patch.object(tokens, "read_url", return_value=None):
                with self.assertRaisesRegex(RuntimeError, "No data"):
                    tokens.read_json("https://example.invalid/missing")

    def test_api_cache_includes_collection_payload(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(tokens, "CATALOG_CACHE", Path(directory)), patch.object(tokens, "REFRESH_CACHE", False):
                with patch.object(tokens, "read_url", return_value=b'{"data": []}') as read:
                    tokens.read_json("collection", {"identifiers": [{"id": "one"}]})
                    tokens.read_json("collection", {"identifiers": [{"id": "one"}]})
                    tokens.read_json("collection", {"identifiers": [{"id": "two"}]})
                    self.assertEqual(read.call_count, 2)

    def test_art_budget_compresses_without_dropping_shared_art(self):
        shared = {**face(), "image_uris": {"art_crop": "https://example.invalid/shared.jpg"}}
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "art.h"
            with patch.object(tokens, "ART_OUTPUT", output), patch.object(tokens, "ART_BYTE_BUDGET", 80):
                with patch.object(tokens, "Image"), patch.object(tokens, "download", return_value=b"image"):
                    with patch.object(tokens, "encode_art", side_effect=lambda image, whole, quality: b"x" * quality):
                        tokens.write_art([("Cat", shared), ("Same art", shared)], 123)
            text = output.read_text()
        self.assertIn("JPEG quality 80", text)
        self.assertIn("ART_DATA[80]", text)
        self.assertEqual(text.count('{0, 80, ""}'), 2)

    def test_sd_art_has_both_sizes_artists_and_catalog(self):
        with_art = {**face(), "artist": "Ana", "image_uris": {"art_crop": "https://example.invalid/a.jpg"}}
        without_art = {**face("Dog"), "artist": "Bo", "image_status": "missing"}
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "sdcard" / "mtgart"
            (output / "full").mkdir(parents=True)
            (output / "full" / "0009.jpg").write_bytes(b"stale")
            with patch.object(tokens, "SD_OUTPUT", output), patch.object(tokens, "Image"):
                with patch.object(tokens, "download", return_value=b"image"):
                    with patch.object(tokens, "encode_art", side_effect=lambda image, whole, quality, size, subsampling:
                                      f"{size[0]}x{size[1]} q{quality} s{subsampling}".encode()):
                        tokens.write_sd_art([("Cat", with_art), ("Dog", without_art)], 0x00FD8168)
            self.assertEqual((output / "catalog.txt").read_text(), "00FD8168\n")
            self.assertEqual((output / "artists.txt").read_text(), "Ana\n\n")
            self.assertEqual((output / "full" / "0001.jpg").read_bytes(), b"214x128 q90 s0")
            self.assertEqual((output / "classic" / "0001.jpg").read_bytes(), b"164x96 q90 s0")
            self.assertEqual(sorted(path.name for path in (output / "full").iterdir()), ["0001.jpg"])

    def test_deck_links_cover_precons_without_token_sets(self):
        decks = [
            {"type": "Commander Deck", "code": "CMD", "fileName": "Old", "releaseDate": "2011-06-17"},
            {"type": "Commander Deck", "code": "BLC", "fileName": "New", "releaseDate": "2024-08-02"},
            {"type": "Commander Deck", "code": "FUT", "fileName": "Future", "releaseDate": "2027-01-01"},
            {"type": "Theme Deck", "code": "IGN", "fileName": "Other", "releaseDate": "2020-01-01"},
        ]
        sets = [{"set_type": "token", "code": "tblc", "parent_set_code": "blc", "released_at": "2024-08-02"}]

        def read(url):
            if url.endswith("DeckList.json"):
                return {"data": decks}
            if url.endswith("/sets"):
                return {"data": sets}
            return {"data": {"mainBoard": [{"name": "Creator", "identifiers": {"scryfallId": url}}]}}

        creator = {"all_parts": [{"component": "token", "id": "linked"},
                                 {"component": "combo_piece", "id": "not-token"}]}
        with patch.object(tokens, "read_json", side_effect=read), patch.object(tokens, "search", return_value=[face()]):
            with patch.object(tokens, "collection", side_effect=[[creator], [face("Dog")]]) as collect:
                result, count, codes = tokens.commander_tokens("2026-10-24")
        self.assertEqual(count, 2)
        self.assertEqual(codes, ["tblc"])
        self.assertEqual({item["name"] for item in result}, {"Cat", "Dog"})
        self.assertEqual(len(collect.call_args_list[0].args[0]), 2)
        self.assertEqual(collect.call_args_list[1].args[0], {"linked"})

    def test_generation_preserves_prefix_and_symbols_and_deduplicates(self):
        cat = face()
        shark = face("Shark", "Token Creature - Shark", "*", "*")
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "catalog.h"
            with patch.object(tokens, "OUTPUT", output), patch.object(tokens, "SPECS", [("Cat", "w", 1, 1, "")]):
                with patch.object(tokens, "fetch", return_value=(cat, "")), patch.object(tokens, "drop_stale_art"):
                    with patch.object(tokens, "commander_tokens", return_value=([cat, shark, shark], 198, ["tblc"])):
                        with patch("sys.argv", ["fetch_tokens.py", "--no-art", "--as-of", "2026-10-24"]):
                            tokens.main()
            text = output.read_text()
        prefix = [("Cat", "Creature - Cat", "", True, 1, 1, "Color::White")]
        expected = zlib.crc32(json.dumps(prefix).encode()) & 0xFFFFFFFF
        self.assertIn(f"0x{expected:08X}u", text)
        self.assertEqual(text.count('{"Shark"'), 1)
        self.assertIn('Color::White, "*", "*"', text)


if __name__ == "__main__":
    unittest.main()
