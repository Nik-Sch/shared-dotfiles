from shared_dotfiles.toggle_app import toggle_app, window_exists

OBSIDIAN_BINARY = "obsidian"
OBSIDIAN_CLASS = "obsidian"


def check_is_running() -> bool:
    return window_exists(OBSIDIAN_CLASS)


def run():

    toggle_app(OBSIDIAN_BINARY, OBSIDIAN_CLASS, check_is_running)
