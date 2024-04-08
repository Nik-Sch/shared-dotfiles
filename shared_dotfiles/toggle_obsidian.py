import subprocess
from shared_dotfiles.toggle_app import toggle_app


def check_is_running() -> bool:
    return (
        len(
            subprocess.run(
                ["ps", "ux"],
                check=True,  # pidof returns error when no pid found
                capture_output=True,
                text=True,
            )
            .stdout.strip()
            .split()
        )
        > 0
    )


def run():
    OBSIDIAN_BINARY = "obsidian"
    OBSIDIAN_CLASS = "obsidian"

    toggle_app(OBSIDIAN_BINARY, OBSIDIAN_CLASS, check_is_running)
