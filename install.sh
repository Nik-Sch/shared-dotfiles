#!/bin/bash
rm -rf dist
poetry install
poetry build
pipx install -f ./dist/shared_dotfiles-*.tar.gz