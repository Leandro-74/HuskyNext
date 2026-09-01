# Interface de linha de comando (CLI) e encaminhamento de funções para uso do HuskyNext

from . import config
from . import device
from . import colors
from . import setup_wizard

MENU = """
=== HuskyNext - Controle de RGB para teclados Husky ===

1. Definir cor (HEX)
2. Testar cor original (diagnostico)
3. Reconfigurar teclado (VID/PID)
4. Sair
"""


# Define a cor que será enviada ao device
def _acao_definir_cor(cfg: dict) -> None:
    hex_str = input("Digite a cor em HEX (ex: FF5733 ou #00FF88): ").strip()
    try:
        r, g, b = colors.parse_hex_color(hex_str)
    except ValueError as e:
        print(e)
        return

    try:
        dev = device.open_by_config(cfg)
    except ConnectionError as e:
        print(e)
        return

    try:
        report = colors.build_color_report(r, g, b)
        n = device.send_report(dev, report)
        print(f"Cor RGB({r}, {g}, {b}) enviada - {n} bytes escritos.")
    finally:
        dev.close()

# Testa o envio do relatório original
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

# Setup da ferramenta, em caso de primeira execução, roda o Setup Wizard para identificar o device
def run() -> None:
    cfg = config.load_config()
    if cfg is None:
        print("Nenhuma configuracao encontrada. Vamos identificar seu teclado.")
        cfg = setup_wizard.run_wizard()

    while True:
        print(MENU)
        escolha = input("Escolha uma opcao: ").strip()

        if escolha == "1":
            _acao_definir_cor(cfg)
        elif escolha == "2":
            _acao_testar_original(cfg)
        elif escolha == "3":
            config.clear_config()
            cfg = setup_wizard.run_wizard()
        elif escolha == "4":
            print("Ate mais!")
            break
        else:
            print("Opcao invalida.")
