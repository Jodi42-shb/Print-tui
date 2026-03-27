from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.reactive import reactive
from textual.widgets import Button, DataTable

from cups_wrapper import cancel_job, get_jobs


class JobsView(Container):
    """View showing active print jobs."""

    selected_job_id = reactive(None)

    def compose(self) -> ComposeResult:
        yield DataTable(id="jobs-table", classes="jobs-table")
        with Horizontal(id="jobs-controls"):
            yield Button(
                "Cancel Selected Job",
                id="cancel-job-button",
                variant="error",
                disabled=True,
            )
            yield Button("Refresh", id="refresh-jobs-button", variant="primary")

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.add_columns("Job ID", "User", "Size", "Time")
        self.refresh_jobs()

    def refresh_jobs(self) -> None:
        jobs = get_jobs()
        table = self.query_one(DataTable)
        table.clear()

        for job in jobs:
            table.add_row(
                job["id"], job["user"], job["size"], job["time"], key=job["id"]
            )

        self.selected_job_id = None
        self.query_one("#cancel-job-button", Button).disabled = True

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        self.selected_job_id = event.row_key.value
        self.query_one("#cancel-job-button", Button).disabled = False

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "refresh-jobs-button":
            self.refresh_jobs()
        elif event.button.id == "cancel-job-button":
            if self.selected_job_id:
                success, output = cancel_job(self.selected_job_id)
                if success:
                    self.app.notify(f"Cancelled job {self.selected_job_id}")
                else:
                    self.app.notify(f"Failed to cancel: {output}", severity="error")
                self.refresh_jobs()
