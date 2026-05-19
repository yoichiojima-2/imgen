from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from . import client
from .io import resolve_output_paths, write_png

ENV_KEY = "GEMINI_API_KEY"

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
    api_key: Optional[str] = typer.Option(None, "--api-key"),
) -> None:
    """Generate one or more images from a text prompt."""
    key = _check_key(api_key)
    paths = resolve_output_paths(output, count, prompt)
    with console.status(f"generating {count} image(s) with {model}…"):
        try:
            images = client.generate(prompt, model=model, n=count, api_key=key)
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
    api_key: Optional[str] = typer.Option(None, "--api-key"),
) -> None:
    """Edit an existing image with a text prompt."""
    key = _check_key(api_key)
    paths = resolve_output_paths(output, count, f"edit-{input_path.stem}-{prompt}")
    with console.status(f"editing image with {model}…"):
        try:
            images = client.edit(input_path, prompt, model=model, n=count, api_key=key)
        except Exception as e:  # noqa: BLE001
            console.print(f"[red]error:[/red] {e}")
            raise typer.Exit(code=1)
    _save(images, paths)


if __name__ == "__main__":
    app()
