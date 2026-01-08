from textual.app import ComposeResult
from textual.widgets import Static, Button
from textual.containers import Container
from textual.reactive import reactive
from typing import Callable


class UserInfoContainer(Container):
    username: reactive[str] = reactive("")
    books_count: reactive[int] = reactive(0)

    DEFAULT_CSS = """
    UserInfoContainer {
        width: 100%;
        height: auto;
        border: round $accent;
        background: $panel;
        layout: grid;
        grid-size: 3 1;
        grid-columns: 3fr 2fr 1fr;
        align: center middle;
    }

    .username {
        height: 100%;
        text-style: bold;
        color: $text;
        align: center middle;
        content-align: left middle;
    }

    .books-count {
        height: 100%;
        color: $text-muted;
        align: center middle;
        content-align: center middle;
    }

    .logout-button {
        width: auto;
        min-width: 8;
        background: $success;
        color: white;
        align: center middle;
        content-align: center middle;
        margin: 0;
        padding: 0;
    }
    """

    def __init__(
            self,
            username: str = "",
            books_count: int = 0,
            on_logout: Callable[[], None] = None,
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.username = username
        self.books_count = books_count
        self.on_logout = on_logout

    def compose(self) -> ComposeResult:
        yield Static(self.username, classes="username")
        yield Static(f"Книг: {self.books_count}", classes="books-count")
        yield Button(
            "login",
            id="logout-button",
            classes="logout-button",
            variant="error"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "logout-button":
            self._handle_logout()

    def _handle_logout(self) -> None:
        if self.on_logout:
            try:
                self.on_logout()
            except Exception as e:
                print(f"Ошибка при выходе: {e}")

    def update_username(self, new_username: str) -> None:
        self.username = new_username
        username_widget = self.query_one(".username", Static)
        username_widget.update(new_username)

    def update_books_count(self, new_count: int) -> None:
        self.books_count = new_count
        count_widget = self.query_one(".books-count", Static)
        count_widget.update(f"Книг: {new_count}")

    def update_user_info(self, username: str, books_count: int) -> None:
        self.username = username
        self.books_count = books_count

        username_widget = self.query_one(".username", Static)
        count_widget = self.query_one(".books-count", Static)

        username_widget.update(username)
        count_widget.update(f"Книг: {books_count}")
