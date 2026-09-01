# Assistente de config inicial do teclado, para identificar o device
# Busca por candidatos que podem corresponder ao controlador
# Envia relatórios de teste para confirmação visual
# Caso a identificação automática falhe, cai para a configuração de IDs manual

from . import config
from . import device
from . import colors

# Sequência de cores de teste (Vermelho, Azul, Vermelho, Azul)
sequence = [
    (255, 255, 255),
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 255, 255),
]

# Recebe um dicionário de dados do device e cria as strings com as infos do device
def _describe(d: dict) -> str:
    manuf = d.get("manufacturer_string") or "?"
    prod = d.get("product_string") or "?"
    vid = d.get("vendor_id", 0)
    pid = d.get("product_id", 0)
    iface = d.get("interface_number")
    usage_page = d.get("usage_page", 0)
    return f"{manuf} / {prod}  (VID={vid:#06x} PID={pid:#06x} iface={iface} usage_page={usage_page:#06x})"

# Abre conexão com um candidato, envia a sequência de cores de teste, e pede confirmação visual
def _try_candidate(d: dict) -> bool:
    try:
        dev = device.open_by_path(d["path"])
    except OSError as e:
        print(f"  Nao consegui abrir esse dispositivo: {e}")
        return False

    try:
        for i, (r, g, b) in enumerate(sequence):
            report = colors.build_color_report(r, g, b)
            device.send_report(dev, report)
            if i < len(sequence) - 1:
                time.sleep(0.4)
    finally:
        dev.close()

    resposta = input("  A cor do teclado mudou? [s/n]: ").strip().lower()
    return resposta.startswith("s")

# Fallback caso a identificação falhe
def _manual_entry() -> dict:
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

# Roda o Wizard, salva a config encontrada e a devolve
def run_wizard() -> dict:
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
