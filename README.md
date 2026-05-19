# imgen

A small CLI for generating images with OpenAI (`gpt-image-1`) or Google (Gemini "nano-banana") — currently the two most capable image models (top of LM Arena, May 2026).

## Install

```sh
uv sync
# or, as a global tool:
uv build && pipx install dist/*.whl
```

## Auth

```sh
export OPENAI_API_KEY=sk-...     # for --backend openai (default)
export GEMINI_API_KEY=...        # for --backend gemini
```

## Usage

```sh
# basic
imgen generate "a calm pebble on wet sand at dusk"

# explicit output, larger size
imgen generate "..." -o pebble.png --size 1536x1024

# batch of 4
imgen generate "..." -n 4 -o pebble.png   # -> pebble-1.png ... pebble-4.png

# higher quality
imgen generate "..." --quality high

# edit an image
imgen edit pebble.png "add a small bird in the corner" -o pebble-bird.png

# masked edit
imgen edit pebble.png "replace sky with aurora" --mask mask.png

# use gemini (nano-banana) — better for text-heavy / diagram-style images
imgen generate "a workflow diagram with japanese labels" --backend gemini
imgen edit diagram.png "make the result badge red" --backend gemini
```

Outputs without `-o` land in `./output/` with a timestamped name.

OpenAI sizes: `1024x1024`, `1024x1536`, `1536x1024`, `auto`. `--size` / `--quality` / `--mask` are OpenAI-only.

## Backends

- **`openai`** (default, `gpt-image-1`): strongest general-purpose quality, weaker at rendering exact text.
- **`gemini`** (`gemini-3.1-flash-image-preview`, a.k.a. nano-banana): far better at rendering text (including CJK), structured diagrams, and following layout instructions.
