import subprocess
from shared_dotfiles.toggle_app import toggle_app

OBSIDIAN_BINARY = "obsidian"
OBSIDIAN_CLASS = "obsidian"


def check_is_running() -> bool:
    try:
        subprocess.run(
            ["xdotool", "search", "--class", OBSIDIAN_CLASS],
            check=True,
            capture_output=True,
            text=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def run():

    toggle_app(OBSIDIAN_BINARY, OBSIDIAN_CLASS, check_is_running)
