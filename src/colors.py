# Construção do relatório com as modificações informadas, usa um
# relatório capturado pelo Wireshark ao alterar a cor pelo software oficial

import re

REPORT_ID = 0x04

# Relatorio original capturado (64 bytes, incluindo o Report ID no
# primeiro byte). Os bytes de cor ficam nas posicoes 14, 15 e 16.
BASE_REPORT = bytearray([
    0x04, 0xa1, 0x01, 0x06, 0x38, 0x00, 0x00, 0x55,
    0x00, 0x06, 0x04, 0x01, 0x00, 0x00, 0x32, 0x88,
    0x49, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
])

# Posições das cores dentro do relatório
COLOR_OFFSET_R = 14
COLOR_OFFSET_G = 15
COLOR_OFFSET_B = 16

# Converte a strinf "FFFFFF" ou "#FFFFFF" em (r. g, b)
def parse_hex_color(hex_str: str) -> tuple[int, int, int]:
    hex_str = hex_str.strip().lstrip("#")
    if not re.fullmatch(r"[0-9a-fA-F]{6}", hex_str):
        raise ValueError(f"Cor invalida: '{hex_str}'. Use o formato RRGGBB, ex: FF5733")
    r = int(hex_str[0:2], 16)
    g = int(hex_str[2:4], 16)
    b = int(hex_str[4:6], 16)
    return r, g, b

# Gera o relatório modificado com as cores informadas
def build_color_report(r: int, g: int, b: int) -> bytes:
    data = bytearray(BASE_REPORT)
    data[COLOR_OFFSET_R] = r
    data[COLOR_OFFSET_G] = g
    data[COLOR_OFFSET_B] = b
    return bytes(data)

# Devolve o relatório original. Para diagnosticar erros
def original_report() -> bytes:
    return bytes(BASE_REPORT)