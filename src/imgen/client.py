from __future__ import annotations

import base64
from pathlib import Path

from openai import OpenAI


def _decode(items) -> list[bytes]:
    return [base64.b64decode(item.b64_json) for item in items]


def generate(
    prompt: str,
    *,
    model: str,
    size: str,
    n: int,
    quality: str,
    api_key: str | None = None,
) -> list[bytes]:
    client = OpenAI(api_key=api_key) if api_key else OpenAI()
    resp = client.images.generate(
        model=model,
        prompt=prompt,
        size=size,
        n=n,
        quality=quality,
    )
    return _decode(resp.data)


def edit(
    image_path: Path,
    prompt: str,
    *,
    model: str,
    size: str,
    n: int,
    mask_path: Path | None = None,
    api_key: str | None = None,
) -> list[bytes]:
    client = OpenAI(api_key=api_key) if api_key else OpenAI()
    with open(image_path, "rb") as image_file:
        kwargs = dict(
            model=model,
            image=image_file,
            prompt=prompt,
            size=size,
            n=n,
        )
        if mask_path is not None:
            with open(mask_path, "rb") as mask_file:
                kwargs["mask"] = mask_file
                resp = client.images.edit(**kwargs)
        else:
            resp = client.images.edit(**kwargs)
    return _decode(resp.data)
