import shutil

LARGURA = 56
ESC = "\x1b"

def _pad_horizontal() -> int:
    try:
        cols = shutil.get_terminal_size().columns
    except Exception:
        cols = LARGURA + 2
    return max(0, (cols - (LARGURA+2)) // 2)

def _pad_vertical(total_linhas: int) -> int:
    try:
        rows = shutil.get_terminal_size().lines
    except Exception:
        return 0
    return max(0, (rows - total_linhas) // 2)

def _linha(texto: str = "") -> str:
    return "║" + (" " + texto).ljust(LARGURA) + "║"

def _topo() -> str:
    return "╔" + "═" * LARGURA + "╗"

def _sep() -> str:
    return "╠" + "═" * LARGURA + "╣"

def _fundo() -> str:
    return "╚" + "═" * LARGURA + "╝"

def menu_principal() -> list:
    return [
        "HuskyNext - Husky Sled",
        _sep(),
        "1. Definir cor",
        "2. Definir modo de iluminação",
        "3. Definir Brilho",
        "4. Reconfigurar conexão (VID/PID)",
        "5. Pywal",
        "6. Sair",
    ]

def menu_cores() -> list:
    return [
        "HuskyNext - Definir cor",
        _sep(),
        "Para definir a cor, envie o código HEX da",
        "cor desejada. O código deve seguir o padrão",
        "#FFFFFF ou FFFFFF."
    ]

def menu_brilho() -> list:
    return[
        "HuskyNext - Definir Brilho",
        _sep(),
        "1. 0%",
        "2. 25%",
        "3. 50%",
        "4. 75%",
        "5. 100%",
    ]

def menu_pywal(enabled: bool, target: str) -> list:
    status = "ativada" if enabled else "desativada"
    return [
        "HuskyNext - Pywal",
        _sep(),
        f"Sincronização: {status}",
        f"Cor usada: {target}",
        _sep(),
        "Sincroniza"
        "Escolha uma cor da paleta do pywal.",
        "Opcoes: foreground, background, cursor",
        "ou color0, color1, ..., color15.",
        "Exemplo: color5",
    ]

def menu_pywal_target() -> list:
    return [
        "HuskyNext - Cor do Pywal",
        _sep(),
        "Escolha qual cor usar da paleta.",
        "",
        "auto       - escolhe automaticamente",
        "foreground - cor principal clara",
        "background - cor de fundo",
        "cursor     - cor do cursor",
        "color0..color15 - cores da paleta",
    ]
def menu_modos(EFFECTS: list) -> list:
    linhas = []
    total = len(EFFECTS)
    meio = (total + 1) // 2

    for i in range(meio):
        nome1, _ = EFFECTS[i]
        col1 = f"{i + 1}. {nome1}".ljust(24)

        if i + meio < total:
            nome2, _ = EFFECTS[i + meio]
            col2 = f"{i + 1 + meio}. {nome2}"
            linhas.append(f"{col1}{col2}")
        else:
            linhas.append(col1)
    return [
        "HuskyNext - Definir modo de iluminação",
        _sep(),
        *linhas,
    ]

def abrir_caixa(linhas: list, prompt: str) -> None:
    pad = _pad_horizontal()
    total = len(linhas) + 4
    print("\n" * _pad_vertical(total), end="")

    def out(s: str) -> None:
        print(" " * pad + s)

    out(_topo())
    for l in linhas:
        out(l if l.startswith("╠") else _linha(l))
    out(_sep())
    texto = " " + prompt
    out("║" + texto + " " * max(1, LARGURA - len(texto)) + "║")
    out(_fundo())
    col = pad + 2 + len(texto)
    print(f"{ESC}[2A{ESC}[{col}G", end="", flush=True)

def fechar_caixa() -> None:
    print(f"{ESC}[1B", end="", flush=True)

def perguntar(linhas: list, prompt: str) -> str:
    abrir_caixa(linhas, prompt)
    valor = input()
    fechar_caixa()
    return valor.strip()