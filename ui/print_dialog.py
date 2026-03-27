import os

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.reactive import reactive
from textual.widgets import Button, Input, Label, Select

from cups_wrapper import get_printers, print_file


class PrintDialogView(Container):
    """View to select a file and send a print job."""

    selected_printer = reactive(None)

    def compose(self) -> ComposeResult:
        with Container(id="print-form"):
            yield Label("Print Document", id="print-header", classes="printer-title")

            with Horizontal(classes="form-row"):
                yield Label("Document Path:", classes="form-label")
                yield Input(
                    placeholder="/path/to/document.pdf",
                    id="file-input",
                    classes="form-input",
                )

            with Horizontal(classes="form-row"):
                yield Label("Printer:", classes="form-label")
                yield Select(
                    [],
                    id="printer-select",
                    prompt="Select Printer",
                    classes="form-input",
                )

            with Horizontal(classes="form-row"):
                yield Label("Copies:", classes="form-label")
                yield Input(
                    "1", id="copies-input", type="integer", classes="form-input"
                )

            with Horizontal(classes="form-row"):
                yield Label("Sides:", classes="form-label")
                yield Select(
                    [
                        ("Default", "default"),
                        ("One Sided", "one-sided"),
                        ("Two Sided (Long Edge)", "two-sided-long-edge"),
                        ("Two Sided (Short Edge)", "two-sided-short-edge"),
                    ],
                    id="sides-select",
                    value="default",
                    classes="form-input",
                )

            with Horizontal(classes="form-row"):
                yield Label("Media:", classes="form-label")
                yield Select(
                    [("Default", "default"), ("A4", "A4"), ("Letter", "Letter")],
                    id="media-select",
                    value="default",
                    classes="form-input",
                )

            yield Button("Print", id="print-button", variant="success")

    def on_mount(self) -> None:
        self.refresh_printers()

    def refresh_printers(self) -> None:
        printers = get_printers()
        select = self.query_one("#printer-select", Select)

        options = [(p["name"], p["name"]) for p in printers]
        select.set_options(options)

        if options:
            select.value = options[0][1]

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "print-button":
            self.submit_print_job()

    def submit_print_job(self) -> None:
        file_path = self.query_one("#file-input", Input).value.strip()
        printer = self.query_one("#printer-select", Select).value
        copies_str = self.query_one("#copies-input", Input).value
        sides = self.query_one("#sides-select", Select).value
        media = self.query_one("#media-select", Select).value

        if not file_path or not os.path.exists(file_path):
            self.app.notify("Error: File not found or empty path.", severity="error")
            return

        if not printer:
            self.app.notify("Error: No printer selected.", severity="error")
            return

        try:
            copies = int(copies_str)
        except ValueError:
            copies = 1

        # Optional args
        s_arg = sides if sides != "default" else None
        m_arg = media if media != "default" else None

        success, output = print_file(
            printer, file_path, copies=copies, sides=s_arg, media=m_arg
        )

        if success:
            self.app.notify(f"Successfully sent to {printer}", severity="information")
            self.query_one("#file-input", Input).value = ""
        else:
            self.app.notify(f"Failed to print: {output}", severity="error")
