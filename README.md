# Conky Theme Manager

Gerenciador de temas para [Conky](https://github.com/brndnmtthws/conky) com interface gráfica.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-FF6B2B)
![License](https://img.shields.io/badge/License-MIT-green)

## Funcionalidades

- **Editor Visual** — Edite cores, fonte, opacidade, posição e conteúdo
- **Preview ao vivo** — Veja como o tema fica antes de aplicar
- **Raw Editor** — Edite o `.conkyrc` diretamente
- **Aplicar** — Salva no `.conkyrc` e reinicia o conky automaticamente
- **Exportar/Importar** — Salve e carregue temas como arquivos JSON
- **Criar/Deletar** — Gerencie seus próprios temas
- **6 Temas Pré-incluídos** — Retro Dark, Minimal Light, Neon Cyberpunk, Solarized, Monochrome, Warm Sunset

## Captura de Tela

```
┌─────────────────────────────────────────────┐
│  Conky Theme Manager                        │
├──────────────┬──────────────────────────────┤
│  Temas       │  Editor / Preview / Raw      │
│  ┌────────┐  │  ┌────────────────────────┐  │
│  │ retro  │  │  │  Nome: Retro Dark      │  │
│  │ neon   │  │  │  Fundo: [#1A1A2E] 🎨   │  │
│  │ solar  │  │  │  Texto: [#F5E6D3] 🎨   │  │
│  │ mono   │  │  │  Accent: [#FF6B2B] 🎨  │  │
│  │ sunset │  │  │  ...                   │  │
│  │ light  │  │  └────────────────────────┘  │
│  └────────┘  │  [Aplicar] [Exportar]        │
├──────────────┴──────────────────────────────┤
│  Status: Tema "retro" aplicado!             │
└─────────────────────────────────────────────┘
```

## Instalação

### Dependências

```bash
# Arch/Manjaro
sudo pacman -S tk python

# Debian/Ubuntu
sudo apt install python3-tk

# Fedora
sudo dnf install python3-tkinter
```

### Uso

```bash
# Clone o repositório
git clone https://github.com/dznass-cmd/conky-theme-manager.git
cd conky-theme-manager

# Execute
chmod +x launch.sh
./launch.sh
```

Ou diretamente:

```bash
python3 conky_manager.py
```

## Temas Incluídos

| Tema | Descrição |
|------|-----------|
| **Retro Dark** | Navy escuro com laranja vibrante |
| **Minimal Light** | Fundo claro, minimalista |
| **Neon Cyberpunk** | Verde neon, fundo escuro |
| **Solarized** | Cores solarized clássicas |
| **Monochrome** | Preto e branco puro |
| **Warm Sunset** | Tons de pôr do sol |

## Estrutura

```
conky-theme-manager/
├── conky_manager.py    # Aplicação principal
├── launch.sh           # Script de inicialização
├── README.md           # Este arquivo
└── themes/             # Temas salvos (JSON)
```

## Como Funciona

1. Selecione um tema na lista lateral
2. Edite as propriedades no aba **Editor**
3. Veja o resultado no aba **Preview**
4. Clique em **Aplicar** para salvar e ativar
5. Exporte seus temas como JSON para compartilhar

## Licença

MIT
