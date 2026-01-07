from textual.app import ComposeResult
from textual.widgets import Input
from typing import Callable, Optional
from textual.containers import Container


class InputSection(Container):
    DEFAULT_CSS = """
    InputSection {
        width: 100%;
        height: 50%;
        align: center middle;
    }

    .input-section {
        width: 80%;
        height: 5;
        border: round $accent;
        padding: 1;
        background: $panel;
        align: center middle;
    }

    .text-input {
        width: 100%;
        align: center middle;
        content-align: center middle;
        text-align: center;
    }
    """

    def __init__(
            self,
            section_title: str,
            input_placeholder: str,
            on_enter_callback: Optional[Callable[[str], None]] = None,
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.section_title = section_title
        self.input_placeholder = input_placeholder
        self.on_enter = on_enter_callback
        self.add_class("input-section")

    def compose(self) -> ComposeResult:
        yield Input(
            placeholder=self.input_placeholder,
            id="text-input",
            classes="text-input"
        )

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "text-input":
            self._handle_submit()

    def _handle_submit(self) -> None:
        input_widget = self.query_one("#text-input", Input)
        text = input_widget.value.strip()

        if self.on_enter:
            try:
                self.on_enter(text)
                input_widget.value = ""
                input_widget.focus()
            except Exception as e:
                pass
