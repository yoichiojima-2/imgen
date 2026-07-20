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

(Or pass `--api-key` per invocation.)

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

# pick aspect ratio, resolution, and thinking level
imgen generate "tokyo skyline at night" --aspect 16:9 --size 2K
imgen generate "diagram of a binary tree" --thinking high --aspect 4:3
```

Supported `--aspect`: `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9`, `1:4`, `4:1`, `1:8`, `8:1`.
Supported `--size`: `512`, `1K` (default), `2K`, `4K`.
Supported `--thinking`: `minimal`, `high`.

Outputs without `-o` land in `./output/` with a timestamped name.

## Why Gemini?

Nano-banana is excellent at rendering text (including CJK), structured diagrams, and following layout instructions — the cases where most image models still fall apart.
