from shared_dotfiles.toggle_app import toggle_app


def run():
    CALCULATOR_BINARY = "qalculate-qt"
    CALCULATOR_CLASS = "qalculate-qt"

    toggle_app(CALCULATOR_BINARY, CALCULATOR_CLASS)
