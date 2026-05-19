from __future__ import annotations

import os
from enum import Enum
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from . import client
from .io import resolve_output_paths, write_png

ENV_KEY = "GEMINI_API_KEY"


class Aspect(str, Enum):
    r1_1 = "1:1"
    r2_3 = "2:3"
    r3_2 = "3:2"
    r3_4 = "3:4"
    r4_3 = "4:3"
    r4_5 = "4:5"
    r5_4 = "5:4"
    r9_16 = "9:16"
    r16_9 = "16:9"
    r21_9 = "21:9"
    r1_4 = "1:4"
    r4_1 = "4:1"
    r1_8 = "1:8"
    r8_1 = "8:1"


class Size(str, Enum):
    s512 = "512"
    s1k = "1K"
    s2k = "2K"
    s4k = "4K"


class Thinking(str, Enum):
    minimal = "minimal"
    high = "high"

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="Generate images with Google's Gemini (nano-banana).",
)
console = Console()


def _check_key(api_key: Optional[str]) -> str:
    key = api_key or os.environ.get(ENV_KEY)
    if not key:
        console.print(f"[red]error:[/red] {ENV_KEY} not set. Export it or pass --api-key.")
        raise typer.Exit(code=2)
    return key


def _save(images: list[bytes], paths: list[Path]) -> None:
    for data, path in zip(images, paths):
        write_png(data, path)
        console.print(f"[green]saved[/green] {path}")


@app.command()
def generate(
    prompt: str = typer.Argument(..., help="Text prompt."),
    output: Optional[Path] = typer.Option(
        None, "-o", "--output", help="Output file (or stem for batch)."
    ),
    count: int = typer.Option(1, "-n", "--count", min=1, max=10),
    model: str = typer.Option(client.DEFAULT_MODEL, "--model"),
    aspect: Optional[Aspect] = typer.Option(None, "--aspect", help="Aspect ratio."),
    size: Optional[Size] = typer.Option(None, "--size", help="Output resolution."),
    thinking: Optional[Thinking] = typer.Option(None, "--thinking", help="Thinking level."),
    api_key: Optional[str] = typer.Option(None, "--api-key"),
) -> None:
    """Generate one or more images from a text prompt."""
    key = _check_key(api_key)
    paths = resolve_output_paths(output, count, prompt)
    with console.status(f"generating {count} image(s) with {model}…"):
        try:
            images = client.generate(
                prompt,
                model=model,
                n=count,
                api_key=key,
                aspect_ratio=aspect.value if aspect else None,
                image_size=size.value if size else None,
                thinking=thinking.value if thinking else None,
            )
        except Exception as e:  # noqa: BLE001
            console.print(f"[red]error:[/red] {e}")
            raise typer.Exit(code=1)
    _save(images, paths)


@app.command()
def edit(
    input_path: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True),
    prompt: str = typer.Argument(..., help="Edit instruction."),
    output: Optional[Path] = typer.Option(None, "-o", "--output"),
    count: int = typer.Option(1, "-n", "--count", min=1, max=10),
    model: str = typer.Option(client.DEFAULT_MODEL, "--model"),
    aspect: Optional[Aspect] = typer.Option(None, "--aspect", help="Aspect ratio."),
    size: Optional[Size] = typer.Option(None, "--size", help="Output resolution."),
    thinking: Optional[Thinking] = typer.Option(None, "--thinking", help="Thinking level."),
    api_key: Optional[str] = typer.Option(None, "--api-key"),
) -> None:
    """Edit an existing image with a text prompt."""
    key = _check_key(api_key)
    paths = resolve_output_paths(output, count, f"edit-{input_path.stem}-{prompt}")
    with console.status(f"editing image with {model}…"):
        try:
            images = client.edit(
                input_path,
                prompt,
                model=model,
                n=count,
                api_key=key,
                aspect_ratio=aspect.value if aspect else None,
                image_size=size.value if size else None,
                thinking=thinking.value if thinking else None,
            )
        except Exception as e:  # noqa: BLE001
            console.print(f"[red]error:[/red] {e}")
            raise typer.Exit(code=1)
    _save(images, paths)


if __name__ == "__main__":
    app()
