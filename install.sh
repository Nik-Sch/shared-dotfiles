#!/bin/bash
set -e
uv build
uv tool install dist/shared_dotfiles-*.whl --force