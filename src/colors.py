"""
Construcao de relatorios HID de cor/efeito, a partir do relatorio
original capturado via Wireshark/USBPcap para o teclado Husky Sled.
"""

import re
from dataclasses import dataclass

REPORT_ID = 0x04

# Relatorio original capturado (64 bytes, incluindo o Report ID no
# primeiro byte).
BASE_REPORT = bytearray([
    0x04, 0xa1, 0x01, 0x06, 0x38, 0x00, 0x00, 0x55,
    0x00, 0x06, 0x04, 0x01, 0x00, 0x00, 0xFF, 0xFF,
    0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
])

MODE_OFFSET = 9
BRIGHT_OFFSET = 10
COLOR_OFFSET_R = 14
COLOR_OFFSET_G = 15
COLOR_OFFSET_B = 16

# Mapeamento modo -> codigo hex enviado ao teclado (byte MODE_OFFSET).
# Confirmados por captura real: Estatico (0x06) e Gota de Chuva (0x08).
# Os demais seguem o padrao observado nesses dois (0x00-0x09 sequencial,
# depois 0x0A-0x0F, depois 0x10-0x12) e ainda precisam ser validados
# um a um contra capturas reais no Wireshark.
EFFECTS = [
    ("Desligado", 0x00),
    ("Onda", 0x01),
    ("Persianas", 0x02),
    ("Difusão", 0x03),
    ("Néon", 0x04),
    ("Respiração", 0x05),
    ("Estático", 0x06),
    ("Reativo", 0x07),
    ("Gota de Chuva", 0x08),
    ("Reativa por Linha", 0x09),
    ("Escaneamento", 0x10),
    ("Single Off", 0x11),
    ("Fluxo", 0x12),
    ("Iluminado por Estrelas", 0x0A),
    ("Flores em Flor", 0x0B),
    ("Cascata", 0x0C),
    ("Arco-íris", 0x0D),
    ("Desenho Animado", 0x0E),
    ("Cena de Chuva", 0x0F),
]

# Guarda os dados enviados para evitar perder um ao alterar o outro
@dataclass
class KeyboardState:
    effect: int = 0x06
    bright: int = 0x04
    r: int = 0xFF
    g: int = 0xFF
    b: int = 0xFF

# Converte a string contendo o código HEX em (r, g, b)
def parse_hex_color(hex_str: str) -> tuple[int, int, int]:
    hex_str = hex_str.strip().lstrip("#")
    if not re.fullmatch(r"[0-9a-fA-F]{6}", hex_str):
        raise ValueError(f"Cor invalida: '{hex_str}'. Use o formato RRGGBB, ex: FF5733")
    r = int(hex_str[0:2], 16)
    g = int(hex_str[2:4], 16)
    b = int(hex_str[4:6], 16)
    return r, g, b

# Monta o relatório com os dados da KeyboardState
def build_report(state: KeyboardState) -> bytes:
    data = bytearray(BASE_REPORT)
    data[MODE_OFFSET] = state.effect
    data[BRIGHT_OFFSET] = state.bright
    data[COLOR_OFFSET_R] = state.r
    data[COLOR_OFFSET_G] = state.g
    data[COLOR_OFFSET_B] = state.b

    return bytes(data)

# Retorna o relatório original capturado (para fins de teste)
def original_report() -> bytes:
    return bytes(BASE_REPORT)
