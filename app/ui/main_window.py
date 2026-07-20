from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from app.domain.material import MATERIALS
from app.domain.slicing_profile import UserChoices
from app.services.config_service import load_json_config, save_json_config
from app.services.profile_engine import (
    ENVIRONMENTS,
    PRIORITIES,
    PURPOSES,
    QUALITY_RULES,
    STRENGTH_RULES,
    STRESS_DIRECTIONS,
    build_profile,
)
from app.services.project_export_service import ProjectExportError, export_recommended_3mf
from app.services.report_service import build_summary, save_summary
from app.services.model_import_service import ModelImportError, analyze_model
from app.services.auto_slice_service import AutoSliceError, generate_gcode
from app.services.slicer_service import SlicerServiceError, open_project, validate_slicer_path


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
        self.purpose = tk.StringVar(value="uso comum")
        self.environment = tk.StringVar(value="interno")
        self.heat_exposure = tk.BooleanVar(value=False)
        self.needs_flexibility = tk.BooleanVar(value=False)
        self.stress_direction = tk.StringVar(value="nao informado")
        self.copies = tk.IntVar(value=1)
        self.nozzle = tk.StringVar(value="0.4")
        self.custom_infill_enabled = tk.BooleanVar(value=False)
        self.custom_infill_percent = tk.IntVar(value=15)
        self.filament_price_per_kg = tk.StringVar(value="")
        self.temperature_calibration = tk.BooleanVar(value=False)
        self.flow_calibration = tk.BooleanVar(value=False)
        self.pressure_advance_calibration = tk.BooleanVar(value=False)
        self.supports_allowed = tk.BooleanVar(value=True)
        settings = load_json_config("app_settings.json")
        self.slicer_path = tk.StringVar(value=settings.get("slicer_path", ""))
        self.output_dir = tk.StringVar(value=settings.get("default_output_dir", "exports"))
        self.auto_open_slicer = tk.BooleanVar(value=bool(settings.get("auto_open_slicer_after_export", False)))

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
        self._combo(form, "Prioridade", self.priority, PRIORITIES)
        self._combo(form, "Finalidade", self.purpose, PURPOSES)
        self._combo(form, "Ambiente", self.environment, ENVIRONMENTS)
        self._combo(form, "Esforco", self.stress_direction, STRESS_DIRECTIONS)
        numeric = ttk.Frame(form)
        numeric.pack(fill=tk.X, pady=3)
        ttk.Label(numeric, text="Copias", width=14).pack(side=tk.LEFT)
        ttk.Spinbox(numeric, from_=1, to=99, textvariable=self.copies, width=8).pack(side=tk.LEFT)
        ttk.Label(numeric, text="Bico", width=8).pack(side=tk.LEFT, padx=(12, 0))
        ttk.Combobox(numeric, textvariable=self.nozzle, values=["0.4"], state="readonly", width=8).pack(side=tk.LEFT)
        ttk.Label(numeric, text="R$/kg", width=8).pack(side=tk.LEFT, padx=(12, 0))
        ttk.Entry(numeric, textvariable=self.filament_price_per_kg, width=10).pack(side=tk.LEFT)
        infill_row = ttk.Frame(form)
        infill_row.pack(fill=tk.X, pady=3)
        ttk.Checkbutton(infill_row, text="Preenchimento customizado (%)", variable=self.custom_infill_enabled).pack(
            side=tk.LEFT
        )
        ttk.Spinbox(infill_row, from_=0, to=100, textvariable=self.custom_infill_percent, width=8).pack(
            side=tk.LEFT, padx=(8, 0)
        )
        ttk.Checkbutton(form, text="Permitir suportes quando recomendados", variable=self.supports_allowed).pack(
            anchor=tk.W, pady=(6, 0)
        )
        ttk.Checkbutton(form, text="Exposto a calor/sol", variable=self.heat_exposure).pack(anchor=tk.W)
        ttk.Checkbutton(form, text="Precisa ser flexivel", variable=self.needs_flexibility).pack(anchor=tk.W)
        calib = ttk.LabelFrame(form, text="Assistentes de calibracao", padding=8)
        calib.pack(fill=tk.X, pady=(6, 0))
        ttk.Checkbutton(calib, text="Temperatura", variable=self.temperature_calibration).pack(side=tk.LEFT)
        ttk.Checkbutton(calib, text="Flow ratio", variable=self.flow_calibration).pack(side=tk.LEFT, padx=(12, 0))
        ttk.Checkbutton(calib, text="Pressure advance", variable=self.pressure_advance_calibration).pack(
            side=tk.LEFT, padx=(12, 0)
        )

        self.tabs = ttk.Notebook(root)
        self.tabs.pack(fill=tk.BOTH, expand=True)
        self.analysis_view = self._text_tab("Analise")
        self.profile_view = self._text_tab("Perfil")
        self.error_view = self._text_tab("Erros")
        self.settings_view = self._settings_tab()
        self._set_text(self.analysis_view, "Selecione um arquivo STL ou 3MF para comecar.")

        actions = ttk.Frame(root)
        actions.pack(anchor=tk.E, pady=(12, 0))
        ttk.Button(actions, text="Gerar resumo JSON", command=self._generate_summary).pack(side=tk.LEFT)
        ttk.Button(actions, text="Exportar 3MF com perfil", command=self._export_project).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(actions, text="Abrir no slicer", command=self._open_project_in_slicer).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(actions, text="Gerar G-code", command=self._generate_gcode).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(actions, text="Salvar configuracoes", command=self._save_settings).pack(side=tk.LEFT, padx=(8, 0))

    def _combo(self, parent: ttk.Frame, label: str, variable: tk.StringVar, values: list[str]) -> None:
        row = ttk.Frame(parent)
        row.pack(fill=tk.X, pady=3)
        ttk.Label(row, text=label, width=14).pack(side=tk.LEFT)
        ttk.Combobox(row, textvariable=variable, values=values, state="readonly").pack(
            side=tk.LEFT, fill=tk.X, expand=True
        )

    def _text_tab(self, title: str) -> tk.Text:
        frame = ttk.Frame(self.tabs, padding=8)
        self.tabs.add(frame, text=title)
        text = tk.Text(frame, wrap=tk.WORD, height=12)
        text.pack(fill=tk.BOTH, expand=True)
        return text

    def _settings_tab(self) -> ttk.Frame:
        frame = ttk.Frame(self.tabs, padding=12)
        self.tabs.add(frame, text="Configuracoes")
        row = ttk.Frame(frame)
        row.pack(fill=tk.X, pady=4)
        ttk.Label(row, text="Fatiador", width=14).pack(side=tk.LEFT)
        ttk.Entry(row, textvariable=self.slicer_path).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(row, text="Procurar", command=self._select_slicer).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(row, text="Validar", command=self._validate_slicer).pack(side=tk.LEFT, padx=(8, 0))
        row = ttk.Frame(frame)
        row.pack(fill=tk.X, pady=4)
        ttk.Label(row, text="Saida padrao", width=14).pack(side=tk.LEFT)
        ttk.Entry(row, textvariable=self.output_dir).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Checkbutton(frame, text="Abrir slicer apos exportar", variable=self.auto_open_slicer).pack(anchor=tk.W, pady=6)
        return frame

    def _select_file(self) -> None:
        path = filedialog.askopenfilename(
            title="Selecione um STL ou 3MF",
            filetypes=[("Modelos 3D", "*.stl *.3mf"), ("STL", "*.stl"), ("3MF", "*.3mf"), ("Todos os arquivos", "*.*")],
        )
        if path:
            self.selected_file.set(path)
            self._refresh_analysis()

    def _select_slicer(self) -> None:
        path = filedialog.askopenfilename(
            title="Selecione o executavel do slicer",
            filetypes=[("Executavel", "*.exe"), ("Todos os arquivos", "*.*")],
        )
        if path:
            self.slicer_path.set(path)

    def _refresh_analysis(self) -> None:
        try:
            analysis = analyze_model(self.selected_file.get())
        except ModelImportError as exc:
            self._show_error(str(exc))
            return

        self._set_text(self.analysis_view, _format_analysis(analysis))
        self._set_text(self.profile_view, "Preencha as opcoes e gere o resumo ou exporte o 3MF.")
        self._set_text(self.error_view, _format_issues(analysis))

    def _generate_summary(self) -> None:
        source = self.selected_file.get()
        if not source:
            messagebox.showerror("Arquivo obrigatorio", "Selecione um arquivo STL ou 3MF antes de gerar o resumo.")
            return

        try:
            analysis, choices, profile = self._current_result()
            summary = build_summary(analysis, choices, profile)
            output_path = save_summary(summary, Path("logs"))
        except (ModelImportError, ValueError) as exc:
            messagebox.showerror("Nao foi possivel gerar", str(exc))
            return

        self._set_text(self.analysis_view, _format_analysis(analysis))
        self._set_text(self.profile_view, _format_profile(profile))
        self._set_text(self.error_view, _format_issues(analysis, profile))
        messagebox.showinfo("Resumo gerado", f"Resumo salvo em:\n{output_path}")

    def _export_project(self) -> None:
        source = self.selected_file.get()
        if not source:
            messagebox.showerror("Arquivo obrigatorio", "Selecione um arquivo STL ou 3MF antes de exportar.")
            return

        default_name = f"{Path(source).stem}_kobra_s1_recomendado.3mf"
        output = filedialog.asksaveasfilename(
            title="Salvar 3MF com perfil recomendado",
            defaultextension=".3mf",
            initialfile=default_name,
            filetypes=[("Projeto 3MF", "*.3mf")],
        )
        if not output:
            return

        try:
            analysis, choices, profile = self._current_result()
            output_path = export_recommended_3mf(source, output, analysis, choices, profile)
        except (ModelImportError, ProjectExportError, ValueError) as exc:
            messagebox.showerror("Nao foi possivel exportar", str(exc))
            return

        self._set_text(self.analysis_view, _format_analysis(analysis))
        self._set_text(self.profile_view, _format_profile(profile))
        self._set_text(self.error_view, _format_issues(analysis, profile))
        messagebox.showinfo(
            "3MF exportado",
            "Projeto salvo com o perfil recomendado.\n\n"
            "Abra o arquivo no slicer e confira a pre-visualizacao antes de imprimir:\n"
            f"{output_path}",
        )
        self._open_slicer_if_requested(output_path)

    def _open_project_in_slicer(self) -> None:
        source = self.selected_file.get()
        if not source:
            messagebox.showerror("Arquivo obrigatorio", "Selecione um arquivo STL ou 3MF antes de abrir no slicer.")
            return
        try:
            analysis, choices, profile = self._current_result()
            output_path = Path(self.output_dir.get() or "exports") / f"{Path(source).stem}_kobra_s1_recomendado.3mf"
            output_path = export_recommended_3mf(source, output_path, analysis, choices, profile)
            open_project(self.slicer_path.get(), output_path)
        except (ModelImportError, ProjectExportError, SlicerServiceError, ValueError) as exc:
            self._show_error(str(exc))
            return
        messagebox.showinfo("Slicer", f"Projeto aberto no slicer:\n{output_path}")

    def _generate_gcode(self) -> None:
        source = self.selected_file.get()
        if not source:
            messagebox.showerror("Arquivo obrigatorio", "Selecione um arquivo STL ou 3MF antes de gerar G-code.")
            return
        try:
            analysis, choices, profile = self._current_result()
            result = generate_gcode(
                self.slicer_path.get(),
                source,
                self.output_dir.get() or "exports",
                analysis,
                choices,
                profile,
            )
        except (ModelImportError, AutoSliceError, ProjectExportError, ValueError) as exc:
            self._show_error(str(exc))
            return
        self._set_text(self.error_view, _format_slice_result(result))
        if result.success:
            messagebox.showinfo("G-code gerado", f"G-code validado:\n{result.gcode_path}")
        else:
            messagebox.showwarning(
                "G-code nao gerado",
                "O slicer nao retornou um G-code valido. Veja a aba Erros para detalhes.",
            )

    def _current_result(self):
        analysis = analyze_model(self.selected_file.get())
        try:
            copies = int(self.copies.get())
            nozzle = float(self.nozzle.get())
            custom_infill = int(self.custom_infill_percent.get())
            price = _optional_float(self.filament_price_per_kg.get())
        except (TypeError, ValueError) as exc:
            raise ValueError("Copias, bico, preenchimento e preco devem ser numeros validos.") from exc
        choices = UserChoices(
            material=self.material.get(),
            strength=self.strength.get(),
            quality=self.quality.get(),
            priority=self.priority.get(),
            supports_allowed=self.supports_allowed.get(),
            purpose=self.purpose.get(),
            environment=self.environment.get(),
            heat_exposure=self.heat_exposure.get(),
            needs_flexibility=self.needs_flexibility.get(),
            stress_direction=self.stress_direction.get(),
            copies=copies,
            nozzle_diameter_mm=nozzle,
            custom_infill_enabled=self.custom_infill_enabled.get(),
            custom_infill_percent=custom_infill,
            filament_price_per_kg=price,
            enable_temperature_calibration=self.temperature_calibration.get(),
            enable_flow_calibration=self.flow_calibration.get(),
            enable_pressure_advance_calibration=self.pressure_advance_calibration.get(),
        )
        profile = build_profile(choices, analysis)
        return analysis, choices, profile

    def _save_settings(self) -> None:
        save_json_config(
            "app_settings.json",
            {
                "slicer_path": self.slicer_path.get(),
                "default_output_dir": self.output_dir.get() or "exports",
                "auto_open_slicer_after_export": self.auto_open_slicer.get(),
            },
        )
        messagebox.showinfo("Configuracoes", "Configuracoes salvas.")

    def _validate_slicer(self) -> None:
        try:
            installation = validate_slicer_path(self.slicer_path.get())
        except SlicerServiceError as exc:
            self._show_error(str(exc))
            return
        self._set_text(
            self.error_view,
            "Slicer validado:\n"
            f"Nome: {installation.name}\n"
            f"Versao: {installation.version or 'nao identificada'}\n"
            f"Executavel: {installation.executable}",
        )
        messagebox.showinfo("Slicer", "Slicer validado com sucesso.")

    def _set_text(self, widget: tk.Text, content: str) -> None:
        widget.configure(state=tk.NORMAL)
        widget.delete("1.0", tk.END)
        widget.insert(tk.END, content)
        widget.configure(state=tk.DISABLED)

    def _show_error(self, content: str) -> None:
        self._set_text(self.error_view, content)
        self.tabs.select(self.error_view.master)
        messagebox.showerror("Erro", content)

    def _open_slicer_if_requested(self, output_path: Path) -> None:
        if not self.auto_open_slicer.get():
            return
        try:
            open_project(self.slicer_path.get(), output_path)
        except SlicerServiceError as exc:
            self._show_error(str(exc))


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
    reasons = "\n".join(f"- {reason}" for reason in profile.decision_reasons) or "- Sem justificativas."
    weight = f"{profile.estimated_weight_g:.2f} g" if profile.estimated_weight_g is not None else "indisponivel"
    total_weight = (
        f"{profile.estimated_total_weight_g:.2f} g" if profile.estimated_total_weight_g is not None else "indisponivel"
    )
    cost = f"R$ {profile.estimated_cost:.2f}" if profile.estimated_cost is not None else "indisponivel"
    calibration = _format_calibration(profile)
    comparison = _format_strength_consumption(profile)
    return (
        "Perfil recomendado:\n"
        f"Material: {profile.material}\n"
        f"Bico/Mesa: {profile.nozzle_temp_c} C / {profile.bed_temp_c} C\n"
        f"Camada: {profile.layer_height_mm:.2f} mm\n"
        f"Paredes: {profile.walls}\n"
        f"Preenchimento: {profile.infill_percent}% {profile.infill_pattern}\n"
        f"Topo/fundo: {profile.top_bottom_layers} camadas\n"
        f"Velocidade base: {profile.speed_mm_s} mm/s\n"
        f"Aderencia: {profile.adhesion_type}\n"
        f"Suportes: {'sim' if profile.supports else 'nao'} ({profile.support_style})\n"
        f"Peso estimado por peca: {weight}\n"
        f"Peso total estimado: {total_weight}\n"
        f"Custo estimado: {cost}\n"
        f"{profile.estimated_cost_note}\n"
        f"\nAssistentes de calibracao:\n{calibration}\n"
        f"\nComparacao resistencia x consumo:\n{comparison}\n"
        f"Justificativas:\n{reasons}\n"
        f"Avisos finais:\n{warnings}"
    )


def _format_issues(analysis, profile=None) -> str:
    issue_lines = [
        f"- [{issue.severity}] {issue.code}: {issue.message}"
        for issue in analysis.issues
    ]
    if profile is not None:
        issue_lines.extend(f"- [perfil] {warning}" for warning in profile.warnings)
    return "\n".join(issue_lines) or "Nenhum erro ou aviso relevante."


def _format_slice_result(result) -> str:
    lines = [
        "Resultado do fatiamento automatico:",
        f"Projeto: {result.project_path}",
        f"Saida: {result.output_dir}",
        f"Exit code: {result.command_result.exit_code}",
        f"G-code: {result.gcode_path or 'nao gerado'}",
    ]
    if result.validation is not None:
        lines.append(f"G-code valido: {'sim' if result.validation.is_valid else 'nao'}")
        if result.validation.bounds_mm is not None:
            lines.append(f"Limites de movimento: {result.validation.bounds_mm}")
        if result.validation.estimated_time:
            lines.append(f"Tempo estimado: {result.validation.estimated_time}")
        if result.validation.filament_used:
            lines.append(f"Filamento: {result.validation.filament_used}")
        lines.extend(f"- {warning}" for warning in result.validation.warnings)
    if result.command_result.stdout.strip():
        lines.extend(["", "STDOUT:", result.command_result.stdout.strip()])
    if result.command_result.stderr.strip():
        lines.extend(["", "STDERR:", result.command_result.stderr.strip()])
    diagnosis = _friendly_slice_diagnosis(result)
    if diagnosis:
        lines.extend(["", "Diagnostico:", diagnosis])
    if result.command_result.generated_files:
        lines.append("")
        lines.append("Arquivos gerados:")
        lines.extend(f"- {path}" for path in result.command_result.generated_files)
    return "\n".join(lines)


def _friendly_slice_diagnosis(result) -> str:
    combined = f"{result.command_result.stdout}\n{result.command_result.stderr}".lower()
    if result.gcode_path is None and "crash reporter" in combined:
        return (
            "O Anycubic Slicer Next falhou durante o fatiamento automatico deste modelo. "
            "O projeto 3MF foi gerado, mas nenhum G-code valido saiu do CLI. "
            "Use 'Abrir no slicer' e faca o fatiamento manual pela interface grafica."
        )
    if result.gcode_path is None and "no such file" in combined:
        return (
            "O slicer nao conseguiu encontrar um arquivo necessario durante a execucao por linha de comando. "
            "Tente exportar o 3MF e abrir manualmente no slicer."
        )
    if result.validation is not None and not result.validation.is_valid:
        return "O G-code foi criado, mas falhou na validacao de seguranca do assistente."
    return ""


def _optional_float(value: str) -> float | None:
    cleaned = value.strip().replace(",", ".")
    if not cleaned:
        return None
    return float(cleaned)


def _format_calibration(profile) -> str:
    plan = profile.calibration_plan
    lines: list[str] = []
    if plan.temperature_tower:
        lines.append("Temperatura: " + ", ".join(f"{temp} C" for temp in plan.temperature_tower))
    if plan.flow_ratio_steps:
        lines.append("Flow ratio: " + ", ".join(f"{step:.2f}" for step in plan.flow_ratio_steps))
    if plan.pressure_advance_steps:
        lines.append("Pressure advance: " + ", ".join(f"{step:.2f}" for step in plan.pressure_advance_steps))
    lines.extend(f"- {note}" for note in plan.notes)
    return "\n".join(lines)


def _format_strength_consumption(profile) -> str:
    lines = []
    for option in profile.strength_consumption_options:
        weight = f"{option.estimated_weight_g:.2f} g" if option.estimated_weight_g is not None else "?"
        cost = f"R$ {option.estimated_cost:.2f}" if option.estimated_cost is not None else "custo indisponivel"
        lines.append(
            f"- {option.strength}: {option.walls} paredes, {option.infill_percent}% infill, {weight}, {cost} ({option.note})"
        )
    return "\n".join(lines)


def run_app() -> None:
    MainWindow().mainloop()
