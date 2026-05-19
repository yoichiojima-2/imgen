from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from . import client as openai_api
from . import gemini as gemini_api
from .io import resolve_output_paths, write_png

VALID_SIZES = {"1024x1024", "1024x1536", "1536x1024", "auto"}
BACKENDS = {"openai", "gemini"}
DEFAULT_MODELS = {
    "openai": "gpt-image-1",
    "gemini": gemini_api.DEFAULT_MODEL,
}
ENV_KEYS = {
    "openai": "OPENAI_API_KEY",
    "gemini": "GEMINI_API_KEY",
}

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="Generate images with OpenAI (gpt-image-1) or Google (gemini / nano-banana).",
)
console = Console()


def _check_backend(backend: str) -> None:
    if backend not in BACKENDS:
        console.print(
            f"[red]error:[/red] invalid --backend {backend!r}. "
            f"Valid: {', '.join(sorted(BACKENDS))}"
        )
        raise typer.Exit(code=2)


def _check_key(api_key: Optional[str], backend: str) -> str:
    env = ENV_KEYS[backend]
    key = api_key or os.environ.get(env)
    if not key:
        console.print(f"[red]error:[/red] {env} not set. Export it or pass --api-key.")
        raise typer.Exit(code=2)
    return key


def _check_size(size: str) -> None:
    if size not in VALID_SIZES:
        console.print(
            f"[red]error:[/red] invalid --size {size!r}. "
            f"Valid: {', '.join(sorted(VALID_SIZES))}"
        )
        raise typer.Exit(code=2)


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
    size: str = typer.Option(
        "1024x1024", "--size", help="OpenAI only: 1024x1024 | 1024x1536 | 1536x1024 | auto"
    ),
    count: int = typer.Option(1, "-n", "--count", min=1, max=10),
    quality: str = typer.Option(
        "auto", "--quality", help="OpenAI only: low | medium | high | auto"
    ),
    backend: str = typer.Option("openai", "--backend", help="openai | gemini"),
    model: Optional[str] = typer.Option(None, "--model", help="Override default model."),
    api_key: Optional[str] = typer.Option(None, "--api-key"),
) -> None:
    """Generate one or more images from a text prompt."""
    _check_backend(backend)
    key = _check_key(api_key, backend)
    model = model or DEFAULT_MODELS[backend]
    paths = resolve_output_paths(output, count, prompt)
    with console.status(f"generating {count} image(s) with {backend}/{model}…"):
        try:
            if backend == "openai":
                _check_size(size)
                images = openai_api.generate(
                    prompt, model=model, size=size, n=count, quality=quality, api_key=key
                )
            else:
                images = gemini_api.generate(prompt, model=model, n=count, api_key=key)
        except Exception as e:  # noqa: BLE001
            console.print(f"[red]error:[/red] {e}")
            raise typer.Exit(code=1)
    _save(images, paths)


@app.command()
def edit(
    input_path: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True),
    prompt: str = typer.Argument(..., help="Edit instruction."),
    output: Optional[Path] = typer.Option(None, "-o", "--output"),
    mask: Optional[Path] = typer.Option(
        None, "--mask", exists=True, dir_okay=False, readable=True,
        help="OpenAI only: mask image for inpainting.",
    ),
    size: str = typer.Option("1024x1024", "--size", help="OpenAI only."),
    count: int = typer.Option(1, "-n", "--count", min=1, max=10),
    backend: str = typer.Option("openai", "--backend", help="openai | gemini"),
    model: Optional[str] = typer.Option(None, "--model"),
    api_key: Optional[str] = typer.Option(None, "--api-key"),
) -> None:
    """Edit an existing image with a text prompt (optionally masked)."""
    _check_backend(backend)
    key = _check_key(api_key, backend)
    model = model or DEFAULT_MODELS[backend]
    paths = resolve_output_paths(output, count, f"edit-{input_path.stem}-{prompt}")
    with console.status(f"editing image with {backend}/{model}…"):
        try:
            if backend == "openai":
                _check_size(size)
                images = openai_api.edit(
                    input_path, prompt, model=model, size=size, n=count,
                    mask_path=mask, api_key=key,
                )
            else:
                if mask is not None:
                    console.print("[yellow]warn:[/yellow] --mask is ignored for gemini backend.")
                images = gemini_api.edit(
                    input_path, prompt, model=model, n=count, api_key=key
                )
        except Exception as e:  # noqa: BLE001
            console.print(f"[red]error:[/red] {e}")
            raise typer.Exit(code=1)
    _save(images, paths)


if __name__ == "__main__":
    app()
