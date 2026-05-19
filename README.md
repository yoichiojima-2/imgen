# imgen

A small CLI for generating images with Google's Gemini (`gemini-3.1-flash-image-preview`, a.k.a. "nano-banana").

## Install

```sh
uv sync
# or, as a global tool:
uv build && pipx install dist/*.whl
```

## Auth

```sh
export GEMINI_API_KEY=...
```

## Usage

```sh
# basic
imgen generate "a calm pebble on wet sand at dusk"

# explicit output
imgen generate "..." -o pebble.png

# batch of 4
imgen generate "..." -n 4 -o pebble.png   # -> pebble-1.png ... pebble-4.png

# edit an image
imgen edit pebble.png "add a small bird in the corner" -o pebble-bird.png
```

Outputs without `-o` land in `./output/` with a timestamped name.

## Why Gemini?

Nano-banana is excellent at rendering text (including CJK), structured diagrams, and following layout instructions — the cases where most image models still fall apart.
