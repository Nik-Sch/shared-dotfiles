#!/bin/env python3
import argparse
import re
import subprocess
import time
from pathlib import Path

from .python_helper import get_gsettings_color_scheme, is_hyprland


def _hyprpaper(*args: str) -> bool:
    """Silent with rc 0 on success, "error: ..." with rc 1 on failure."""
    result = subprocess.run(
        ["hyprctl", "hyprpaper", *args], capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"hyprpaper {' '.join(args)}: {result.stdout.strip()}")
        return False
    return True


def set_bg(name: str):
    if not is_hyprland():
        subprocess.call(["feh", "--no-fehbg", "--bg-fill", name])
        return

    if not Path(name).is_file():
        print(f"No such wallpaper: {name}")
        return
    # empty monitor means every monitor; hyprpaper may still be coming up when
    # this runs from the autostart, so give it a few seconds
    for _ in range(20):
        if _hyprpaper("wallpaper", f",{name},cover"):
            return
        time.sleep(0.25)
    print("hyprpaper is not answering, wallpaper unchanged")


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


def set_wezterm(name: str):
    # wezterm.lua reads this file and reloads itself when it changes
    path = Path.home() / ".local/state/wezterm-colorscheme"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{name}\n", encoding="utf8")


def set_vscode(name: str):
    settings_path = Path.home() / ".config/Code/User/settings.json"
    try:
        text = settings_path.read_text(encoding="utf8")
    except FileNotFoundError:
        print(f"No vscode settings at {settings_path}")
        return
    # settings.json is jsonc, so it is edited textually to keep the comments
    text, replaced = re.subn(
        r'("workbench\.colorTheme"\s*:\s*)"[^"]*"', rf'\1"{name}"', text, count=1
    )
    if replaced == 0:
        print("No workbench.colorTheme in the vscode settings")
        return
    settings_path.write_text(text, encoding="utf8")


def go_dark(background_path: str):
    set_color("prefer-dark")
    set_vscode("One Dark Pro")
    set_bg(f"{background_path}/dark.jpg")
    set_kitty("One Dark")
    set_wezterm("OneDark (base16)")


def go_light(background_path: str):
    set_color("prefer-light")
    set_vscode("Atom One Light")
    set_bg(f"{background_path}/light.jpg")
    set_kitty("Atom One Light")
    set_wezterm("One Light (base16)")


def toggle():
    global color_scheme
    if color_scheme == "dark":
        color_scheme = "light"
    else:
        color_scheme = "dark"


color_scheme = get_gsettings_color_scheme()


def run():
    print(f"Detected {color_scheme} scheme")
    parser = argparse.ArgumentParser(
        prog="go mode",
        description="Sets/Toggles light dark mode",
    )
    parser.add_argument("-n", "--no-toggle", action="store_true")
    parser.add_argument("-b", "--background-path", default=Path.home())
    args = parser.parse_args()
    if not args.no_toggle:
        toggle()
    if color_scheme == "dark":
        go_dark(args.background_path)
    else:
        go_light(args.background_path)
