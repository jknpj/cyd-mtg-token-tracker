#include "../src/table_state.h"

#include <assert.h>
#include <stdio.h>

int main() {
  using namespace tabletop;
  static_assert(sizeof(DeckBook) == 1236, "deck save layout changed");
  static_assert(sizeof(Match) == 280, "match save layout changed");
  DeckBook book;
  assert(book.count(456) == 456);
  book.active = 1;
  assert(book.count(456) == 0);
  assert(book.next(42, 1, 456) == 42);
  book.decks[0].toggle(0);
  book.decks[0].toggle(455);
  assert(book.count(456) == 2);
  assert(book.next(0, -1, 456) == 455);
  assert(book.next(455, 1, 456) == 0);
  assert(book.next(0, 1, 456) == 455);
  book.decks[0].toggle(455);
  assert(book.next(0, -1, 456) == 0);
  book.decks[0].toggle(TOKEN_CAPACITY - 1);
  book.decks[0].toggle(TOKEN_CAPACITY);
  assert(book.decks[0].contains(TOKEN_CAPACITY - 1));
  assert(!book.decks[0].contains(TOKEN_CAPACITY));
  book.active = 2;
  assert(!book.includes(0));
  book.active = 0;
  assert(book.includes(0));

  Match match;
  match.reset(8, 20);
  assert(match.valid() && match.life[7] == 20);
  assert(match.adjustLife(7, -25) && match.life[7] == -5);
  assert(!match.adjustLife(8, 1));
  assert(match.adjustDamage(7, 0, 0, 20));
  assert(!match.commanderLethal(7));
  assert(match.adjustDamage(7, 0, 1, 20));
  assert(!match.commanderLethal(7));  // Partners' damage must not be added for the 21 threshold.
  assert(match.adjustDamage(7, 0, 1, 1));
  assert(match.commanderLethal(7));
  assert(match.life[7] == -46);
  assert(match.adjustDamage(7, 0, 1, -5));
  assert(!match.commanderLethal(7) && match.life[7] == -41);
  assert(match.adjustDamage(7, 0, 1, -99));
  assert(match.damage[7][0][1] == 0 && match.life[7] == -25);
  assert(!match.adjustDamage(7, 0, 1, -1));
  assert(!match.adjustDamage(7, 0, 2, 1));
  assert(match.adjustDamage(0, 0, 0, 21));  // A stolen commander can damage its owner.
  assert(match.commanderLethal(0));
  match.life[0] = -LIFE_LIMIT;
  const uint16_t previous = match.damage[0][0][0];
  assert(!match.adjustDamage(0, 0, 0, 1));
  assert(match.damage[0][0][0] == previous);
  match.reset(1, 40);
  assert(!match.commanderLethal(0) && match.damage[7][0][0] == 0 && match.life[7] == 40);
  assert(match.adjustDamage(0, 0, 0, 1000));
  assert(match.damage[0][0][0] == DAMAGE_LIMIT && match.life[0] == 40 - DAMAGE_LIMIT);
  assert(!match.adjustDamage(0, 0, 0, 1));
  match.players = 9;
  assert(!match.valid());
  match.reset(8, 1);
  match.damage[7][7][1] = DAMAGE_LIMIT + 1;
  assert(!match.valid());
  match.reset(8, 40);
  for (uint8_t recipient = 0; recipient < MAX_PLAYERS; ++recipient) {
    for (uint8_t source = 0; source < MAX_PLAYERS; ++source)
      for (uint8_t commander = 0; commander < 2; ++commander)
        assert(match.adjustDamage(recipient, source, commander, 1));
    assert(match.life[recipient] == 24);
  }
  Match restored;
  memcpy(&restored, &match, sizeof(match));
  assert(restored.valid() && restored.life[7] == 24 && restored.damage[7][7][1] == 1);
  restored.initialLife = 0;
  assert(!restored.valid());
  restored = match;
  restored.version = 2;
  assert(!restored.valid());

  for (uint8_t sides : DIE_SIDES) {
    int counts[21] = {};
    for (uint32_t value = 1000 * sides; value < 1001u * sides; ++value)
      ++counts[roll(sides, [value]() { return value; })];
    for (uint8_t face = 1; face <= sides; ++face) assert(counts[face] == 1);
    assert(roll(sides, []() { return UINT32_MAX; }) <= sides);
  }
  unsigned calls = 0;
  assert(roll(6, [&calls]() { return calls++ == 0 ? 0u : 7u; }) == 2);
  assert(calls == 2);
  for (uint8_t players = 1; players <= MAX_PLAYERS; ++players) {
    static uint8_t owner[320][240];
    memset(owner, 0xFF, sizeof(owner));
    for (uint8_t i = 0; i < players; ++i) {
      const Seat seat = seatOf(i, players, 240, 320);
      assert(seat.w > 0 && seat.h > 0 && seat.x >= 0 && seat.y >= 0 && seat.x + seat.w <= 240 && seat.y + seat.h <= 320);
      for (int y = seat.y; y < seat.y + seat.h; ++y)
        for (int x = seat.x; x < seat.x + seat.w; ++x) {
          assert(owner[y][x] == 0xFF);
          owner[y][x] = i;
        }
      for (int v = 0; v < seat.readerH(); ++v)
        for (int u = 0; u < seat.readerW(); ++u) {
          int px, py, ru, rv;
          seat.toScreen(u, v, px, py);
          assert(seat.toReader(px, py, ru, rv) && ru == u && rv == v);
        }
      int px, py;
      seat.toScreen(seat.readerW() / 2, 0, px, py);  // The top of each panel faces the middle of the table.
      if (seat.facing == FaceLeft) assert(px == seat.x + seat.w - 1);
      if (seat.facing == FaceRight) assert(px == seat.x);
      if (seat.facing == FaceTop) assert(py == seat.y + seat.h - 1);
      if (seat.facing == FaceBottom) assert(py == seat.y);
    }
    for (int y = 0; y < 320; ++y)
      for (int x = 0; x < 240; ++x) assert(owner[y][x] != 0xFF);
  }
  assert(seatOf(0, 4, 240, 320).facing == FaceLeft && seatOf(0, 4, 240, 320).y == 160);  // Clockwise from bottom left.
  assert(seatOf(1, 4, 240, 320).facing == FaceLeft && seatOf(1, 4, 240, 320).y == 0);
  assert(seatOf(2, 4, 240, 320).facing == FaceRight && seatOf(2, 4, 240, 320).y == 0);
  assert(seatOf(0, 5, 240, 320).facing == FaceBottom && seatOf(1, 2, 240, 320).facing == FaceTop);
  int u, v;
  assert(!seatOf(0, 2, 240, 320).toReader(10, 10, u, v));
  puts("Table state tests passed (decks, 8 players, partners, life bounds, dice, seats).");
}
