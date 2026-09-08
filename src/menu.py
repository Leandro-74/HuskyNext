LARGURA = 55
ESC = "\x1b"

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
        "5. Sair",

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
    print(_topo())
    for l in linhas:
        print(l if l.startswith("╠") else _linha(l))
    print(_sep())
    texto = " " + prompt
    print("║" + texto + " " * max(1, LARGURA - len(texto)) + "║")
    print(_fundo())
    col = 2 + len(texto)
    print(f"{ESC}[2A{ESC}[{col}G", end="", flush=True)

def fechar_caixa() -> None:
    print(f"{ESC}[1B", end="", flush=True)

def perguntar(linhas: list, prompt: str) -> str:
    abrir_caixa(linhas, prompt)
    valor = input()
    fechar_caixa()
    return valor.strip()