#!/bin/env python3
import argparse
import json
import subprocess
from pathlib import Path

import argcomplete

from .python_helper import get_gsettings_color_scheme


def set_bg(name: str):
    subprocess.call(
        [
            "feh",
            "--no-fehbg",
            "--bg-fill",
            name,
        ]
    )


def set_theme(name: str):
    subprocess.call(
        ["gsettings", "set", "org.gnome.desktop.interface", "gtk-theme", name]
    )


def set_color(name: str):
    subprocess.call(
        [
            "gsettings",
            "set",
            "org.gnome.desktop.interface",
            "color-scheme",
            name,
        ]
    )


def set_kitty(name: str):
    subprocess.call(
        [
            "kitty",
            "+kitten",
            "themes",
            "--reload-in=all",
            name,
        ]
    )


def set_vscode(name: str):
    settings_path = Path.home() / ".config/Code/User/settings.json"
    settings = json.loads(Path(settings_path).read_text(encoding="utf8"))
    settings["workbench.colorTheme"] = name
    settings_path.write_text(json.dumps(settings, indent=4))


def go_dark(background_path: str):
    set_color("prefer-dark")
    set_vscode("One Dark Pro")
    set_bg(f"{background_path}/dark.jpg")
    set_kitty("One Dark")


def go_light(background_path: str):
    set_color("prefer-light")
    set_vscode("Atom One Light")
    set_bg(f"{background_path}/light.jpg")
    set_kitty("Atom One Light")


def toggle():
    global COLOR_SCHEME
    if COLOR_SCHEME == "dark":
        COLOR_SCHEME = "light"
    else:
        COLOR_SCHEME = "dark"


COLOR_SCHEME = get_gsettings_color_scheme()


def run():
    print(f"Detected {COLOR_SCHEME} scheme")
    parser = argparse.ArgumentParser(
        prog="go mode",
        description="Sets/Toggles light dark mode",
    )
    parser.add_argument("-n", "--no-toggle", action="store_true")
    parser.add_argument("-b", "--background-path", default=Path.home())
    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    if not args.no_toggle:
        toggle()
    if COLOR_SCHEME == "dark":
        go_dark(args.background_path)
    else:
        go_light(args.background_path)
