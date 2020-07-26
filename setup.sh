#!/bin/bash

# create virtualenv to not mess up your machine
virtualenv -q -p python3 env-tetris-ai
source env-tetris-ai/bin/activate
python -m pip install --upgrade pip

# install pygame dependencies
brew install sdl2 sdl2_gfx sdl2_image sdl2_mixer sdl2_net sdl2_ttf

# download, configure and install pygame
git clone -b 1.9.6 https://github.com/pygame/pygame.git .pygame
python .pygame/setup.py -config -auto -sdl2
python .pygame/setup.py install
