from textual.app import ComposeResult
from textual.containers import Container, ScrollableContainer
from textual.reactive import reactive
from textual.widgets import Label, ListItem, ListView, Static

from cups_wrapper import get_default_printer, get_printer_options, get_printers


class PrintersView(Container):
    """View showing all installed printers and their options."""

    selected_printer = reactive(None)

    def compose(self) -> ComposeResult:
        with ScrollableContainer(id="printers-list"):
            yield ListView(id="printer-list-view")
        with ScrollableContainer(id="printer-details"):
            yield Static(
                "Select a printer to view details.", id="printer-detail-content"
            )

    def on_mount(self) -> None:
        self.refresh_printers()

    def refresh_printers(self) -> None:
        printers = get_printers()
        default_printer = get_default_printer()

        list_view = self.query_one("#printer-list-view", ListView)
        list_view.clear()

        for p in printers:
            name = p["name"]
            state = p["state"]
            is_default = name == default_printer

            label_text = f"[*] {name}" if is_default else name
            item = ListItem(Label(f"{label_text}\n[{state}]"), id=f"printer-{name}")
            list_view.append(item)

        if printers and not self.selected_printer:
            self.selected_printer = printers[0]["name"]
            # Highlight first
            list_view.index = 0

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        if event.item:
            # Extract printer name from the item ID (e.g. "printer-HP_LaserJet")
            p_name = event.item.id.replace("printer-", "")
            self.selected_printer = p_name
            self.update_details()

    def update_details(self) -> None:
        if not self.selected_printer:
            return

        detail_view = self.query_one("#printer-detail-content", Static)
        options = get_printer_options(self.selected_printer)

        content = f"## Printer: {self.selected_printer}\n\n"
        content += "### Configure Options\n"

        if not options:
            content += "No advanced options found or printer is offline.\n"
        else:
            for key, value in options.items():
                content += f"- **{key}**: {value}\n"

        detail_view.update(content)
