# Weathervane Desktop e-ink display

A little desktop display to show readings from my [Weathervane API](https://github.com/Chattox/weathervane-ts-api) on the [Waveshare three-colour 2.13" e-ink display HAT](https://thepihut.com/products/three-colour-2-13-eink-display-phat-red-black-white)

## Setup
If running in a virtual environment, will need access to global packages to access built in raspi libraries.

```zsh
python -m venv --system-site-packages ./.venv
cd .venv/bin
source activate
cd ../..
pip install -r requirements.txt
pip install .
```

## Running

For running normally
```zsh
python main.py
```

For running in dev mode (outputs display image to a window instead of updating the display to save time while developing)
```zsh
python main.py dev
```