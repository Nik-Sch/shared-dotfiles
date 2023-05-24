#!/bin/env python3
import argparse
import subprocess as sp
import re
from pathlib import Path
from typing import List

from python_helper import get_gsettings_color_scheme

parser = argparse.ArgumentParser(
    prog="detect_display",
    description="detects displays and enables them accordingly",
)
parser.add_argument("-b", "--background-path", default=Path.home())
args = parser.parse_args()

xrandr_out = sp.check_output(["xrandr"]).decode("utf-8")
connected_displays: List[List[str]] = re.findall(
    r"^(\S+)\s+connected.*$\s*(\d+)x(\d+)", xrandr_out, re.M
)
disconnected_displays: List[str] = re.findall(r"^(\S+)\s+disconnected", xrandr_out, re.M)
if connected_displays == None:
    print("Failed to parse xrandr output")
    exit(1)
print(
    "detected displays:",
    ", ".join(f"{m[0]} ({m[1]}x{m[2]})" for m in connected_displays),
)
print(f'disconnected displays: {", ".join(disconnected_displays)}')


try:
    with open("/proc/acpi/button/lid/LID0/state") as lid_file:
        content = "\n".join(lid_file.readlines())
        if "closed" in content:
            print("Detected closed lid, disabling eDP")
            disconnected_displays.append(
                next(filter(lambda d: "eDP" in d[0], connected_displays), [""])[0]
            )
            connected_displays = list(
                filter(lambda d: "eDP" not in d[0], connected_displays)
            )
except FileNotFoundError:
    print("Cannot determine lid status")

existing_desktops = sorted(
    sp.check_output(["bspc", "query", "-D", "--names"]).decode("utf-8").splitlines()
)

print(f"Setting {len(connected_displays)} monitors")
xrandr_call = ["xrandr"]
for d in disconnected_displays:
    xrandr_call.extend(["--output", d, "--off"])
x_pos = 0
for d in connected_displays:
    xrandr_call.extend(
        [
            "--output",
            d[0],
            "--mode",
            f"{d[1]}x{d[2]}",
            "--primary",
            "--pos",
            f"{x_pos}x0",
            "--rotate",
            "normal",
        ]
    )
    x_pos += int(d[1])
    # add temp desktop because each screen always needs one
    sp.call(["bspc", "monitor", d[0], "-a", "Desktop"])
print(xrandr_call)
sp.call(xrandr_call)

desktop_per_display = int(len(existing_desktops) / len(connected_displays))
n = 0
for i, desktop in enumerate(existing_desktops):
    sp.call(
        [
            "bspc",
            "desktop",
            desktop,
            "-m",
            connected_displays[
                min(int(i / desktop_per_display), len(connected_displays) - 1)
            ][0],
        ]
    )
for d in disconnected_displays:
    try:
        sp.call(["bspc", "monitor", d, "-r"], stdout=sp.DEVNULL, stderr=sp.DEVNULL)
    finally:
        pass
while "Desktop" in sp.check_output(["bspc", "query", "-D", "--names"]).decode("utf-8"):
    sp.call(["bspc", "desktop", "Desktop", "-r"])

color_mode = get_gsettings_color_scheme()
sp.call(["feh", "--no-fehbg", "--bg-fill", f"{args.background_path}/{color_mode}.jpg"])
