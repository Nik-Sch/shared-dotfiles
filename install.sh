#!/bin/bash
rm -rf dist
poetry install
poetry build
pipx install ./dist/shared_dotfiles-*.tar.gz --force
