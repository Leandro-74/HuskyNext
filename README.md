<p align="center">
  <img src="assets/logo.png" alt="Logo do HuskyNext" width="120">
</p>

<h1 align="center">HuskyNext</h1>

<p align="center">
  Ferramenta em Python para controlar a cor do LED do teclado <b>Husky Sled</b>
  via linha de comando — sem depender do software oficial da Husky.
</p>

> ⚠️ Projeto não-oficial, feito por engenharia reversa. Sem vínculo com a Husky. Use por sua conta e risco.

O projeto nasceu de uma engenharia reversa do protocolo USB HID do teclado: os comandos de troca de cor foram capturados com Wireshark/USBPcap enquanto o software original da Husky era usado, e depois replicados diretamente via HID.

## Funcionalidades

- Definir a cor do LED do teclado via código HEX (`FF5733`, `#00FF88`, etc.)
- Identificação **guiada** do teclado na primeira execução (não precisa saber VID/PID de antemão)
- Configuração salva automaticamente, sem precisar repetir a identificação toda vez
- Interface simples em linha de comando, por menu numerado

## Requisitos

- Python 3.10 ou superior
- Windows ou Linux (testado até agora principalmente no Windows; suporte a Linux em andamento)

### ⚠️ Nota para usuários Linux
Devido às restrições de permissão do kernel Linux em dispositivos USB raw (HID), você precisará criar uma regra do `udev` para rodar o script sem `sudo`.
Crie o arquivo `/etc/udev/rules.d/99-huskynext.rules` com o seu VID e PID (exemplo):
```
SUBSYSTEM=="usb", ATTRS{idVendor}=="SEU_VID", ATTRS{idProduct}=="SEU_PID", MODE="0666"
```
Depois, recarregue as regras: `sudo udevadm control --reload-rules && udevadm trigger`

## Instalação

```bash
git clone https://github.com/<seu-usuario>/huskynext.git
cd huskynext
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
```

## Uso

Rode a partir da raiz do projeto:

```bash
python main.py
```

### Primeira execução

Na primeira vez, o programa vai procurar automaticamente por dispositivos com um controle de iluminação proprietário conectados ao computador. Para cada candidato encontrado, ele:

1. Envia uma cor de teste (vermelho) para o dispositivo
2. Pergunta se a cor do teclado mudou

Se você confirmar, a configuração é salva em `~/.huskynext/config.json` e não será pedida novamente. Se nenhum candidato for confirmado, você pode informar o Vendor ID e Product ID manualmente (encontrados no Gerenciador de Dispositivos no Windows, ou com `lsusb` no Linux).

### Menu

```
=== HuskyNext - Controle de RGB para teclados Husky ===

1. Definir cor (HEX)
2. Escolher modo de iluminação
3. Brilho
4. Testar cor original (diagnostico)
5. Reconfigurar teclado (VID/PID)
6. Sair
```

- **1. Definir cor**: digite um código HEX (ex: `FF5733`) e o teclado mudará para essa cor
- **2. Escolher modo de iluminação**: escolha um dos modos listados e o teclado mudará para ele
- **3. Brilho**: escolha um dos níveis de brilho listados e o teclado mudará para ele
- **4. Testar cor original**: reenvia o exato pacote capturado na engenharia reversa — útil para diagnosticar problemas de comunicação
- **5. Reconfigurar**: apaga a configuração salva e roda o assistente de identificação de novo (útil se você trocar de teclado ou a identificação salva parar de funcionar)

## Estrutura do projeto

```
huskynext/
├── main.py                # ponto de entrada
├── requirements.txt
├── README.md
└── src/
    ├── config.py            # carrega/salva a configuracao do teclado
    ├── device.py             # comunicacao HID de baixo nivel
    ├── colors.py             # parsing de HEX e montagem do relatorio HID
    ├── setup_wizard.py       # assistente de identificacao do teclado
    └── cli.py                # menu e loop principal
```

## Como funciona por baixo dos panos

O teclado expõe várias interfaces/collections HID; a de controle de iluminação é identificada por um `usage_page` na faixa vendor-specific (`0xff00`–`0xffff`). O comando de cor é enviado como um `SET_REPORT` HID (Report ID `0x04`, tipo Output), com um payload de 64 bytes onde os bytes 14, 15 e 16 representam, respectivamente, os canais R, G e B.

## Roadmap

- [ ] Suporte a efeitos/animações (respiração, onda, arco-íris, etc.)
- [ ] Suporte testado e documentado no Linux
- [ ] Empacotamento via `pip install`

## Contribuindo

Se você tem um teclado Husky Sled e o assistente de identificação não funcionou, abra uma *issue* com a saída do menu de diagnóstico — isso ajuda a mapear variações entre modelos/revisões do controlador.

Pull requests são bem-vindos, especialmente para:
- Suporte a novos efeitos de iluminação
- Testes e ajustes para Linux
- Melhorias na interface CLI

## Licença

<!-- Defina a licença do projeto, ex: MIT -->
