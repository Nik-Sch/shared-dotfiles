#!/bin/env python3

# requires i3lock-color
import argparse
import itertools
import re
import subprocess
from pathlib import Path

from .python_helper import get_gsettings_color_scheme


def run():
    parser = argparse.ArgumentParser(
        prog="lock",
        description="locks the screen",
    )
    parser.add_argument("-b", "--background-path", default=Path.home())
    args = parser.parse_args()

    color_mode = get_gsettings_color_scheme()

    font_large = 32
    font_medium = 16
    font_small = 12

    text_color = "ffffffff" if color_mode == "dark" else "000000ff"

    dpms_text = subprocess.check_output(
        [
            "xset",
            "q",
        ],
        encoding="utf8",
    )
    dpms_timeout = re.compile(r"Standby: (\d+)").search(dpms_text)

    # before lock:
    if dpms_timeout is not None:
        subprocess.call(["xset", "dpms", "5"])

    if subprocess.call(["pidof", "keepassxc"], stdout=subprocess.DEVNULL) == 0:
        subprocess.call(["keepassxc", "--lock"])

    params = {
        "-i": f"{args.background_path}/{color_mode}.jpg",
        "--ind-pos": "x+310:y+h-80",
        "--radius": "25",
        "--ring-width": "5",
        "--color": "000000ff",
        "--inside-color": "00000000",
        "--ring-color": "98c379ff",
        "--separator-color": "00000000",
        "--insidever-color": "00000000",
        "--insidewrong-color": "e06c75ff",
        "--ringver-color": "61afefff",
        "--ringwrong-color": "abb2bfff",
        "--keyhl-color": "e06c75ff",
        "--bshl-color": "e06c75ff",
        "--time-pos": "ix-265:iy-10",
        "--time-align": "1",
        "--time-str": "%H:%M:%S",
        "--time-color": f"{text_color}",
        "--time-size": f"{font_large}",
        "--date-str": "",
        "--greeter-pos": "ix-265:iy+12",
        "--greeter-align": "1",
        "--greeter-text": "You shall not pass!",
        "--greeter-color": f"{text_color}",
        "--greeter-size": f"{font_medium}",
        "--layout-pos": "ix-265:iy+32",
        "--layout-align": "1",
        "--layout-color": f"{text_color}",
        "--layout-font": "$font",
        "--layout-size": f"{font_small}",
        "--verif-pos": "ix+35:iy-34",
        "--verif-align": "2",
        "--verif-text": "Verifying...",
        "--verif-color": f"{text_color}",
        "--verif-size": f"{font_small}",
        "--wrong-pos": "ix+24:iy-34",
        "--wrong-align": "2",
        "--wrong-text": "Failure!",
        "--wrong-color": "d23c3dff",
        "--wrong-size": f"{font_small}",
        "--modif-pos": "ix+45:iy+43",
        "--modif-align": "2",
        "--modif-size": f"{font_small}",
        "--modif-color": "d23c3dff",
        "--noinput-text": "",
        "--keylayout": "0",
        "--screen": "$display_on",
    }

    subprocess.call(
        [
            "i3lock",
            *itertools.chain(*[[key, value] for key, value in params.items()]),
            "-f",
            "-L",
            "-n",
            "--line-uses-inside",
            "--clock",
            "--force-clock",
            "--pass-media-keys",
            "--pass-screen-keys",
            "--pass-volume-keys",
            "--pass-power-keys",
        ]
    )
    # restore dpms timeout
    if dpms_timeout is not None:
        subprocess.call(["xset", "dpms", dpms_timeout[1]])
