from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

DEFAULT_OUTPUT_DIR = Path("output")


def slug(prompt: str, max_len: int = 40) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", prompt.lower()).strip("-")
    return (s[:max_len].rstrip("-")) or "image"


def default_stem(prompt: str) -> str:
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"imgen-{slug(prompt)}-{ts}"


def resolve_output_paths(output: Path | None, count: int, prompt: str) -> list[Path]:
    if output is None:
        stem = default_stem(prompt)
        base = DEFAULT_OUTPUT_DIR / f"{stem}.png"
    else:
        base = output
        if base.suffix == "":
            base = base.with_suffix(".png")

    if count == 1:
        return [base]

    return [base.with_name(f"{base.stem}-{i + 1}{base.suffix}") for i in range(count)]


def write_png(data: bytes, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
