import os
import subprocess
from typing import Literal


def get_gsettings_color_scheme() -> Literal["light", "dark"]:
    try:
        text = subprocess.check_output(
            ["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"],
            encoding="utf8",
        )

        if "prefer-light" in text:
            return "light"
    except Exception as e:
        print(e)
        print("Error during settings read -> default dark")
    return "dark"


def is_hyprland() -> bool:
    return bool(os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")) and bool(
        os.environ.get("WAYLAND_DISPLAY")
    )
