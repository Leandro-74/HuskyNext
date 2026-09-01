"""
Assistente de identificacao do teclado: lista candidatos prováveis,
testa uma cor em cada um pedindo confirmacao visual da pessoa, e
salva a configuracao encontrada. Se nada for confirmado, cai para
entrada manual dos IDs.
"""

from . import config
from . import device
from . import colors


def _describe(d: dict) -> str:
    manuf = d.get("manufacturer_string") or "?"
    prod = d.get("product_string") or "?"
    vid = d.get("vendor_id", 0)
    pid = d.get("product_id", 0)
    iface = d.get("interface_number")
    usage_page = d.get("usage_page", 0)
    return f"{manuf} / {prod}  (VID={vid:#06x} PID={pid:#06x} iface={iface} usage_page={usage_page:#06x})"


def _try_candidate(d: dict) -> bool:
    """Abre o candidato, manda uma cor de teste (vermelho) e pede confirmacao."""
    try:
        dev = device.open_by_path(d["path"])
    except OSError as e:
        print(f"  Nao consegui abrir esse dispositivo: {e}")
        return False

    try:
        report = colors.build_color_report(255, 0, 0)
        device.send_report(dev, report)
    finally:
        dev.close()

    resposta = input("  A cor do teclado mudou para vermelho? [s/n]: ").strip().lower()
    return resposta.startswith("s")


def _manual_entry() -> dict:
    """Fallback: pede os IDs do teclado manualmente."""
    print("\nInforme os dados manualmente. No Windows, use o Gerenciador de Dispositivos")
    print("(Propriedades > Detalhes > Hardware Ids). No Linux, use 'lsusb'.")
    vendor_id = int(input("Vendor ID (hex, ex: 0c45): ").strip(), 16)
    product_id = int(input("Product ID (hex, ex: 8501): ").strip(), 16)
    interface_number = int(input("Interface number (ex: 1): ").strip())
    usage_page_str = input("Usage page (hex, opcional - Enter para pular): ").strip()
    usage_page = int(usage_page_str, 16) if usage_page_str else None
    return {
        "vendor_id": vendor_id,
        "product_id": product_id,
        "interface_number": interface_number,
        "usage_page": usage_page,
    }


def run_wizard() -> dict:
    """
    Executa o assistente de identificacao do teclado, salva a
    configuracao encontrada e a devolve.
    """
    print("\n=== Assistente de identificacao do teclado ===")
    print("Procurando dispositivos com controle proprietario (possivel iluminacao RGB)...\n")

    candidates = device.list_candidate_devices()
    cfg = None

    if not candidates:
        print("Nenhum candidato encontrado automaticamente.")
    else:
        for i, d in enumerate(candidates, start=1):
            print(f"\nCandidato {i}/{len(candidates)}: {_describe(d)}")
            if _try_candidate(d):
                cfg = {
                    "vendor_id": d["vendor_id"],
                    "product_id": d["product_id"],
                    "interface_number": d.get("interface_number"),
                    "usage_page": d.get("usage_page"),
                }
                print("  Confirmado!")
                break
            print("  Ok, tentando o proximo...")

    if cfg is None:
        print("\nNenhum candidato automatico foi confirmado.")
        cfg = _manual_entry()

    config.save_config(
        cfg["vendor_id"], cfg["product_id"], cfg["interface_number"], cfg["usage_page"]
    )
    print("\nConfiguracao salva com sucesso!\n")
    return cfg
