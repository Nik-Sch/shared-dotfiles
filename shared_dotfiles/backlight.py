import argparse
import os
from pathlib import Path
from typing import Any, cast
import argcomplete


def parse_percentage(arg: Any):
    assert isinstance(arg, str)
    if arg.endswith("%"):
        percentage = float(arg[:-1]) / 100
    else:
        percentage = float(arg)
    assert (
        percentage > 0 and percentage <= 1
    ), f"Expected SET to be a percentage between 0 and 1 (or 0% and 100%) but is {percentage}"
    return percentage


def run():
    parser = argparse.ArgumentParser(
        description="""
        set the backlight intensity.
        If no argument is specified, the current brightness is printed.
        """,
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-q", "--query", action="store_true", help="Print the current brightness level."
    )
    group.add_argument(
        "-s", "--set", type=str, help="Set the brightness level in percent"
    )
    group.add_argument(
        "-i",
        "--increase",
        type=str,
        help="Increase the current brightness level by a percentage value",
    )
    group.add_argument(
        "-d",
        "--decrease",
        type=str,
        help="Decrease the current brightness level by a percentage value",
    )
    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    backlight_dir = Path("/sys/class/backlight/intel_backlight/")
    assert backlight_dir.exists(), f"{backlight_dir} does not exist"
    assert backlight_dir.is_dir(), f"{backlight_dir} is not a directory"
    max_file = backlight_dir / "max_brightness"
    brightness_file = backlight_dir / "brightness"
    assert os.access(max_file, os.R_OK), f"{max_file} is not readable"
    assert os.access(
        brightness_file, os.W_OK
    ), f"""
{brightness_file} is not writable.
To fix this, you may want to add a udev rule to give write access to users of the video group:
echo 'SUBSYSTEM=="backlight", ACTION=="add", \\
  RUN+="/bin/chgrp video /sys/class/backlight/%k/brightness", \\
  RUN+="/bin/chmod g+w /sys/class/backlight/%k/brightness"' | sudo tee /etc/udev/rules.d/90-backlight.rules
"""
    with open(max_file, "r") as f:
        max_brightness = int(f.read())
    with open(brightness_file, "r") as f:
        current_brightness = int(f.read())

    if args.query or not any(vars(args).values()):
        print(
            f"Current brightness is at {(current_brightness/max_brightness) * 100:.0f}% ({current_brightness} / {max_brightness})"
        )
    if args.set:
        percentage = parse_percentage(args.set)
        absolute_brightness = int(percentage * max_brightness)
        with open(brightness_file, "w") as f:
            f.write(str(absolute_brightness))
        print(
            f"Set brightness to {percentage * 100:.0f}% ({absolute_brightness} / {max_brightness})"
        )
    if args.increase:
        percentage = parse_percentage(args.increase)
        absolute_brightness = current_brightness + int(percentage * max_brightness)
        if absolute_brightness > max_brightness:
            absolute_brightness = max_brightness
        if absolute_brightness < 0:
            absolute_brightness = 0
        with open(brightness_file, "w") as f:
            f.write(str(absolute_brightness))
        print(
            f"Set brightness to {(absolute_brightness / max_brightness) * 100:.0f}% ({absolute_brightness} / {max_brightness})"
        )
    if args.decrease:
        percentage = parse_percentage(args.decrease)
        absolute_brightness = current_brightness - int(percentage * max_brightness)
        if absolute_brightness > max_brightness:
            absolute_brightness = max_brightness
        if absolute_brightness < 0:
            absolute_brightness = 0
        with open(brightness_file, "w") as f:
            f.write(str(absolute_brightness))
        print(
            f"Set brightness to {(absolute_brightness / max_brightness) * 100:.0f}% ({absolute_brightness} / {max_brightness})"
        )
