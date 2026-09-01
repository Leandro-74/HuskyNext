"""
Comunicacao HID de baixo nivel com o teclado: listar dispositivos,
encontrar a interface/collection certa e enviar relatorios.
"""

import hid

# Faixa de usage_page reservada para uso proprietario dos fabricantes
# (vendor-specific) - forte indicio de controles como iluminacao RGB.
VENDOR_SPECIFIC_USAGE_PAGE_MIN = 0xFF00
VENDOR_SPECIFIC_USAGE_PAGE_MAX = 0xFFFF


def list_all_devices() -> list[dict]:
    """Lista todos os dispositivos HID conectados no computador."""
    return hid.enumerate()


def list_candidate_devices() -> list[dict]:
    """
    Lista dispositivos HID cujo usage_page esta na faixa vendor-specific
    (0xff00-0xffff) - candidatos mais provaveis a controle de iluminacao.
    """
    candidates = []
    for d in hid.enumerate():
        usage_page = d.get("usage_page", 0)
        if VENDOR_SPECIFIC_USAGE_PAGE_MIN <= usage_page <= VENDOR_SPECIFIC_USAGE_PAGE_MAX:
            candidates.append(d)
    return candidates


def find_target_path(vid: int, pid: int, interface_number: int, usage_page: int | None = None) -> bytes | None:
    """Acha o 'path' da interface/collection especifica de um dispositivo HID."""
    candidates = [
        d for d in hid.enumerate(vid, pid)
        if d.get("interface_number") == interface_number
    ]
    if usage_page is not None:
        filtered = [d for d in candidates if d.get("usage_page") == usage_page]
        if filtered:
            candidates = filtered
    if not candidates:
        return None
    return candidates[0]["path"]


def open_by_config(cfg: dict) -> "hid.device":
    """Abre a conexao HID usando uma configuracao ja salva."""
    path = find_target_path(
        cfg["vendor_id"],
        cfg["product_id"],
        cfg["interface_number"],
        cfg.get("usage_page"),
    )
    if path is None:
        raise ConnectionError(
            "Nao foi possivel encontrar o teclado com a configuracao salva. "
            "Ele pode estar desconectado, ou os IDs podem ter mudado. "
            "Use a opcao de reconfigurar no menu."
        )
    return open_by_path(path)


def open_by_path(path: bytes) -> "hid.device":
    """Abre a conexao HID diretamente por um path especifico."""
    dev = hid.device()
    dev.open_path(path)
    return dev


def send_report(dev: "hid.device", report: bytes) -> int:
    """Envia um relatorio HID para o dispositivo ja aberto."""
    return dev.write(report)
