"""
Interface de linha de comando (menu numerado) do HuskyNext.
"""

from . import config
from . import device
from . import colors
from . import setup_wizard

MENU = """
=== HuskyNext - Controle de RGB para teclados Husky ===

1. Definir cor (HEX)
2. Escolher modo de iluminação
3. Testar cor original (diagnostico)
4. Reconfigurar teclado (VID/PID)
5. Sair
"""


def _modes_menu_text() -> str:
    """Monta o texto do menu de modos a partir de colors.EFFECTS,
    para nunca ficar dessincronizado dos codigos reais."""
    linhas = ["", "=== HuskyNext - Modos de Iluminação ===", ""]
    for i, (nome, _codigo) in enumerate(colors.EFFECTS, start=1):
        linhas.append(f"{i}. {nome}")
    linhas.append("")
    return "\n".join(linhas)


def _enviar(cfg: dict, state: colors.KeyboardState, descricao: str) -> None:
    """Abre o teclado, monta o relatorio a partir do state atual e envia."""
    try:
        dev = device.open_by_config(cfg)
    except ConnectionError as e:
        print(e)
        return
    try:
        report = colors.build_report(state)
        n = device.send_report(dev, report)
        print(f"{descricao} - {n} bytes escritos.")
    finally:
        dev.close()


def _acao_definir_cor(cfg: dict, state: colors.KeyboardState) -> None:
    hex_str = input("Digite a cor em HEX (ex: FF5733 ou #00FF88): ").strip()
    try:
        r, g, b = colors.parse_hex_color(hex_str)
    except ValueError as e:
        print(e)
        return
    state.r, state.g, state.b = r, g, b
    _enviar(cfg, state, f"Cor RGB({r}, {g}, {b}) enviada")


def _acao_definir_modo(cfg: dict, state: colors.KeyboardState) -> None:
    print(_modes_menu_text())
    escolha = input("Escolha o modo: ").strip()
    if not escolha.isdigit() or not (1 <= int(escolha) <= len(colors.EFFECTS)):
        print("Opcao invalida.")
        return
    nome, codigo = colors.EFFECTS[int(escolha) - 1]
    state.effect = codigo
    _enviar(cfg, state, f"Modo '{nome}' (0x{codigo:02x}) enviado")


def _acao_testar_original(cfg: dict) -> None:
    try:
        dev = device.open_by_config(cfg)
    except ConnectionError as e:
        print(e)
        return
    try:
        n = device.send_report(dev, colors.original_report())
        print(f"Relatorio original reenviado - {n} bytes escritos.")
    finally:
        dev.close()


def run() -> None:
    cfg = config.load_config()
    if cfg is None:
        print("Nenhuma configuracao encontrada. Vamos identificar seu teclado.")
        cfg = setup_wizard.run_wizard()

    # Guarda o ultimo modo/cor enviados nesta sessao, para que alterar um
    # nao "resete" o outro para os valores padrao do template.
    state = colors.KeyboardState()

    while True:
        print(MENU)
        escolha = input("Escolha uma opcao: ").strip()

        if escolha == "1":
            _acao_definir_cor(cfg, state)
        elif escolha == "2":
            _acao_definir_modo(cfg, state)
        elif escolha == "3":
            _acao_testar_original(cfg)
        elif escolha == "4":
            config.clear_config()
            cfg = setup_wizard.run_wizard()
        elif escolha == "5":
            print("Ate mais!")
            break
        else:
            print("Opcao invalida.")
