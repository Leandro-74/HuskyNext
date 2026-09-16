import json
import os
import colorsys
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

import colorsys


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    c = hex_color.strip().lstrip("#")

    if len(c) != 6:
        raise ValueError(f"Cor HEX invalida: {hex_color}")

    try:
        r = int(c[0:2], 16)
        g = int(c[2:4], 16)
        b = int(c[4:6], 16)
    except ValueError as e:
        raise ValueError(f"Cor HEX invalida: {hex_color}") from e

    return r, g, b


def choose_auto(palette: dict) -> tuple[str, str]:
    colors_map = palette.get("colors", {})
    special = palette.get("special", {})

    background_hex = special.get("background")
    background_rgb = None

    if background_hex:
        try:
            background_rgb = _hex_to_rgb(background_hex)
        except ValueError:
            background_rgb = None

    best_key = None
    best_hex = None
    best_score = -1.0

    for key, hex_color in colors_map.items():
        try:
            r, g, b = _hex_to_rgb(hex_color)
        except ValueError:
            continue

        _, saturation, value = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)

        score = saturation * value

        if value < 0.15:
            score *= 0.15

        if saturation < 0.20:
            score *= 0.35

        if background_rgb is not None:
            br, bg, bb = background_rgb
            distance = ((r - br) ** 2 + (g - bg) ** 2 + (b - bb) ** 2) ** 0.5

            if distance < 70:
                score *= 0.20

        if key in ("color3", "color4", "color5", "color6"):
            score *= 1.05

        if score > best_score:
            best_score = score
            best_key = key
            best_hex = hex_color

    if best_hex is None:
        foreground = special.get("foreground")

        if foreground:
            return "foreground", foreground

        raise ValueError("Nenhuma cor valida encontrada na paleta.")

    return best_key, best_hex


def resolve_target(palette: dict, target: str) -> tuple[str, str]:
    target = (target or "auto").strip().lower()

    if target == "auto":
        return choose_auto(palette)

    return target, get_hex_color(palette, target)