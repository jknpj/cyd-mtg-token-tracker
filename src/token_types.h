#pragma once

#include <stdint.h>

enum class Color : uint8_t { White, Blue, Black, Red, Green, Multicolor, Colorless };

struct Token {
  const char *name;
  const char *type;
  const char *text;
  bool hasPT;
  int8_t power;
  int8_t toughness;
  Color color;
  const char *powerSymbol = nullptr;
  const char *toughnessSymbol = nullptr;
};
