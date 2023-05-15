#!/bin/env python3
import argparse
import json
import subprocess
from pathlib import Path
from time import sleep


def set_bg(name: str):
    subprocess.call(
        [
            "feh",
            "--no-fehbg",
            "--bg-fill",
            "--no-xinerama",
            name,
        ]
    )


def set_theme(name: str):
    # subprocess.call(
    #     ["xfconf-query", "-c", "xsettings", "-np", "/Net/ThemeName", "-s", name]
    # )
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


def go_dark():
    # set_theme("Adwaita-dark")
    set_color("prefer-dark")
    set_vscode("Atom One Dark")
    set_bg(f"{Path.home()}/configGit/falcon.jpg")
    set_kitty("Atom")


def go_light():
    # set_theme("Adwaita")
    set_color("prefer-light")
    set_vscode("Atom One Light")
    set_bg(f"{Path.home()}/configGit/light.jpg")
    set_kitty("Atom One Light")


def toggle():
    global MODE
    if MODE == "dark":
        MODE = "light"
    else:
        MODE = "dark"


MODE = "dark"

try:
    text = subprocess.check_output(
        ["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"],
        encoding="utf8",
    )

    if "prefer-light" in text:
        MODE = "light"
except Exception as e:
    print(e)
    print("Error during settings read -> default dark")
print(f"Detected {MODE} mode")
parser = argparse.ArgumentParser(
    prog="go mode",
    description="Sets/Toggles light dark mode",
)
parser.add_argument('-n', '--no-toggle', action='store_true');
args = parser.parse_args();
if not args.no_toggle:
    toggle()
if MODE == "dark":
    go_dark()
else:
    go_light()
