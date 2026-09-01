# Carrega/salva as configurações informadas (IDs, path, etc) em um JSON na pasta do usuário

import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".huskynext"
CONFIG_FILE = CONFIG_DIR / "config.json"

# Carrega a config, caso não haja ou esteja corrompida, carrega None
def load_config() -> dict | None:
    if not CONFIG_FILE.exists():
        return None
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None

# Salva a config do teclado identificado
def save_config(vendor_id: int, product_id: int, interface_number: int, usage_page: int | None) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    data = {
        "vendor_id": vendor_id,
        "product_id": product_id,
        "interface_number": interface_number,
        "usage_page": usage_page,
    }
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# Limpa a config para caso seja necessário reconfigurar
def clear_config() -> None:
    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()
