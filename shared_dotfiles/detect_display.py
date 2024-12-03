#!/bin/env python3
import argparse
from dataclasses import dataclass
import json
import subprocess as sp
import re
from pathlib import Path
from typing import cast
from shared_dotfiles.python_helper import get_gsettings_color_scheme
import jc
from jc.jc_types import JSONDictType


def get_highest_resolution(associated_modes: list[JSONDictType]):
    return max(
        associated_modes, key=lambda x: x["resolution_width"] * x["resolution_height"]
    )


@dataclass
class Display:
    name: str
    width: int = -1
    height: int = -1

    def __init__(self, display: JSONDictType) -> None:
        self.name = display["device_name"]
        if len(display["modes"]) > 0:
            resolution = get_highest_resolution(display["modes"])
            self.width = resolution["resolution_width"]
            self.height = resolution["resolution_height"]


def get_displays() -> tuple[list[Display], list[Display]]:
    xrandr_out = sp.check_output(["xrandr"]).decode("utf-8")
    result = cast(JSONDictType, jc.parse("xrandr", xrandr_out))
    displays = result["screens"][0]["devices"]  # type: ignore
    connected = [x for x in displays if x["is_connected"]]
    disconnected = [x for x in displays if not x["is_connected"]]
    return list(map(lambda display: Display(display), connected)), list(
        map(lambda display: Display(display), disconnected)
    )


def run():
    parser = argparse.ArgumentParser(
        prog="detect_display",
        description="detects displays and enables them accordingly",
    )
    parser.add_argument("-b", "--background-path", default=Path.home())
    parser.add_argument("-d", "--desktops", nargs="+")
    args = parser.parse_args()

    connected_displays, disconnected = get_displays()

    print("detected displays:", connected_displays)
    print("disconnected displays:", ", ".join(display.name for display in disconnected))

    try:
        with open("/proc/acpi/button/lid/LID0/state") as lid_file:
            content = "\n".join(lid_file.readlines())
            if "closed" in content:
                print("Detected closed lid, disabling eDP")
                disconnected.append(
                    next(filter(lambda d: "eDP" in d.name, connected_displays))
                )
                connected_displays = list(
                    filter(lambda d: "eDP" not in d.name, connected_displays)
                )
    except FileNotFoundError:
        print("Cannot determine lid status")

    existing_desktops = sorted(
        sp.check_output(["bspc", "query", "-D", "--names"]).decode("utf-8").splitlines()
    )

    print(f"Setting {len(connected_displays)} monitors")
    xrandr_call = ["xrandr"]
    for d in disconnected:
        xrandr_call.extend(["--output", d.name, "--off"])
    x_pos = 0
    for d in connected_displays:
        xrandr_call.extend(
            [
                "--output",
                d.name,
                "--mode",
                f"{d.width}x{d.height}",
                "--primary",
                "--pos",
                f"{x_pos}x0",
                "--rotate",
                "normal",
            ]
        )
        x_pos += int(d.width)
        # add temp desktop because each screen always needs one
        sp.call(["bspc", "monitor", d.name, "-a", "Desktop"])
    # print(xrandr_call)
    sp.call(xrandr_call)
    target_desktops = existing_desktops if args.desktops is None else args.desktops
    desktop_per_display = len(target_desktops) // len(connected_displays)
    for i, desktop in enumerate(target_desktops):
        monitor_name = connected_displays[
            min(i // desktop_per_display, len(connected_displays) - 1)
        ].name
        if desktop in existing_desktops:
            sp.call(
                [
                    "bspc",
                    "desktop",
                    desktop,
                    "-m",
                    monitor_name,
                ]
            )
        else:
            sp.run(["bspc", "monitor", monitor_name, "-a", desktop], check=True)
    for d in disconnected:
        try:
            sp.call(
                ["bspc", "monitor", d.name, "-r"], stdout=sp.DEVNULL, stderr=sp.DEVNULL
            )
        finally:
            pass
    while "Desktop" in sp.check_output(["bspc", "query", "-D", "--names"]).decode(
        "utf-8"
    ):
        sp.call(["bspc", "desktop", "Desktop", "-r"])

    color_mode = get_gsettings_color_scheme()
    sp.call(
        ["feh", "--no-fehbg", "--bg-fill", f"{args.background_path}/{color_mode}.jpg"]
    )
