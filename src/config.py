"""
Modulo responsavel por carregar e salvar a configuracao do teclado
(vendor_id, product_id, interface_number, usage_page) em um arquivo
JSON na pasta do usuario, para que a identificacao nao precise ser
refeita a cada execucao do programa.
"""

import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".huskynext"
CONFIG_FILE = CONFIG_DIR / "config.json"


def load_config() -> dict | None:
    """Carrega a configuracao salva, ou None se ainda nao existir/estiver corrompida."""
    if not CONFIG_FILE.exists():
        return None
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def save_config(vendor_id: int, product_id: int, interface_number: int, usage_page: int | None) -> None:
    """Salva a configuracao do teclado identificado."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    data = {
        "vendor_id": vendor_id,
        "product_id": product_id,
        "interface_number": interface_number,
        "usage_page": usage_page,
    }
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def clear_config() -> None:
    """Remove a configuracao salva (usado ao reconfigurar)."""
    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()
