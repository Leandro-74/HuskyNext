"""
Modulo responsavel por carregar e salvar a configuracao no arquivo
JSON na pasta do usuario: tanto a identificacao do teclado (VID, PID,
interface, usage_page) quanto o ultimo estado de iluminacao enviado
(modo e cor), para que nada se perca ao fechar e reabrir o programa.
"""

import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".huskynext"
CONFIG_FILE = CONFIG_DIR / "config.json"


def _read() -> dict:
    """Le o arquivo de config bruto. Devolve {} se nao existir ou estiver corrompido."""
    if not CONFIG_FILE.exists():
        return {}
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _write(data: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_config() -> dict | None:
    """Carrega toda a configuracao salva (dispositivo + estado), ou None se vazia."""
    data = _read()
    return data if data else None


def save_device(vendor_id: int, product_id: int, interface_number: int, usage_page: int | None) -> None:
    """Salva a identificacao do teclado, preservando o estado (cor/modo) ja salvo."""
    data = _read()
    data.update({
        "vendor_id": vendor_id,
        "product_id": product_id,
        "interface_number": interface_number,
        "usage_page": usage_page,
    })
    _write(data)


def save_state(effect: int, bright: int, r: int, g: int, b: int) -> None:
    """Salva o ultimo modo/cor enviados, preservando a identificacao do dispositivo."""
    data = _read()
    data.update({"effect": effect, "bright": bright, "r": r, "g": g, "b": b})
    _write(data)


def clear_device() -> None:
    """Remove so os dados de identificacao do teclado, mantendo o ultimo estado salvo."""
    data = _read()
    for key in ("vendor_id", "product_id", "interface_number", "usage_page"):
        data.pop(key, None)
    if data:
        _write(data)
    elif CONFIG_FILE.exists():
        CONFIG_FILE.unlink()


def clear_config() -> None:
    """Remove toda a configuracao salva (dispositivo e estado)."""
    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()
