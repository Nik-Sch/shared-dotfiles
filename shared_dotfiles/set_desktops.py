import argparse
from itertools import batched
from subprocess import call, check_call, check_output
from typing import cast

from shared_dotfiles.detect_display import get_displays


def run():
    parser = argparse.ArgumentParser(
        prog=f"set_desktops",
        description="distributes desktops across monitors",
    )
    parser.add_argument("desktops", nargs="+")
    args = parser.parse_args()
    displays, _ = get_displays()
    desktops = cast(list[str], args.desktops)
    existing_desktops = sorted(
        check_output(["bspc", "query", "-D", "--names"]).decode("utf-8").splitlines()
    )
    for desktops, display in zip(
        batched(desktops, len(desktops) // len(displays)), displays, strict=True
    ):
        monitor_name = display.name
        for desktop in desktops:
            if desktop in existing_desktops:
                call(
                    [
                        "bspc",
                        "desktop",
                        desktop,
                        "-m",
                        monitor_name,
                    ]
                )
            else:
                check_call(["bspc", "monitor", monitor_name, "-a", desktop])
