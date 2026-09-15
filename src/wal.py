import json
import os
from pathlib import Path

VALID_SPECIAL = ("foreground", "background", "cursor")
VALID_COLORS = tuple(f"color{i}" for i in range(16))

def default_colors_path() -> Path:
    env = os.getenv("HUSKYNEXT_WAL_COLORS")
    if env:
        return Path(env).expanduser()

    return Path.home() / ".cache" / "wal" / "colors.json"


def load_palette(path: str | Path | None = None) -> dict:
    p = Path(path).expanduser() if path else default_colors_path()

    if not p.exists():
        raise FileNotFoundError(
            f"Arquivo do pywal nao encontrado: {p}\n"
            "Gere a paleta com 'wal -i imagem.jpg' "
            "ou defina a variavel HUSKYNEXT_WAL_COLORS."
        )

    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON invalido em {p}: {e}") from e

    if "special" not in data or "colors" not in data:
        raise ValueError(
            f"Formato inesperado em {p}. "
            "O arquivo parece nao ser um colors.json do pywal."
        )

    return data


def get_hex_color(palette: dict, target: str) -> str:
    target = target.strip().lower()

    if target in ("fg", "foreground"):
        return palette["special"]["foreground"]

    if target in ("bg", "background"):
        return palette["special"]["background"]

    if target == "cursor":
        return palette["special"]["cursor"]

    if target in VALID_COLORS:
        return palette["colors"][target]

    valid = ", ".join(
        [
            "fg",
            "foreground",
            "bg",
            "background",
            "cursor",
            "color0..color15",
        ]
    )

    raise ValueError(f"Cor do pywal invalida: '{target}'. Use: {valid}")