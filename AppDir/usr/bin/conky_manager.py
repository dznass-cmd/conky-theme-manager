#!/usr/bin/env python3
"""
Conky Theme Manager - Gerenciador de Temas para Conky
Interface gráfica para gerenciar, criar e aplicar temas do Conky.
"""

import os
import json
import shutil
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser, scrolledtext
from pathlib import Path

BASE_DIR = Path.home() / ".conky-theme-manager"
THEMES_DIR = BASE_DIR / "themes"
CONKYRC = Path.home() / ".conkyrc"

ALIGNMENTS = [
    "top_left", "top_right", "top_center",
    "bottom_left", "bottom_right", "bottom_center",
    "middle_left", "middle_right", "middle_center",
]

def ensure_dirs():
    THEMES_DIR.mkdir(parents=True, exist_ok=True)

def theme_path(name):
    return THEMES_DIR / f"{name}.json"

def load_theme(name):
    p = theme_path(name)
    if p.exists():
        return json.loads(p.read_text())
    return None

def save_theme(name, data):
    theme_path(name).write_text(json.dumps(data, indent=2))

def delete_theme(name):
    p = theme_path(name)
    if p.exists():
        p.unlink()

def list_themes():
    return sorted([f.stem for f in THEMES_DIR.glob("*.json")])

def conkyrc_to_theme():
    text = ""
    if CONKYRC.exists():
        text = CONKYRC.read_text()

    theme = {
        "name": "Importado",
        "font_family": "JetBrains Mono",
        "font_size": 10,
        "alignment": "top_left",
        "bg_color": "#1A1A2E",
        "bg_opacity": 210,
        "text_color": "#F5E6D3",
        "accent1": "#FF6B2B",
        "accent2": "#FFB347",
        "accent3": "#4ECDC4",
        "title_color": "#FF6B2B",
        "border_color": "#FF4500",
        "border_width": 2,
        "gap_x": 50,
        "gap_y": 40,
        "min_width": 250,
        "max_width": 340,
        "min_height": 160,
        "update_interval": 5.0,
        "title_size": 18,
        "title_text": "${nodename}",
        "content": "",
        "raw_config": text,
    }

    for line in text.splitlines():
        line = line.strip()
        if "=" in line and not line.startswith("--") and not line.startswith("conky."):
            key, _, val = line.partition("=")
            key = key.strip()
            val = val.strip().rstrip(",").strip("'\"")
            if key == "font":
                parts = val.split(":")
                if len(parts) >= 1:
                    theme["font_family"] = parts[0]
                for p in parts[1:]:
                    if p.startswith("size="):
                        theme["font_size"] = int(p.split("=")[1])
                    if p == "bold":
                        pass
            elif key == "alignment":
                theme["alignment"] = val
            elif key == "own_window_argb_value":
                theme["bg_opacity"] = int(val)
            elif key == "own_window_colour":
                theme["bg_color"] = "#" + val if not val.startswith("#") else val
            elif key == "gap_x":
                theme["gap_x"] = int(val)
            elif key == "gap_y":
                theme["gap_y"] = int(val)
            elif key == "maximum_width":
                theme["max_width"] = int(val)
            elif key == "minimum_width":
                theme["min_width"] = int(val)
            elif key == "minimum_height":
                theme["min_height"] = int(val)
            elif key == "update_interval":
                theme["update_interval"] = float(val)
            elif key == "border_width":
                theme["border_width"] = int(val)

    in_text = False
    text_lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("conky.text"):
            in_text = True
            continue
        if in_text:
            text_lines.append(line)
    if text_lines:
        raw = "\n".join(text_lines).strip()
        if raw.startswith("[["):
            raw = raw[2:]
        if raw.endswith("]]"):
            raw = raw[:-2]
        theme["content"] = raw.strip()

    return theme


def theme_to_conkyrc(theme):
    lines = [
        f"-- Tema: {theme.get('name', 'Custom')}",
        "-- Gerenciado por Conky Theme Manager",
        "conky.config = {",
        f"    alignment = '{theme['alignment']}',",
        "    background = true,",
        f"    border_width = {theme['border_width']},",
        "    cpu_avg_samples = 4,",
        f"    default_color = '{_hex_to_conky(theme['text_color'])}',",
        f"    default_outline_color = '{_hex_to_conky(theme['accent1'])}',",
        f"    default_shade_color = '{_hex_to_conky(theme['bg_color'])}',",
        "    double_buffer = true,",
        f"    draw_borders = {'true' if theme['border_width'] > 0 else 'false'},",
        "    draw_graph_borders = false,",
        "    draw_outline = false,",
        "    draw_shades = false,",
        f"    font = '{theme['font_family']}:size={theme['font_size']}',",
        f"    gap_x = {theme['gap_x']},",
        f"    gap_y = {theme['gap_y']},",
        f"    minimum_height = {theme['min_height']},",
        f"    minimum_width = {theme['min_width']},",
        f"    maximum_width = {theme['max_width']},",
        "    net_avg_samples = 2,",
        "    no_buffers = true,",
        "    out_to_console = false,",
        "    out_to_x = true,",
        "    own_window = true,",
        "    own_window_class = 'Conky',",
        "    own_window_type = 'override',",
        "    own_window_transparent = false,",
        "    own_window_argb_visual = true,",
        f"    own_window_argb_value = {theme['bg_opacity']},",
        f"    own_window_colour = '{_hex_to_conky(theme['bg_color'])}',",
        "    own_window_hints = 'undecorated,sticky,skip_taskbar,skip_pager',",
        "    show_graph_scale = false,",
        "    show_graph_range = false,",
        "    stippled_borders = 0,",
        f"    update_interval = {theme['update_interval']},",
        "    uppercase = false,",
        "    use_spacer = 'none',",
        "    use_xft = true,",
        f"    color1 = '{_hex_to_conky(theme['accent1'])}',",
        f"    color2 = '{_hex_to_conky(theme['accent2'])}',",
        f"    color3 = '{_hex_to_conky(theme['text_color'])}',",
        f"    color4 = '{_hex_to_conky(theme['accent3'])}',",
        f"    color5 = '{_hex_to_conky(theme['bg_color'])}',",
        "}",
        "",
        "conky.text = [[",
    ]

    content = theme.get("content", "")
    if content.strip():
        lines.append(content)
    else:
        lines.append(f"${{color1}}${{font {theme['font_family']}:bold:size={theme['title_size']}}}{theme['title_text']}${{font}}${{color}}")
        lines.append(f"${{color4}}---${{color}}")
        lines.append(f"${{color1}}wm:${{color}}     xfwm4")
        lines.append(f"${{color1}}mem:${{color}}    ${{mem}} / ${{memmax}}")
        lines.append(f"${{color1}}cpu:${{color}}    ${{cpu cpu0}}%")
        lines.append(f"${{color4}}---${{color}}")
        lines.append(f"${{color3}}${{time %Y-%m-%d}}  ${{time %H:%M}}${{color}}")

    lines.append("]]")
    return "\n".join(lines) + "\n"


def _hex_to_conky(hex_color):
    return hex_color.lstrip("#")


def _conky_to_hex(conky_color):
    c = conky_color.lstrip("#")
    if len(c) == 6:
        return "#" + c
    return conky_color


THEME_PRESETS = [
    {
        "name": "Retro Dark",
        "font_family": "JetBrains Mono",
        "font_size": 10,
        "alignment": "top_left",
        "bg_color": "#1A1A2E",
        "bg_opacity": 210,
        "text_color": "#F5E6D3",
        "accent1": "#FF6B2B",
        "accent2": "#FFB347",
        "accent3": "#4ECDC4",
        "title_color": "#FF6B2B",
        "border_color": "#FF4500",
        "border_width": 2,
        "gap_x": 50,
        "gap_y": 40,
        "min_width": 250,
        "max_width": 340,
        "min_height": 160,
        "update_interval": 5.0,
        "title_size": 18,
        "title_text": "${nodename}",
        "content": """${color1}${font JetBrains Mono:bold:size=18}◄ ${nodename} ►${font}${color}
${color6}┌────────────────────────────┐${color}
${color1}│${color}  wm    ${color2}──►${color}  xfwm4   ${color1}│${color}
${color1}│${color}  cpu   ${color2}──►${color}  ${cpu cpu0}%      ${color1}│${color}
${color1}│${color}  mem   ${color2}──►${color}  ${mem}/${memmax}  ${color1}│${color}
${color1}│${color}  disk  ${color2}──►${color}  ${fs_used /}/${fs_size /} ${color1}│${color}
${color6}├────────────────────────────┤${color}
${color4}│${color}  ▓▓▓ ${time %d/%m/%Y}  ${time %H:%M:%S} ▓▓▓  ${color4}│${color}
${color6}└────────────────────────────┘${color}""",
    },
    {
        "name": "Minimal Light",
        "font_family": "Noto Sans Mono",
        "font_size": 11,
        "alignment": "top_right",
        "bg_color": "#F5F5F5",
        "bg_opacity": 200,
        "text_color": "#333333",
        "accent1": "#2196F3",
        "accent2": "#607D8B",
        "accent3": "#4CAF50",
        "title_color": "#1565C0",
        "border_color": "#90CAF9",
        "border_width": 0,
        "gap_x": 30,
        "gap_y": 30,
        "min_width": 200,
        "max_width": 280,
        "min_height": 100,
        "update_interval": 5.0,
        "title_size": 14,
        "title_text": "${nodename}",
        "content": """${color1}${font Noto Sans Mono:bold:size=14}${nodename}${font}${color}
${color1}────────────────${color}
${color2}wm:${color}    xfwm4
${color2}cpu:${color}   ${cpu cpu0}%
${color2}mem:${color}   ${mem} / ${memmax}
${color3}────────────────${color}
${color3}${time %d/%m/%Y}  ${time %H:%M}${color}
${color1}────────────────${color}""",
    },
    {
        "name": "Neon Cyberpunk",
        "font_family": "JetBrains Mono",
        "font_size": 10,
        "alignment": "top_right",
        "bg_color": "#0D0221",
        "bg_opacity": 220,
        "text_color": "#00FF41",
        "accent1": "#FF00FF",
        "accent2": "#00FFFF",
        "accent3": "#FFD700",
        "title_color": "#FF00FF",
        "border_color": "#FF00FF",
        "border_width": 2,
        "gap_x": 40,
        "gap_y": 40,
        "min_width": 260,
        "max_width": 350,
        "min_height": 160,
        "update_interval": 3.0,
        "title_size": 16,
        "title_text": "► ${nodename} ◄",
        "content": """${color1}${font JetBrains Mono:bold:size=16}► ${nodename} ◄${font}${color}
${color1}═══════════════════════════${color}
${color2}[${color3} WM  ${color2}]${color}  → xfwm4
${color2}[${color3} CPU ${color2}]${color}  → ${cpu cpu0}%
${color2}[${color3} MEM ${color2}]${color}  → ${mem} / ${memmax}
${color2}[${color3} DSK ${color2}]${color}  → ${fs_used /} / ${fs_size /}
${color1}═══════════════════════════${color}
${color3} ${time %d/%m/%Y} │ ${time %H:%M:%S} ${color}
${color1}═══════════════════════════${color}""",
    },
    {
        "name": "Solarized",
        "font_family": "Noto Sans Mono",
        "font_size": 10,
        "alignment": "top_left",
        "bg_color": "#002B36",
        "bg_opacity": 200,
        "text_color": "#839496",
        "accent1": "#CB4B16",
        "accent2": "#B58900",
        "accent3": "#2AA198",
        "title_color": "#CB4B16",
        "border_color": "#586E75",
        "border_width": 1,
        "gap_x": 40,
        "gap_y": 40,
        "min_width": 220,
        "max_width": 300,
        "min_height": 120,
        "update_interval": 5.0,
        "title_size": 14,
        "title_text": "${nodename}",
        "content": """${color1}${font Noto Sans Mono:bold:size=14}${nodename}${font}${color}
${color}────────────────────────
${color1}wm${color}     xfwm4
${color1}cpu${color}    ${cpu cpu0}%
${color1}mem${color}    ${mem} / ${memmax}
${color1}disk${color}   ${fs_used /} / ${fs_size /}
${color}────────────────────────
${color2}${time %Y-%m-%d}  ${time %H:%M}${color}
${color}────────────────────────${color}""",
    },
    {
        "name": "Monochrome",
        "font_family": "Noto Sans Mono",
        "font_size": 10,
        "alignment": "top_right",
        "bg_color": "#111111",
        "bg_opacity": 230,
        "text_color": "#FFFFFF",
        "accent1": "#AAAAAA",
        "accent2": "#666666",
        "accent3": "#DDDDDD",
        "title_color": "#FFFFFF",
        "border_color": "#555555",
        "border_width": 1,
        "gap_x": 40,
        "gap_y": 40,
        "min_width": 200,
        "max_width": 280,
        "min_height": 120,
        "update_interval": 5.0,
        "title_size": 14,
        "title_text": "${nodename}",
        "content": """${color}${font Noto Sans Mono:bold:size=14}${nodename}${font}
${color2}────────────────────${color}
${color1}wm:${color}    xfwm4
${color1}cpu:${color}   ${cpu cpu0}%
${color1}mem:${color}   ${mem} / ${memmax}
${color1}disk:${color}  ${fs_used /} / ${fs_size /}
${color2}────────────────────${color}
${color3}${time %Y-%m-%d %H:%M}${color}
${color2}────────────────────${color}""",
    },
    {
        "name": "Warm Sunset",
        "font_family": "JetBrains Mono",
        "font_size": 10,
        "alignment": "bottom_right",
        "bg_color": "#2D1B14",
        "bg_opacity": 200,
        "text_color": "#FFDEAD",
        "accent1": "#FF6347",
        "accent2": "#FFA07A",
        "accent3": "#FFD700",
        "title_color": "#FF4500",
        "border_color": "#CD5C5C",
        "border_width": 2,
        "gap_x": 40,
        "gap_y": 40,
        "min_width": 240,
        "max_width": 320,
        "min_height": 140,
        "update_interval": 5.0,
        "title_size": 16,
        "title_text": "~ ${nodename} ~",
        "content": """${color1}${font JetBrains Mono:bold:size=16}~ ${nodename} ~${font}${color}
${color1}·:*¨¨*:·. ${color}·:*¨¨*:·.${color}
${color2}  wm    ${color}── ${color3}xfwm4${color}
${color2}  cpu   ${color}── ${color3}${cpu cpu0}%${color}
${color2}  mem   ${color}── ${color3}${mem} / ${memmax}${color}
${color2}  disk  ${color}── ${color3}${fs_used /} / ${fs_size /}${color}
${color1}·:*¨¨*:·. ${color}·:*¨¨*:·.${color}
${color3}   ${time %d/%m/%Y}  ${time %H:%M}${color}
${color1}·:*¨¨*:·. ${color}·:*¨¨*:·.${color}""",
    },
]


class ConkyThemeManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Conky Theme Manager")
        self.root.geometry("900x650")
        self.root.minsize(800, 550)
        self.root.configure(bg="#1e1e2e")

        self.current_theme = None
        self.current_theme_name = None

        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Dark.TFrame", background="#1e1e2e")
        style.configure("Dark.TLabel", background="#1e1e2e", foreground="#cdd6f4", font=("Noto Sans", 10))
        style.configure("Dark.TButton", background="#313244", foreground="#cdd6f4", font=("Noto Sans", 10, "bold"), padding=(12, 6))
        style.map("Dark.TButton", background=[("active", "#45475a")])
        style.configure("Accent.TButton", background="#FF6B2B", foreground="#1e1e2e", font=("Noto Sans", 10, "bold"), padding=(12, 6))
        style.map("Accent.TButton", background=[("active", "#FFB347")])
        style.configure("Danger.TButton", background="#F38BA8", foreground="#1e1e2e", font=("Noto Sans", 10, "bold"), padding=(12, 6))
        style.map("Danger.TButton", background=[("active", "#FFB4C2")])
        style.configure("Dark.TLabel", background="#1e1e2e", foreground="#cdd6f4", font=("Noto Sans", 10))
        style.configure("Header.TLabel", background="#1e1e2e", foreground="#FF6B2B", font=("Noto Sans", 16, "bold"))
        style.configure("Theme.TListbox", background="#181825", foreground="#cdd6f4", selectbackground="#FF6B2B", selectforeground="#1e1e2e", font=("Noto Sans", 11), relief="flat", highlightthickness=0, activestyle="none")
        style.configure("Dark.TEntry", fieldbackground="#313244", foreground="#cdd6f4", insertcolor="#cdd6f4", relief="flat")
        style.configure("Dark.TCombobox", fieldbackground="#313244", foreground="#cdd6f4", selectbackground="#FF6B2B", relief="flat")
        style.configure("Dark.TScale", background="#1e1e2e", troughcolor="#313244")
        style.configure("Dark.TSpinbox", fieldbackground="#313244", foreground="#cdd6f4", relief="flat")
        style.configure("Dark.TNotebook", background="#1e1e2e")
        style.configure("Dark.TNotebook.Tab", background="#313244", foreground="#cdd6f4", padding=(12, 6), font=("Noto Sans", 10))
        style.map("Dark.TNotebook.Tab", background=[("selected", "#FF6B2B")], foreground=[("selected", "#1e1e2e")])

        self._build_ui()
        self._populate_presets()
        self._refresh_list()

        if list_themes():
            self._select_first()

    def _build_ui(self):
        top = ttk.Frame(self.root, style="Dark.TFrame")
        top.pack(fill="x", padx=16, pady=(12, 0))
        ttk.Label(top, text="Conky Theme Manager", style="Header.TLabel").pack(side="left")
        ttk.Label(top, text="by dznas", style="Dark.TLabel").pack(side="right")

        sep = tk.Frame(self.root, bg="#45475a", height=1)
        sep.pack(fill="x", padx=16, pady=8)

        main = ttk.Frame(self.root, style="Dark.TFrame")
        main.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        left = ttk.Frame(main, style="Dark.TFrame", width=220)
        left.pack(side="left", fill="y", padx=(0, 10))
        left.pack_propagate(False)

        ttk.Label(left, text="Temas", style="Dark.TLabel", font=("Noto Sans", 12, "bold")).pack(anchor="w", pady=(0, 6))

        list_frame = tk.Frame(left, bg="#181825", highlightthickness=1, highlightbackground="#45475a")
        list_frame.pack(fill="both", expand=True)

        self.theme_listbox = tk.Listbox(list_frame, **{
            "bg": "#181825",
            "fg": "#cdd6f4",
            "selectbackground": "#FF6B2B",
            "selectforeground": "#1e1e2e",
            "font": ("Noto Sans", 11),
            "relief": "flat",
            "highlightthickness": 0,
            "activestyle": "none",
            "bd": 0,
            "selectborderwidth": 0,
        })
        self.theme_listbox.pack(fill="both", expand=True, padx=2, pady=2)
        self.theme_listbox.bind("<<ListboxSelect>>", self._on_select)

        btn_frame = ttk.Frame(left, style="Dark.TFrame")
        btn_frame.pack(fill="x", pady=(8, 0))

        ttk.Button(btn_frame, text="▶ Aplicar Tema", style="Accent.TButton", command=self._apply_selected_theme).pack(fill="x", pady=(0, 4))
        ttk.Button(btn_frame, text="+ Novo", style="Dark.TButton", command=self._new_theme).pack(fill="x", pady=(0, 4))
        ttk.Button(btn_frame, text="Importar .json", style="Dark.TButton", command=self._import_theme).pack(fill="x", pady=(0, 4))

        right = ttk.Frame(main, style="Dark.TFrame")
        right.pack(side="left", fill="both", expand=True)

        self.notebook = ttk.Notebook(right, style="Dark.TNotebook")
        self.notebook.pack(fill="both", expand=True)

        self._build_editor_tab()
        self._build_preview_tab()
        self._build_raw_tab()

        bottom = ttk.Frame(self.root, style="Dark.TFrame")
        bottom.pack(fill="x", padx=16, pady=(0, 12))

        self.status_var = tk.StringVar(value="Pronto")
        ttk.Label(bottom, textvariable=self.status_var, style="Dark.TLabel").pack(side="left")

        btn_bottom = ttk.Frame(bottom, style="Dark.TFrame")
        btn_bottom.pack(side="right")

        ttk.Button(btn_bottom, text="Exportar", style="Dark.TButton", command=self._export_theme).pack(side="left", padx=(0, 6))
        ttk.Button(btn_bottom, text="Aplicar", style="Accent.TButton", command=self._apply_theme).pack(side="left", padx=(0, 6))
        ttk.Button(btn_bottom, text="Deletar", style="Danger.TButton", command=self._delete_theme).pack(side="left")

    def _build_editor_tab(self):
        tab = ttk.Frame(self.notebook, style="Dark.TFrame")
        self.notebook.add(tab, text="  Editor  ")

        canvas = tk.Canvas(tab, bg="#1e1e2e", highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas, style="Dark.TFrame")

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.editor_fields = {}
        row = 0

        def add_section(text):
            nonlocal row
            ttk.Label(scroll_frame, text=text, style="Dark.TLabel", font=("Noto Sans", 12, "bold")).grid(row=row, column=0, columnspan=4, sticky="w", pady=(12, 4), padx=8)
            row += 1

        def add_entry(label, key, default="", width=20):
            nonlocal row
            ttk.Label(scroll_frame, text=label, style="Dark.TLabel").grid(row=row, column=0, sticky="w", padx=8, pady=3)
            var = tk.StringVar(value=str(default))
            entry = ttk.Entry(scroll_frame, textvariable=var, width=width, style="Dark.TEntry")
            entry.grid(row=row, column=1, columnspan=3, sticky="w", padx=8, pady=3)
            self.editor_fields[key] = var
            row += 1

        def add_color(label, key, default="#FFFFFF"):
            nonlocal row
            ttk.Label(scroll_frame, text=label, style="Dark.TLabel").grid(row=row, column=0, sticky="w", padx=8, pady=3)
            var = tk.StringVar(value=default)
            entry = ttk.Entry(scroll_frame, textvariable=var, width=14, style="Dark.TEntry")
            entry.grid(row=row, column=1, sticky="w", padx=8, pady=3)
            btn = tk.Button(scroll_frame, text="🎨", bg="#313244", fg="#cdd6f4", bd=0, font=("Noto Sans", 10),
                           command=lambda v=var: self._pick_color(v))
            btn.grid(row=row, column=2, sticky="w", padx=4, pady=3)
            preview = tk.Frame(scroll_frame, bg=default, width=24, height=24, highlightthickness=1, highlightbackground="#45475a")
            preview.grid(row=row, column=3, sticky="w", padx=4, pady=3)

            def update_preview(*args):
                try:
                    preview.configure(bg=var.get())
                except:
                    pass
            var.trace_add("write", update_preview)
            self.editor_fields[key] = var

        def add_combo(label, key, values, default=""):
            nonlocal row
            ttk.Label(scroll_frame, text=label, style="Dark.TLabel").grid(row=row, column=0, sticky="w", padx=8, pady=3)
            var = tk.StringVar(value=default)
            combo = ttk.Combobox(scroll_frame, textvariable=var, values=values, width=18, style="Dark.TCombobox", state="readonly")
            combo.grid(row=row, column=1, columnspan=3, sticky="w", padx=8, pady=3)
            self.editor_fields[key] = var
            row += 1

        def add_spin(label, key, default=0, from_=0, to=999, width=8):
            nonlocal row
            ttk.Label(scroll_frame, text=label, style="Dark.TLabel").grid(row=row, column=0, sticky="w", padx=8, pady=3)
            var = tk.IntVar(value=default)
            spin = tk.Spinbox(scroll_frame, from_=from_, to=to, textvariable=var, width=width,
                             bg="#313244", fg="#cdd6f4", buttonbackground="#45475a", bd=0, relief="flat",
                             font=("Noto Sans", 10))
            spin.grid(row=row, column=1, columnspan=3, sticky="w", padx=8, pady=3)
            self.editor_fields[key] = var
            row += 1

        def add_scale(label, key, default=200, from_=0, to=255):
            nonlocal row
            ttk.Label(scroll_frame, text=label, style="Dark.TLabel").grid(row=row, column=0, sticky="w", padx=8, pady=3)
            var = tk.IntVar(value=default)
            scale = ttk.Scale(scroll_frame, from_=from_, to=to, variable=var, orient="horizontal", length=200)
            scale.grid(row=row, column=1, columnspan=2, sticky="w", padx=8, pady=3)
            lbl = ttk.Label(scroll_frame, textvariable=var, style="Dark.TLabel", width=4)
            lbl.grid(row=row, column=3, sticky="w", padx=4)
            self.editor_fields[key] = var
            row += 1

        def add_text(label, key, default="", height=8):
            nonlocal row
            ttk.Label(scroll_frame, text=label, style="Dark.TLabel").grid(row=row, column=0, columnspan=4, sticky="w", padx=8, pady=(8, 2))
            row += 1
            text_widget = scrolledtext.ScrolledText(scroll_frame, height=height, bg="#313244", fg="#cdd6f4",
                                                     insertbackground="#cdd6f4", font=("JetBrains Mono", 10),
                                                     relief="flat", highlightthickness=1, highlightbackground="#45475a",
                                                     wrap="word", bd=0)
            text_widget.grid(row=row, column=0, columnspan=4, sticky="we", padx=8, pady=3)
            self.editor_fields[key] = text_widget
            row += 1

        add_section("Identidade")
        add_entry("Nome", "name", "Meu Tema")
        add_entry("Título", "title_text", "${nodename}")

        add_section("Visual")
        add_color("Fundo", "bg_color", "#1A1A2E")
        add_scale("Opacidade", "bg_opacity", 210, 50, 255)
        add_color("Texto", "text_color", "#F5E6D3")
        add_color("Accent 1", "accent1", "#FF6B2B")
        add_color("Accent 2", "accent2", "#FFB347")
        add_color("Accent 3", "accent3", "#4ECDC4")
        add_spin("Borda (px)", "border_width", 2, 0, 10)

        add_section("Posição & Tamanho")
        add_combo("Alinhamento", "alignment", ALIGNMENTS, "top_left")
        add_spin("Gap X", "gap_x", 50, 0, 200)
        add_spin("Gap Y", "gap_y", 40, 0, 200)
        add_spin("Largura Min", "min_width", 250, 100, 600)
        add_spin("Largura Max", "max_width", 340, 150, 800)
        add_spin("Altura Min", "min_height", 160, 50, 400)

        add_section("Fonte")
        add_entry("Família", "font_family", "JetBrains Mono")
        add_spin("Tamanho", "font_size", 10, 6, 30)
        add_spin("Título (px)", "title_size", 18, 8, 40)
        add_spin("Update (s)", "update_interval", 5, 1, 30)

        add_section("Conteúdo (Conky Text)")
        add_text("Conteúdo Conky", "content", "", height=10)

    def _build_preview_tab(self):
        tab = ttk.Frame(self.notebook, style="Dark.TFrame")
        self.notebook.add(tab, text="  Preview  ")

        self.preview_text = tk.Text(tab, bg="#1A1A2E", fg="#F5E6D3",
                                     font=("JetBrains Mono", 11), relief="flat",
                                     highlightthickness=0, bd=0, wrap="word",
                                     insertbackground="#F5E6D3", state="disabled")
        self.preview_text.pack(fill="both", expand=True, padx=4, pady=4)

        self.preview_text.tag_configure("accent1", foreground="#FF6B2B")
        self.preview_text.tag_configure("accent2", foreground="#FFB347")
        self.preview_text.tag_configure("accent3", foreground="#4ECDC4")
        self.preview_text.tag_configure("title", foreground="#FF6B2B", font=("JetBrains Mono", 14, "bold"))

    def _build_raw_tab(self):
        tab = ttk.Frame(self.notebook, style="Dark.TFrame")
        self.notebook.add(tab, text="  Raw .conkyrc  ")

        self.raw_text = scrolledtext.ScrolledText(tab, bg="#181825", fg="#cdd6f4",
                                                   font=("JetBrains Mono", 10), relief="flat",
                                                   highlightthickness=0, bd=0, wrap="word",
                                                   insertbackground="#cdd6f4")
        self.raw_text.pack(fill="both", expand=True, padx=4, pady=4)

        btn_frame = ttk.Frame(tab, style="Dark.TFrame")
        btn_frame.pack(fill="x", padx=4, pady=(0, 4))
        ttk.Button(btn_frame, text="Copiar", style="Dark.TButton", command=self._copy_raw).pack(side="left")
        ttk.Button(btn_frame, text="Salvar Raw", style="Accent.TButton", command=self._save_raw).pack(side="left", padx=6)

    def _pick_color(self, var):
        color = colorchooser.askcolor(initialcolor=var.get())
        if color and color[1]:
            var.set(color[1])

    def _populate_presets(self):
        for preset in THEME_PRESETS:
            name = preset["name"]
            if not theme_path(name).exists():
                save_theme(name, preset)

    def _refresh_list(self):
        self.theme_listbox.delete(0, "end")
        for name in list_themes():
            self.theme_listbox.insert("end", name)

    def _select_first(self):
        themes = list_themes()
        if themes:
            self.theme_listbox.selection_set(0)
            self._load_selected()

    def _on_select(self, event=None):
        self._load_selected()

    def _load_selected(self):
        sel = self.theme_listbox.curselection()
        if not sel:
            return
        name = self.theme_listbox.get(sel[0])
        theme = load_theme(name)
        if not theme:
            return

        self.current_theme_name = name
        self.current_theme = theme

        for key, widget in self.editor_fields.items():
            val = theme.get(key, "")
            if isinstance(widget, tk.Text):
                widget.delete("1.0", "end")
                widget.insert("1.0", val)
            elif isinstance(widget, tk.IntVar):
                try:
                    widget.set(int(val))
                except (ValueError, TypeError):
                    widget.set(0)
            else:
                widget.set(str(val))

        self._update_preview()
        self._update_raw()
        self.status_var.set(f"Tema: {name}")

    def _gather_theme(self):
        data = {}
        for key, widget in self.editor_fields.items():
            if isinstance(widget, tk.Text):
                content = widget.get("1.0", "end-1c")
                data[key] = content
            elif isinstance(widget, tk.IntVar):
                data[key] = widget.get()
            else:
                data[key] = widget.get()
        return data

    def _update_preview(self):
        theme = self.current_theme or self._gather_theme()
        self.preview_text.config(state="normal")
        self.preview_text.delete("1.0", "end")

        preview = f"=== PREVIEW: {theme.get('name', 'Theme')} ===\n\n"
        preview += f"  Alinhamento: {theme.get('alignment', 'top_left')}\n"
        preview += f"  Fonte: {theme.get('font_family', 'mono')} {theme.get('font_size', 10)}\n"
        preview += f"  Fundo: {theme.get('bg_color', '#000')} (opacidade: {theme.get('bg_opacity', 200)})\n\n"
        preview += f"  ── Cores ──\n"
        preview += f"  Texto:  {theme.get('text_color', '#FFF')}\n"
        preview += f"  Accent1: {theme.get('accent1', '#FF0')}\n"
        preview += f"  Accent2: {theme.get('accent2', '#0FF')}\n"
        preview += f"  Accent3: {theme.get('accent3', '#0F0')}\n\n"
        preview += f"  ── Conteúdo ──\n"

        content = theme.get("content", "")
        if content:
            lines = content.split("\n")
            for line in lines[:20]:
                clean = line.replace("${color1}", "").replace("${color2}", "").replace("${color3}", "").replace("${color4}", "").replace("${color5}", "").replace("${color6}", "")
                clean = clean.replace("${font}", "").replace("${nodename}", "[hostname]")
                clean = clean.replace("${cpu cpu0}", "12").replace("${mem}", "4.5GiB").replace("${memmax}", "16GiB")
                clean = clean.replace("${fs_used /}", "45GiB").replace("${fs_size /}", "256GiB")
                import re
                clean = re.sub(r'\$\{time[^}]*\}', '01/08/2026 14:30', clean)
                clean = re.sub(r'\$\{font[^}]*\}', '', clean)
                preview += f"  {clean}\n"

        self.preview_text.insert("1.0", preview)
        self.preview_text.config(state="disabled")

    def _update_raw(self):
        theme = self._gather_theme()
        raw = theme_to_conkyrc(theme)
        self.raw_text.config(state="normal")
        self.raw_text.delete("1.0", "end")
        self.raw_text.insert("1.0", raw)
        self.raw_text.config(state="normal")

    def _new_theme(self):
        name = tk.simpledialog.askstring("Novo Tema", "Nome do novo tema:", parent=self.root) if hasattr(tk, 'simpledialog') else None
        if not name:
            dialog = tk.Toplevel(self.root)
            dialog.title("Novo Tema")
            dialog.geometry("350x120")
            dialog.configure(bg="#1e1e2e")
            dialog.transient(self.root)
            dialog.grab_set()

            ttk.Label(dialog, text="Nome do novo tema:", style="Dark.TLabel").pack(pady=(16, 8))
            name_var = tk.StringVar()
            entry = ttk.Entry(dialog, textvariable=name_var, width=30, style="Dark.TEntry")
            entry.pack(pady=4)
            entry.focus_set()

            def confirm():
                nonlocal name
                name = name_var.get().strip()
                if name:
                    dialog.destroy()

            ttk.Button(dialog, text="Criar", style="Accent.TButton", command=confirm).pack(pady=8)
            dialog.bind("<Return>", lambda e: confirm())
            self.root.wait_window(dialog)

        if not name:
            return

        if theme_path(name).exists():
            messagebox.showwarning("Aviso", f"Tema '{name}' já existe!")
            return

        new_theme = {
            "name": name,
            "font_family": "JetBrains Mono",
            "font_size": 10,
            "alignment": "top_left",
            "bg_color": "#1A1A2E",
            "bg_opacity": 200,
            "text_color": "#F5E6D3",
            "accent1": "#FF6B2B",
            "accent2": "#FFB347",
            "accent3": "#4ECDC4",
            "title_color": "#FF6B2B",
            "border_color": "#FF4500",
            "border_width": 2,
            "gap_x": 50,
            "gap_y": 40,
            "min_width": 250,
            "max_width": 340,
            "min_height": 160,
            "update_interval": 5.0,
            "title_size": 16,
            "title_text": "${nodename}",
            "content": "",
        }
        save_theme(name, new_theme)
        self._refresh_list()
        idx = list_themes().index(name)
        self.theme_listbox.selection_set(idx)
        self._load_selected()
        self.status_var.set(f"Tema '{name}' criado!")

    def _delete_theme(self):
        if not self.current_theme_name:
            return
        if messagebox.askyesno("Confirmar", f"Deletar tema '{self.current_theme_name}'?"):
            delete_theme(self.current_theme_name)
            self._refresh_list()
            self.current_theme_name = None
            self.current_theme = None
            self._select_first()
            self.status_var.set("Tema deletado!")

    def _apply_selected_theme(self):
        sel = self.theme_listbox.curselection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um tema primeiro!")
            return

        name = self.theme_listbox.get(sel[0])
        theme = load_theme(name)
        if not theme:
            messagebox.showerror("Erro", f"Tema '{name}' não encontrado!")
            return

        content = theme.get("content", "")
        if not content or not content.strip():
            font_family = theme.get('font_family', 'JetBrains Mono')
            title_size = theme.get('title_size', 16)
            title_text = theme.get('title_text', '${nodename}')
            theme["content"] = f"${{color1}}${{font {font_family}:bold:size={title_size}}}{title_text}${{font}}${{color}}\n${{color4}}────────────────────${{color}}\n${{color1}}wm:${{color}}     xfwm4\n${{color1}}mem:${{color}}    ${{mem}} / ${{memmax}}\n${{color1}}cpu:${{color}}    ${{cpu cpu0}}%\n${{color4}}────────────────────${{color}}\n${{color3}}${{time %Y-%m-%d}}  ${{time %H:%M}}${{color}}"

        conf = theme_to_conkyrc(theme)

        if CONKYRC.exists():
            backup = CONKYRC.with_suffix(".rc.backup")
            shutil.copy2(CONKYRC, backup)

        CONKYRC.write_text(conf)

        try:
            subprocess.run(["killall", "conky"], capture_output=True)
        except FileNotFoundError:
            pass

        import time
        time.sleep(0.5)

        try:
            subprocess.Popen(["conky"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.status_var.set(f"Tema '{name}' aplicado com sucesso!")
            messagebox.showinfo("Sucesso", f"Tema '{name}' aplicado!\nBackup salvo em .conkyrc.backup")
        except FileNotFoundError:
            self.status_var.set("Conky não encontrado! Instale o conky.")
            messagebox.showerror("Erro", "Conky não encontrado no sistema!")

    def _apply_theme(self):
        theme = self._gather_theme()

        content = theme.get("content", "")
        if not content or not content.strip():
            font_family = theme.get('font_family', 'JetBrains Mono')
            title_size = theme.get('title_size', 16)
            title_text = theme.get('title_text', '${nodename}')
            theme["content"] = f"${{color1}}${{font {font_family}:bold:size={title_size}}}{title_text}${{font}}${{color}}\n${{color4}}────────────────────${{color}}\n${{color1}}wm:${{color}}     xfwm4\n${{color1}}mem:${{color}}    ${{mem}} / ${{memmax}}\n${{color1}}cpu:${{color}}    ${{cpu cpu0}}%\n${{color4}}────────────────────${{color}}\n${{color3}}${{time %Y-%m-%d}}  ${{time %H:%M}}${{color}}"

        conf = theme_to_conkyrc(theme)

        if CONKYRC.exists():
            backup = CONKYRC.with_suffix(".rc.backup")
            shutil.copy2(CONKYRC, backup)

        CONKYRC.write_text(conf)

        try:
            subprocess.run(["killall", "conky"], capture_output=True)
        except FileNotFoundError:
            pass

        import time
        time.sleep(0.5)

        try:
            subprocess.Popen(["conky"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.status_var.set(f"Tema '{theme.get('name')}' aplicado com sucesso!")
            messagebox.showinfo("Sucesso", f"Tema '{theme.get('name')}' aplicado!\nBackup salvo em .conkyrc.backup")
        except FileNotFoundError:
            self.status_var.set("Conky não encontrado! Instale o conky.")
            messagebox.showerror("Erro", "Conky não encontrado no sistema!")

    def _export_theme(self):
        if not self.current_theme_name:
            return
        theme = self._gather_theme()
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("Todos", "*.*")],
            initialfile=f"{theme.get('name', 'theme')}.json",
            title="Exportar Tema"
        )
        if path:
            Path(path).write_text(json.dumps(theme, indent=2))
            self.status_var.set(f"Tema exportado: {path}")

    def _import_theme(self):
        path = filedialog.askopenfilename(
            filetypes=[("JSON", "*.json"), ("Todos", "*.*")],
            title="Importar Tema"
        )
        if path:
            try:
                data = json.loads(Path(path).read_text())
                name = data.get("name", Path(path).stem)
                data["name"] = name
                save_theme(name, data)
                self._refresh_list()
                idx = list_themes().index(name)
                self.theme_listbox.selection_set(idx)
                self._load_selected()
                self.status_var.set(f"Tema '{name}' importado!")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao importar: {e}")

    def _copy_raw(self):
        raw = self.raw_text.get("1.0", "end")
        self.root.clipboard_clear()
        self.root.clipboard_append(raw)
        self.status_var.set("Copiado para a área de transferência!")

    def _save_raw(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".conf",
            filetypes=[("Conky Config", "*.conf"), ("Todos", "*.*")],
            initialfile=".conkyrc",
            title="Salvar Configuração"
        )
        if path:
            raw = self.raw_text.get("1.0", "end")
            Path(path).write_text(raw)
            self.status_var.set(f"Salvo em: {path}")


def main():
    ensure_dirs()
    root = tk.Tk()
    root.withdraw()

    root.after(100, lambda: root.deiconify())

    app = ConkyThemeManager(root)
    root.mainloop()


if __name__ == "__main__":
    main()
