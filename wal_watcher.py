import hashlib
import sys
import time
import traceback
from pathlib import Path

from src import config
from src import wal
from src import colors
from src import device
from src import colorfx


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_state(cfg: dict, r: int, g: int, b: int) -> colors.KeyboardState:
    base = colors.KeyboardState()

    effect = cfg.get("effect", base.effect)
    bright = cfg.get("bright", base.bright)

    return colors.KeyboardState(
        effect=effect,
        bright=bright,
        r=r,
        g=g,
        b=b,
    )


def apply_palette(cfg: dict, palette: dict, target: str) -> None:
    key, hex_color = wal.resolve_target(palette, target)

    r, g, b = colors.parse_hex_color(hex_color)

    calibration = config.get_calibration()
    cr, cg, cb = colorfx.apply_calibration(r, g, b, calibration)

    state = build_state(cfg, cr, cg, cb)

    dev = device.open_by_config(cfg)

    try:
        report = colors.build_report(state)
        device.send_report(dev, report)

        # Salva a cor original da paleta, não a cor calibrada
        config.save_state(state.effect, state.bright, r, g, b)

        print(f"Pywal aplicado: {key} = {hex_color}")

    finally:
        dev.close()


def main() -> None:
    last_hash = None
    last_enabled = None
    sleep_time = 2.0

    print("HuskyNext watcher iniciado.")

    while True:
        try:
            settings = config.get_wal_settings()

            enabled = settings["enabled"]
            target = settings["target"]
            sleep_time = settings["poll_seconds"]

            if not enabled:
                if last_enabled:
                    print("Sincronizacao Pywal desativada.")

                last_enabled = False
                last_hash = None
                time.sleep(sleep_time)
                continue

            if last_enabled is False:
                print("Sincronizacao Pywal ativada.")
                last_hash = None

            cfg = config.load_config()

            if cfg is None:
                print("Teclado ainda nao configurado.")
                time.sleep(sleep_time)
                continue

            path = wal.default_colors_path()

            if not path.exists():
                print(f"Arquivo de cores nao encontrado: {path}")
                time.sleep(sleep_time)
                continue

            current_hash = file_hash(path)

            if current_hash != last_hash:
                palette = wal.load_palette(path)
                apply_palette(cfg, palette, target)
                last_hash = current_hash

            last_enabled = True

        except KeyboardInterrupt:
            print("Watcher encerrado.")
            break

        except Exception:
            print("Erro no watcher:", file=sys.stderr)
            traceback.print_exc()

        time.sleep(sleep_time)


if __name__ == "__main__":
    main()