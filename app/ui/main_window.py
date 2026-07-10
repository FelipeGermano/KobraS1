from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from app.domain.material import MATERIALS
from app.domain.slicing_profile import UserChoices
from app.services.profile_engine import QUALITY_RULES, STRENGTH_RULES, build_profile
from app.services.report_service import build_summary, save_summary
from app.services.model_import_service import ModelImportError, analyze_model


class MainWindow(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Kobra S1 Assistant")
        self.geometry("760x560")
        self.minsize(680, 520)

        self.selected_file = tk.StringVar()
        self.material = tk.StringVar(value="PLA")
        self.strength = tk.StringVar(value="Uso comum")
        self.quality = tk.StringVar(value="Normal")
        self.priority = tk.StringVar(value="equilibrio")
        self.supports_allowed = tk.BooleanVar(value=True)
        self.analysis_text = tk.StringVar(value="Selecione um arquivo STL ou 3MF para comecar.")

        self._build_layout()

    def _build_layout(self) -> None:
        root = ttk.Frame(self, padding=16)
        root.pack(fill=tk.BOTH, expand=True)

        file_row = ttk.Frame(root)
        file_row.pack(fill=tk.X, pady=(0, 12))
        ttk.Entry(file_row, textvariable=self.selected_file).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(file_row, text="Selecionar modelo", command=self._select_file).pack(side=tk.LEFT, padx=(8, 0))

        form = ttk.LabelFrame(root, text="Opcoes de uso", padding=12)
        form.pack(fill=tk.X, pady=(0, 12))

        self._combo(form, "Material", self.material, list(MATERIALS))
        self._combo(form, "Resistencia", self.strength, list(STRENGTH_RULES))
        self._combo(form, "Qualidade", self.quality, list(QUALITY_RULES))
        self._combo(
            form,
            "Prioridade",
            self.priority,
            ["equilibrio", "economia de material", "resistencia", "qualidade visual", "velocidade"],
        )
        ttk.Checkbutton(form, text="Permitir suportes quando recomendados", variable=self.supports_allowed).pack(
            anchor=tk.W, pady=(6, 0)
        )

        analysis_box = ttk.LabelFrame(root, text="Resumo", padding=12)
        analysis_box.pack(fill=tk.BOTH, expand=True)
        ttk.Label(
            analysis_box,
            textvariable=self.analysis_text,
            justify=tk.LEFT,
            anchor=tk.NW,
            wraplength=700,
        ).pack(fill=tk.BOTH, expand=True)

        ttk.Button(root, text="Gerar resumo JSON", command=self._generate_summary).pack(anchor=tk.E, pady=(12, 0))

    def _combo(self, parent: ttk.Frame, label: str, variable: tk.StringVar, values: list[str]) -> None:
        row = ttk.Frame(parent)
        row.pack(fill=tk.X, pady=3)
        ttk.Label(row, text=label, width=14).pack(side=tk.LEFT)
        ttk.Combobox(row, textvariable=variable, values=values, state="readonly").pack(
            side=tk.LEFT, fill=tk.X, expand=True
        )

    def _select_file(self) -> None:
        path = filedialog.askopenfilename(
            title="Selecione um STL ou 3MF",
            filetypes=[("Modelos 3D", "*.stl *.3mf"), ("STL", "*.stl"), ("3MF", "*.3mf"), ("Todos os arquivos", "*.*")],
        )
        if path:
            self.selected_file.set(path)
            self._refresh_analysis()

    def _refresh_analysis(self) -> None:
        try:
            analysis = analyze_model(self.selected_file.get())
        except ModelImportError as exc:
            self.analysis_text.set(str(exc))
            return

        self.analysis_text.set(_format_analysis(analysis))

    def _generate_summary(self) -> None:
        source = self.selected_file.get()
        if not source:
            messagebox.showerror("Arquivo obrigatorio", "Selecione um arquivo STL antes de gerar o resumo.")
            return

        try:
            analysis = analyze_model(source)
            choices = UserChoices(
                material=self.material.get(),
                strength=self.strength.get(),
                quality=self.quality.get(),
                priority=self.priority.get(),
                supports_allowed=self.supports_allowed.get(),
            )
            profile = build_profile(choices, analysis)
            summary = build_summary(analysis, choices, profile)
            output_path = save_summary(summary, Path("logs"))
        except (ModelImportError, ValueError) as exc:
            messagebox.showerror("Nao foi possivel gerar", str(exc))
            return

        self.analysis_text.set(_format_analysis(analysis) + "\n\n" + _format_profile(profile))
        messagebox.showinfo("Resumo gerado", f"Resumo salvo em:\n{output_path}")


def _format_analysis(analysis) -> str:
    warnings = "\n".join(f"- {warning}" for warning in analysis.warnings) or "- Nenhum aviso critico."
    return (
        f"Arquivo: {analysis.source_path.name}\n"
        f"Dimensoes: {analysis.width_mm:.2f} x {analysis.depth_mm:.2f} x {analysis.height_mm:.2f} mm\n"
        f"Volume aproximado: {analysis.volume_mm3:.2f} mm3\n"
        f"Area superficial: {analysis.surface_area_mm2:.2f} mm2\n"
        f"Triangulos: {analysis.triangle_count}\n"
        f"Componentes: {analysis.component_count}\n"
        f"Malha fechada: {'sim' if analysis.is_watertight else 'nao'}\n"
        f"Arestas nao-manifold: {analysis.non_manifold_edge_count}\n"
        f"Area de contato: {analysis.base_contact_area_mm2:.2f} mm2\n"
        f"Suportes provaveis: {'sim' if analysis.support_likely else 'nao'}\n"
        f"Cabe na Kobra S1: {'sim' if analysis.fits_printer else 'nao'}\n"
        f"Avisos:\n{warnings}"
    )


def _format_profile(profile) -> str:
    warnings = "\n".join(f"- {warning}" for warning in profile.warnings) or "- Nenhum aviso."
    return (
        "Perfil recomendado:\n"
        f"Material: {profile.material}\n"
        f"Bico/Mesa: {profile.nozzle_temp_c} C / {profile.bed_temp_c} C\n"
        f"Camada: {profile.layer_height_mm:.2f} mm\n"
        f"Paredes: {profile.walls}\n"
        f"Preenchimento: {profile.infill_percent}% {profile.infill_pattern}\n"
        f"Topo/fundo: {profile.top_bottom_layers} camadas\n"
        f"Velocidade base: {profile.speed_mm_s} mm/s\n"
        f"Brim: {'sim' if profile.brim else 'nao'}\n"
        f"Suportes: {'sim' if profile.supports else 'nao'}\n"
        f"Avisos finais:\n{warnings}"
    )


def run_app() -> None:
    MainWindow().mainloop()
