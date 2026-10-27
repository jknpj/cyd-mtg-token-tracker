"""Capture README screenshots from a CYD running the `shots` debug build.

    pio run -e shots -t upload
    "%USERPROFILE%\\.platformio\\penv\\Scripts\\python.exe" tools/screenshot.py COM7 tap 120 60 wait 500 shot home

Steps run in order:
    tap X Y       tap at portrait screen coordinates (0-239, 0-319)
    hold X Y MS   press for MS milliseconds
    path X,Y X,Y ... end
                  drag through the points in one stroke (for doodles)
    wait MS       pause
    shot NAME     save docs/screenshots/NAME.png

Reflash the normal firmware afterwards (`pio run -e esp32dev -t upload`).
"""

import pathlib
import struct
import sys
import time
import zlib

import serial

SHOT_DIR = pathlib.Path(__file__).resolve().parent.parent / "docs" / "screenshots"


def open_port(name):
    port = serial.Serial()
    port.port = name
    port.baudrate = 115200
    port.timeout = 30
    # Keep DTR/RTS low so opening the port does not reset the board.
    port.dtr = False
    port.rts = False
    port.open()
    time.sleep(0.2)
    port.reset_input_buffer()
    return port


def send(port, line):
    port.write((line + "\n").encode())
    port.flush()


def read_shot(port):
    send(port, "S")
    while True:
        line = port.readline()
        if not line:
            raise TimeoutError("no screenshot header")
        if line.startswith(b"SHOT "):
            width, height = map(int, line.split()[1:3])
            break
        if line.strip():
            print("board:", line.decode(errors="replace").rstrip())
    size = (width + 1) * height * 2
    data = port.read(size)
    if len(data) != size:
        raise TimeoutError(f"short screenshot: {len(data)} of {size} bytes")
    return width, height, data


def rgb565_rows(width, height, data):
    stride = width + 1

    def pixel(y, x):
        # TFT_eSPI returns big-endian RGB565, as the panel sends it.
        offset = (y * stride + x) * 2
        return (data[offset] << 8) | data[offset + 1]

    for y in range(height):
        row = bytearray(b"\0")
        for x in range(width):
            # Readback arrives one byte late: true red sits in the green field, true green in the
            # blue field, and true blue in the next pixel's red field (each row has one extra pixel).
            value, after = pixel(y, x), pixel(y, x + 1)
            red, green, blue = (value >> 5) & 63, value & 31, (after >> 11) & 31
            row += bytes(((red * 255 + 31) // 63, (green * 255 + 15) // 31, (blue * 255 + 15) // 31))
        yield bytes(row)


def write_png(path, width, height, data):
    def chunk(kind, body):
        return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body))

    raw = b"".join(rgb565_rows(width, height, data))
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9))
    png += chunk(b"IEND", b"")
    path.write_bytes(png)


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    port = open_port(argv[0])
    steps = argv[1:]
    i = 0
    while i < len(steps):
        step = steps[i]
        if step == "tap":
            send(port, f"T {steps[i + 1]} {steps[i + 2]}")
            time.sleep(0.4)
            i += 3
        elif step == "hold":
            send(port, f"T {steps[i + 1]} {steps[i + 2]} {steps[i + 3]}")
            time.sleep(int(steps[i + 3]) / 1000 + 0.4)
            i += 4
        elif step == "wait":
            time.sleep(int(steps[i + 1]) / 1000)
            i += 2
        elif step == "path":
            # path X,Y X,Y ... end: one continuous stroke through the points.
            points = []
            i += 1
            while steps[i] != "end":
                points.append(tuple(int(v) for v in steps[i].split(",")))
                i += 1
            i += 1
            for (x0, y0), (x1, y1) in zip(points, points[1:]):
                count = max(1, int(max(abs(x1 - x0), abs(y1 - y0)) / 3))
                for k in range(count):
                    x = x0 + (x1 - x0) * k // count
                    y = y0 + (y1 - y0) * k // count
                    send(port, f"T {x} {y} 120")
                    time.sleep(0.03)
            send(port, f"T {points[-1][0]} {points[-1][1]} 60")
            time.sleep(0.4)
        elif step == "shot":
            SHOT_DIR.mkdir(parents=True, exist_ok=True)
            path = SHOT_DIR / f"{steps[i + 1]}.png"
            write_png(path, *read_shot(port))
            print(f"saved {path}")
            i += 2
        else:
            print(f"unknown step: {step}")
            return 2
    port.close()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
