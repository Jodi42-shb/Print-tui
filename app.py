from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Footer, Header, TabbedContent, TabPane

from ui.jobs import JobsView
from ui.print_dialog import PrintDialogView
from ui.printers import PrintersView


class PrintTUIApp(App):
    """A Textual App to manage printers, print jobs, and print files."""

    CSS_PATH = "print_tui.tcss"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("d", "toggle_dark", "Toggle Dark Mode"),
        ("r", "refresh_data", "Refresh Data"),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header(show_clock=True)
        with Container(id="main-container"):
            with TabbedContent(initial="printers-tab"):
                with TabPane("Printers", id="printers-tab"):
                    yield PrintersView()
                with TabPane("Jobs", id="jobs-tab"):
                    yield JobsView()
                with TabPane("Print Document", id="print-tab"):
                    yield PrintDialogView()
        yield Footer()

    def action_refresh_data(self) -> None:
        """Refresh data in active tab (e.g. refresh printers or jobs)"""
        try:
            printers = self.query(PrintersView)
            if printers:
                printers.first().refresh_printers()
        except Exception:
            pass

        try:
            jobs = self.query(JobsView)
            if jobs:
                jobs.first().refresh_jobs()
        except Exception:
            pass

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark
