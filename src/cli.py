# Interface de Linha de Comando (CLI)

from . import config
from . import device
from . import colors
from . import setup_wizard
import time
import os

MENU = """
=== HuskyNext - Controle de RGB para teclados Husky ===

1. Definir cor (HEX)
2. Escolher modo de iluminação
3. Brilho
4. Testar cor original (diagnostico)
5. Reconfigurar teclado (VID/PID)
6. Sair

"""

BRIGHTS = """
=== HuskyNext - Controle de Brilho ===

1. 0%
2. 25%
3. 50%
4. 75%
5. 100%

"""

# Monta o texto do menu de modos de iluminação
def _modes_menu_text() -> str:
    linhas = ["", "=== HuskyNext - Modos de Iluminação ===", ""]
    for i, (nome, _codigo) in enumerate(colors.EFFECTS, start=1):
        linhas.append(f"{i}. {nome}")
    linhas.append("")
    return "\n".join(linhas)

# Recupera o último state do device, caso não haja, retorna o padrão
def _load_initial_state(cfg: dict) -> colors.KeyboardState:
    if all(k in cfg for k in ("effect", "r", "g", "b")):
        return colors.KeyboardState(effect=cfg["effect"], r=cfg["r"], g=cfg["g"], b=cfg["b"])
    return colors.KeyboardState()

# Abre o device, monta o report, envia e salva o state atual
def _enviar(cfg: dict, state: colors.KeyboardState, descricao: str) -> None:
    try:
        dev = device.open_by_config(cfg)
    except ConnectionError as e:
        print(e)
        return
    try:
        report = colors.build_report(state)
        n = device.send_report(dev, report)
        print(f"{descricao} - {n} bytes escritos.")
        config.save_state(state.effect, state.r, state.g, state.b)
    finally:
        dev.close()

# Define a cor, envia pro parse e envia para o device
def _acao_definir_cor(cfg: dict, state: colors.KeyboardState) -> None:
    hex_str = input("Digite a cor em HEX (ex: FF5733 ou #00FF88): ").strip()
    try:
        r, g, b = colors.parse_hex_color(hex_str)
    except ValueError as e:
        print(e)
        return
    state.r, state.g, state.b = r, g, b
    _enviar(cfg, state, f"Cor RGB({r}, {g}, {b}) enviada")

# Define o modo de iluminação e envia para o device
def _acao_definir_modo(cfg: dict, state: colors.KeyboardState) -> None:
    print(_modes_menu_text())
    escolha = input("Escolha o modo: ").strip()
    if not escolha.isdigit() or not (1 <= int(escolha) <= len(colors.EFFECTS)):
        print("Opcao invalida.")
        return
    nome, codigo = colors.EFFECTS[int(escolha) - 1]
    state.effect = codigo
    _enviar(cfg, state, f"Modo '{nome}' (0x{codigo:02x}) enviado")

# Define o brilho e envia para o device
def _acao_definir_brilho(cfg: dict, state: colors.KeyboardState) -> None:
    limpar_tela()
    print(BRIGHTS)
    escolha = input("Escolha uma opção: ").strip()
    if not escolha.isdigit() or not (1 <= int(escolha) <= 5):
        print("Opção Inválida.")
        time.sleep(3)
        return
    state.bright = int(escolha) - 1
    _enviar(cfg, state, f"Brilho {escolha} enviado")

# Envia o relatório original (o coletado) para fins de restauração ou teste
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

# Carrega as configurações (ou o Wizard, caso não tenha configuração) e roda o menu
def run() -> None:
    cfg = config.load_config()
    if cfg is None:
        print("Nenhuma configuracao encontrada. Vamos identificar seu teclado.")
        cfg = setup_wizard.run_wizard()

    # Recupera o ultimo modo/cor enviados (persistidos entre execucoes),
    # para nao "resetar" pros valores padrao do template ao reabrir o programa.
    state = _load_initial_state(cfg)

    while True:
        limpar_tela()
        print(MENU)
        escolha = input("Escolha uma opção: ").strip()

        if escolha == "1":
            _acao_definir_cor(cfg, state)
        elif escolha == "2":
            _acao_definir_modo(cfg, state)
        elif escolha == "3":
            _acao_definir_brilho(cfg, state)
        elif escolha == "4":
            _acao_testar_original(cfg)
        elif escolha == "5":
            config.clear_device()
            cfg = setup_wizard.run_wizard()
        elif escolha == "6":
            print("Ate mais!")
            break
        else:
            print("Opcao invalida.")

# Define a função de limpar tela para interface
def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')