import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".huskynext"
CONFIG_FILE = CONFIG_DIR / "config.json"


def _read() -> dict:
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
    data = _read()
    return data if data else None


def save_device(vendor_id: int, product_id: int, interface_number: int, usage_page: int | None) -> None:
    data = _read()
    data.update({
        "vendor_id": vendor_id,
        "product_id": product_id,
        "interface_number": interface_number,
        "usage_page": usage_page,
    })
    _write(data)


def save_state(effect: int, bright: int, r: int, g: int, b: int) -> None:
    data = _read()
    data.update({"effect": effect, "bright": bright, "r": r, "g": g, "b": b})
    _write(data)


def clear_device() -> None:
    data = _read()
    for key in ("vendor_id", "product_id", "interface_number", "usage_page"):
        data.pop(key, None)
    if data:
        _write(data)
    elif CONFIG_FILE.exists():
        CONFIG_FILE.unlink()

def get_wal_settings() -> dict:
    data = _read()

    return {
        "enabled": bool(data.get("wal_enabled", False)),
        "target": str(data.get("wal_target", "auto")),
        "poll_seconds": float(data.get("wal_poll_seconds", 2.0)),
    }

def set_wal_settings(
    enabled: bool | None = None,
    target: str | None = None,
    poll_seconds: float | None = None,
) -> None:
    data = _read()

    if enabled is not None:
        data["wal_enabled"] = bool(enabled)

    if target is not None:
        data["wal_target"] = target
    
    if poll_seconds is not None:
        data["wal_poll_seconds"] = float(poll_seconds)

    _write(data)

def get_calibration() -> dict:
    data = _read()

    return data.get("calibration", {})

def save_calibration(calibration: dict) -> None:
    data = _read()
    data["calibration"] = calibration
    _write(data)

def clear_config() -> None:
    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()