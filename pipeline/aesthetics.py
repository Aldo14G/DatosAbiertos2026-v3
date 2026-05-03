"""
Módulo de Estética UI/UX para el CLI — Datos Abiertos NL.
Implementa el sistema de diseño: Senior Data-Driven Dashboard.
Colores: Blue (#1E40AF), Amber (#F59E0B), Background (#F8FAFC).
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.theme import Theme
from rich.text import Text
from rich.columns import Columns
from typing import Dict, Any, List

# Definición del Tema basado en el Design System
custom_theme = Theme({
    "info": "bold #3B82F6",      # Secondary Blue
    "primary": "bold #1E40AF",   # Primary Blue
    "warning": "bold #F59E0B",   # Amber
    "danger": "bold red",
    "success": "bold green",
    "highlight": "#F59E0B",      # Amber
    "data": "bold cyan",
    "muted": "#94A3B8"           # Slate-400
})

console = Console(theme=custom_theme)

class DataAesthetics:
    @staticmethod
    def print_header(title: str, subtitle: str = ""):
        grid = Table.grid(expand=True)
        grid.add_column(justify="left")
        grid.add_column(justify="right")
        
        header_text = Text.assemble(
            (f" {title} ", "white on #1E40AF"),
            (f" {subtitle} " if subtitle else "", "bold #1E40AF")
        )
        
        console.print("\n")
        console.print(Panel(header_text, border_style="#1E40AF", expand=True))

    @staticmethod
    def print_kpi_grid(stats: Dict[str, Any]):
        """Crea un layout tipo 'Bento Grid' para KPIs."""
        panels = []
        for label, value in stats.items():
            content = Text.assemble(
                (f"{label}\n", "muted"),
                (f"{value}", "primary")
            )
            panels.append(Panel(content, border_style="#3B82F6", padding=(1, 2)))
        
        console.print(Columns(panels, equal=True, expand=True))

    @staticmethod
    def create_quality_table(title: str) -> Table:
        table = Table(title=title, border_style="#1E40AF", header_style="bold #1E40AF", show_header=True)
        table.add_column("Dataset", style="white", no_wrap=True)
        table.add_column("Org", style="muted")
        table.add_column("Score", justify="right")
        table.add_column("Status", justify="center")
        return table

    @staticmethod
    def get_status_tag(score: float) -> str:
        if score >= 90: return "[bold green]Excelente[/bold green]"
        if score >= 80: return "[bold #3B82F6]Bueno[/bold #3B82F6]"
        if score >= 70: return "[bold #F59E0B]Aceptable[/bold #F59E0B]"
        return "[bold red]Crítico[/bold red]"

    @staticmethod
    def print_log(message: str, level: str = "info"):
        icon = "ℹ️"
        if level == "success": icon = "✅"
        elif level == "warning": icon = "⚠️"
        elif level == "error": icon = "❌"
        
        console.print(f"[{level}]{icon} {message}[/{level}]")

def get_progress():
    return Progress(
        SpinnerColumn(spinner_name="dots"),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=None, complete_style="#1E40AF", finished_style="green"),
        TaskProgressColumn(),
        console=console
    )
