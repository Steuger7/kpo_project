from textual.app import ComposeResult
from textual.widgets import Static
from textual.containers import Container, Vertical
from typing import Callable, Optional

class BookContainer(Container):
    DEFAULT_CSS = """
    BookContainer {
        width: 100%;
        height: 12;
        margin: 1;
        padding: 1;
        border: round $accent;
        background: $panel;
        layout: vertical;
    }

    BookContainer:focus {
        border: double $accent;
        background: $boost;
        outline: heavy $accent;
    }

    .book-title {
        text-style: bold;
        color: $text;
        margin-bottom: 1;
    }

    .book-author {
        color: $text-muted;
        margin-bottom: 1;
    }

    .book-year {
        color: $success;
    }

    .book-status_notAdded {
        color: $warning;
        text-style: italic;
        margin-top: 1;
    }

    .book-status_added {
        color: $success;
        text-style: italic;
        margin-top: 1;
    }
    """

    def __init__(self,
                 book: dict,
                 add_to_lib: Callable[[dict], None],
                 rem_in_lib: Callable[[dict], None],
                 is_added: bool = False,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.book = book
        self.add_to_lib = add_to_lib
        self.rem_in_lib = rem_in_lib
        self.is_added = is_added
        self.focus_handler = None
        self.can_focus = True

    def compose(self) -> ComposeResult:
        status_text = "Статус: Добавлена в библиотеку" if self.is_added else "Статус: Не добавлена"
        status_class = "book-status_added" if self.is_added else "book-status_notAdded"

        yield Container(
            Vertical(
                Static(self.book['title'], classes="book-title"),
                Static(f"Автор: {', '.join(self.book['author'])}", classes="book-author"),
                Static(f"Год: {self.book['year']}", classes="book-year"),
                Static(status_text, classes=status_class, id="book-status_notAdded"),
            ),
        )

    def set_focus_handler(self, handler: Callable) -> None:
        self.focus_handler = handler

    def on_focus(self) -> None:
        if self.focus_handler:
            self.focus_handler(self)

    def on_key(self, event):
        if event.key == "enter":
            self._handle_save()
            event.stop()
        return False

    def _handle_save(self) -> None:
        status_widget = self.query_one("#book-status_notAdded", Static)

        if not self.is_added:
            self.is_added = True
            status_widget.update("Статус: Добавлена в библиотеку")
            status_widget.remove_class("book-status_notAdded")
            status_widget.add_class("book-status_added")
            self.add_to_lib(self.book)
        else:
            self.is_added = False
            status_widget.update("Статус: Не добавлена")
            status_widget.remove_class("book-status_added")
            status_widget.add_class("book-status_notAdded")
            self.rem_in_lib(self.book)
