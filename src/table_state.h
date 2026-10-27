#pragma once

#include <stddef.h>
#include <stdint.h>
#include <string.h>

namespace tabletop {

constexpr uint8_t MAX_DECKS = 8;
constexpr size_t DECK_NAME_LIMIT = 24;
constexpr size_t TOKEN_CAPACITY = 1024;
constexpr uint8_t MAX_PLAYERS = 8;
constexpr int LIFE_LIMIT = 9999;
constexpr uint16_t DAMAGE_LIMIT = 999;
constexpr uint8_t MAX_DICE = 20;
constexpr uint8_t DIE_SIDES[] = {2, 4, 6, 8, 10, 12, 20};

struct Deck {
  char name[DECK_NAME_LIMIT + 1] = {};
  uint8_t tokens[TOKEN_CAPACITY / 8] = {};

  bool contains(size_t token) const {
    return token < TOKEN_CAPACITY && (tokens[token / 8] & (1u << (token % 8)));
  }

  void toggle(size_t token) {
    if (token < TOKEN_CAPACITY) tokens[token / 8] ^= 1u << (token % 8);
  }
};

struct DeckBook {
  uint32_t version = 1;
  uint32_t catalog = 0;
  uint16_t catalogCount = 0;
  uint8_t active = 0;  // 0 is the full catalog, 1..MAX_DECKS are named decks.
  uint8_t reserved = 0;
  Deck decks[MAX_DECKS] = {};

  bool includes(size_t token) const {
    return active == 0 || (active <= MAX_DECKS && decks[active - 1].contains(token));
  }

  size_t count(size_t tokenCount) const {
    size_t result = 0;
    for (size_t i = 0; i < tokenCount; ++i) if (includes(i)) ++result;
    return result;
  }

  size_t next(size_t selected, int step, size_t tokenCount) const {
    if (!tokenCount) return selected;
    for (size_t i = 1; i <= tokenCount; ++i) {
      const size_t candidate = step < 0 ? (selected + tokenCount - i) % tokenCount
                                        : (selected + i) % tokenCount;
      if (includes(candidate)) return candidate;
    }
    return selected;
  }
};

struct Match {
  uint32_t version = 1;
  uint8_t players = 4;
  uint8_t reserved = 0;
  int16_t initialLife = 40;
  int16_t life[MAX_PLAYERS] = {};
  uint16_t damage[MAX_PLAYERS][MAX_PLAYERS][2] = {};  // Recipient, source player, commander.

  void reset(uint8_t count, int16_t initial) {
    players = count;
    initialLife = initial;
    for (auto &value : life) value = initial;
    memset(damage, 0, sizeof(damage));
  }

  bool valid() const {
    if (version != 1 || players < 1 || players > MAX_PLAYERS || initialLife < 1 || initialLife > LIFE_LIMIT)
      return false;
    for (size_t recipient = 0; recipient < MAX_PLAYERS; ++recipient) {
      if (life[recipient] < -LIFE_LIMIT || life[recipient] > LIFE_LIMIT) return false;
      for (size_t source = 0; source < MAX_PLAYERS; ++source)
        for (size_t commander = 0; commander < 2; ++commander)
          if (damage[recipient][source][commander] > DAMAGE_LIMIT) return false;
    }
    return true;
  }

  bool adjustLife(uint8_t player, int delta) {
    if (player >= players) return false;
    const int next = life[player] + delta;
    if (next < -LIFE_LIMIT || next > LIFE_LIMIT) return false;
    life[player] = next;
    return true;
  }

  bool adjustDamage(uint8_t recipient, uint8_t source, uint8_t commander, int delta) {
    if (recipient >= players || source >= players || commander >= 2) return false;
    uint16_t &value = damage[recipient][source][commander];
    int next = value + delta;
    if (next < 0) next = 0;
    if (next > DAMAGE_LIMIT) next = DAMAGE_LIMIT;
    if (next == value || !adjustLife(recipient, value - next)) return false;
    value = next;
    return true;
  }

  bool commanderLethal(uint8_t recipient) const {
    if (recipient >= players) return false;
    for (uint8_t source = 0; source < players; ++source)
      for (uint8_t commander = 0; commander < 2; ++commander)
        if (damage[recipient][source][commander] >= 21) return true;
    return false;
  }
};

// A player's panel on the life screen. The board lies in the middle of the table, so each panel is
// turned toward the edge its player sits at.
enum Facing : uint8_t { FaceBottom, FaceLeft, FaceTop, FaceRight };

struct Seat {
  int16_t x, y, w, h;
  uint8_t facing;

  // Size of the panel as its player reads it.
  int16_t readerW() const { return facing == FaceLeft || facing == FaceRight ? h : w; }
  int16_t readerH() const { return facing == FaceLeft || facing == FaceRight ? w : h; }

  // (u, v) is right and down for the player reading the panel.
  void toScreen(int u, int v, int &px, int &py) const {
    switch (facing) {
      case FaceLeft: px = x + w - 1 - v; py = y + u; break;
      case FaceTop: px = x + w - 1 - u; py = y + h - 1 - v; break;
      case FaceRight: px = x + v; py = y + h - 1 - u; break;
      default: px = x + u; py = y + v; break;
    }
  }

  bool toReader(int px, int py, int &u, int &v) const {
    if (px < x || py < y || px >= x + w || py >= y + h) return false;
    switch (facing) {
      case FaceLeft: u = py - y; v = x + w - 1 - px; break;
      case FaceTop: u = x + w - 1 - px; v = y + h - 1 - py; break;
      case FaceRight: u = y + h - 1 - py; v = px - x; break;
      default: u = px - x; v = py - y; break;
    }
    return true;
  }
};

// Height of the two side columns; an odd player count leaves a seat across the bottom.
inline int sideHeight(uint8_t players, int screenH) {
  if (players <= 2) return screenH;
  return players % 2 ? screenH - screenH / (players / 2 + 1) : screenH;
}

// Seats go clockwise around the table: the bottom seat, up the left column, down the right one.
inline Seat seatOf(uint8_t index, uint8_t players, int screenW, int screenH) {
  if (players <= 1) return {0, 0, int16_t(screenW), int16_t(screenH), FaceBottom};
  const int16_t halfH = screenH / 2;
  if (players == 2) {
    return index == 0 ? Seat{0, halfH, int16_t(screenW), int16_t(screenH - halfH), FaceBottom}
                      : Seat{0, 0, int16_t(screenW), halfH, FaceTop};
  }
  const int sideH = sideHeight(players, screenH);
  if (players % 2) {
    if (index == 0) return {0, int16_t(sideH), int16_t(screenW), int16_t(screenH - sideH), FaceBottom};
    --index;
  }
  const uint8_t rows = players / 2;
  const int rowH = sideH / rows;
  const int16_t halfW = screenW / 2;
  const bool left = index < rows;
  const uint8_t row = left ? rows - 1 - index : index - rows;
  const int16_t top = row * rowH;
  const int16_t height = row == rows - 1 ? sideH - top : rowH;
  return left ? Seat{0, top, halfW, height, FaceLeft}
              : Seat{halfW, top, int16_t(screenW - halfW), height, FaceRight};
}

// Reject the incomplete part of the uint32_t range rather than biasing dice with modulo.
template <typename Random>
uint8_t roll(uint8_t sides, Random random) {
  const uint32_t threshold = (uint32_t(0) - sides) % sides;
  uint32_t value;
  do { value = random(); } while (value < threshold);
  return static_cast<uint8_t>(value % sides + 1);
}

}  // namespace tabletop
