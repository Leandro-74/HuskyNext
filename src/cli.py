from . import config
from . import device
from . import colors
from . import setup_wizard
from . import menu
from . import wal
from . import colorfx
import time
import os

def _load_initial_state(cfg: dict) -> colors.KeyboardState:
    if all(k in cfg for k in ("effect", "bright", "r", "g", "b")):
        return colors.KeyboardState(
            effect=cfg["effect"], bright=cfg["bright"],
            r=cfg["r"], g=cfg["g"], b=cfg["b"]
            )
    return colors.KeyboardState()

def _enviar(cfg: dict, state: colors.KeyboardState, descricao: str) -> None:
    try:
        dev = device.open_by_config(cfg)
    except ConnectionError as e:
        print(e)
        return

    try:
        calibration = config.get_calibration()

        cr, cg, cb = colorfx.apply_calibration(
            state.r,
            state.g,
            state.b,
            calibration,
        )

        corrected_state = colors.KeyboardState(
            effect=state.effect,
            bright=state.bright,
            r=cr,
            g=cg,
            b=cb,
        )

        report = colors.build_report(corrected_state)
        n = device.send_report(dev, report)

        print(
            f"{descricao} - {n} bytes escritos. "
            f"RAW={state.r:02X}{state.g:02X}{state.b:02X} "
            f"OUT={cr:02X}{cg:02X}{cb:02X}"
        )

        config.save_state(
            state.effect,
            state.bright,
            state.r,
            state.g,
            state.b,
        )

    finally:
        dev.close()

def _acao_definir_cor(cfg: dict, state: colors.KeyboardState) -> None:
    limpar_tela()
    hex_str = menu.perguntar(menu.menu_cores(), "Escolha: ")
    try:
        r, g, b = colors.parse_hex_color(hex_str)
    except ValueError as e:
        print(e)
        return
    state.r, state.g, state.b = r, g, b
    _enviar(cfg, state, f"Cor RGB({r}, {g}, {b}) enviada")

def _acao_definir_modo(cfg: dict, state: colors.KeyboardState) -> None:
    limpar_tela()
    escolha = menu.perguntar(menu.menu_modos(colors.EFFECTS), "Escolha: ")
    if not escolha.isdigit() or not (1 <= int(escolha) <= len(colors.EFFECTS)):
        return
    nome, codigo = colors.EFFECTS[int(escolha) - 1]
    state.effect = codigo
    _enviar(cfg, state, f"Modo '{nome}' (0x{codigo:02x}) enviado")

def _acao_pywal(cfg: dict, state: colors.KeyboardState) -> None:
    while True:
        limpar_tela()

        settings = config.get_wal_settings()

        escolha = menu.perguntar(
            menu.menu_pywal(settings["enabled"], settings["target"]),
            "Escolha: "
        )

        if escolha == "1":
            new_enabled = not settings["enabled"]
            config.set_wal_settings(enabled=new_enabled)

            if new_enabled:
                _acao_aplicar_wal(cfg, state, settings["target"])

        elif escolha == "2":
            limpar_tela()

            target = menu.perguntar(
                menu.menu_pywal_target(),
                "Cor: "
            ).strip().lower()

            try:
                palette = wal.load_palette()
                wal.resolve_target(palette, target)
                config.set_wal_settings(target=target)
            except (FileNotFoundError, ValueError) as e:
                print(e)
                time.sleep(4)

        elif escolha == "3":
            _acao_aplicar_wal(cfg, state)

        elif escolha == "4":
            break

        else:
            print("Opcao invalida.")
            time.sleep(2)

def _acao_definir_brilho(cfg: dict, state: colors.KeyboardState) -> None:
    limpar_tela()
    escolha = menu.perguntar(menu.menu_brilho(), "Escolha: ")
    if not escolha.isdigit() or not (1 <= int(escolha) <= 5):
        return
    state.bright = int(escolha) - 1
    _enviar(cfg, state, f"Brilho {escolha} enviado")

def _acao_aplicar_wal(cfg: dict, state: colors.KeyboardState, target: str | None = None) -> bool:
    settings = config.get_wal_settings()

    if target is None:
        target = settings["target"]

    try:
        palette = wal.load_palette()
        key, hex_color = wal.resolve_target(palette, target)
        r, g, b = colors.parse_hex_color(hex_color)
    except (FileNotFoundError, ValueError) as e:
        print(e)
        time.sleep(4)
        return False

    state.r, state.g, state.b = r, g, b
    _enviar(cfg, state, f"Pywal '{key}' aplicado")

    return True

def run() -> None:
    cfg = config.load_config()
    if cfg is None:
        print("Nenhuma configuracao encontrada. Vamos identificar seu teclado.")
        cfg = setup_wizard.run_wizard()
    state = _load_initial_state(cfg)

    while True:
        limpar_tela()
        escolha = (menu.perguntar(menu.menu_principal(), "Escolha: "))

        if escolha == "1":
            _acao_definir_cor(cfg, state)
        elif escolha == "2":
            _acao_definir_modo(cfg, state)
        elif escolha == "3":
            _acao_definir_brilho(cfg, state)
        elif escolha == "4":
            config.clear_device()
            cfg = setup_wizard.run_wizard()
            state = _load_initial_state(cfg)
        elif escolha == "5":
            _acao_pywal(cfg, state)
        elif escolha == "6":
            print(" Ate mais!\n")
            break
        else:
            print("Opcao invalida.")

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')