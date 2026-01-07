import json
import os
import requests

from textual.app import App, ComposeResult
from textual.widgets import Input, Static
from textual.containers import Vertical, Container, VerticalScroll
from textual.binding import Binding
from inputSection import InputSection
from booksContainer import BookContainer
from userContainer import UserInfoContainer
from LoginForm import LoginForm
from ScreenPop import ScreenPop


class MainGridContainer(Container):
    def compose(self) -> ComposeResult:
        with VerticalScroll(id="input-container"):
            yield InputSection(
                section_title="Первое поле ввода",
                input_placeholder="Поле для поиска в API...",
                on_enter_callback=self.app.search_books,
                id="section1"
            )
            yield InputSection(
                section_title="Второе поле ввода",
                input_placeholder="Поле для поиска в личной библиотеке...",
                on_enter_callback=self.app.search_personal_library,
                id="section2"
            )

        with VerticalScroll(id="right-pane"):
            books = []
            for number in range(len(books)):
                book_container = BookContainer(
                    books[number],
                    add_to_lib=self.app.add_book_to_library,
                    rem_in_lib=self.app.remove_book_from_library
                )
                self.app.book_containers.append(book_container)
                yield book_container

        yield UserInfoContainer(
            self.app.current_user,
            self.app.user_books_count,
            self.app.logout,
            id="user-info"
        )


class LibApp(App):
    CSS_PATH = "LibApp.tcss"

    BINDINGS = [
        Binding("f1", "focus_first", "Фокус 1", show=True),
        Binding("f2", "focus_second", "Фокус 2", show=True),
        Binding("ctrl+c", "quit", "Выход", show=True),
        Binding("f3", "toggle_panes", "Свернуть/развернуть панели", show=True),

        Binding("j", "scroll_down", "Вниз", show=True),
        Binding("k", "scroll_up", "Вверх", show=True),

        Binding("ctrl+down", "focus_next_book", "Следующая книга", show=True),
        Binding("ctrl+up", "focus_previous_book", "Предыдущая книга", show=True),
    ]

    def __init__(self):
        super().__init__()
        self.panes_collapsed = False
        self.current_user = "Гость"
        self.user_books_count = 0
        self.userid = None
        self.password = None
        self.last_focused_book = None
        self.book_containers = []
        self.main_container = None
        self.library_keys = {}

        self.auto_login_attempted = False
        self.config_file = "user_config.json"

        self.base_url = "http://localhost:8080"
        self.search_api = "http://openlibrary.org/search.json"

    def show_login_screen(self) -> None:
        login_form = LoginForm(
            on_login=self._handle_login_backend,
            on_register=self._handle_register_backend
        )
        screen_pop = ScreenPop(
            content_widget=login_form,
            on_close=self._on_login_close
        )

        self.hideMainContainer()

        self.app.push_screen(screen_pop)

    def _on_login_close(self) -> None:
        self.showMainContainer()
        if self.current_user != "Гость":
            self._update_library_keys_full()
            self.update_user_info_display()

    def compose(self) -> ComposeResult:
        self.main_container = MainGridContainer(id="main-grid-container")
        self.main_container.styles.display = "none"
        yield self.main_container

    def on_mount(self) -> None:
        for book_container in self.book_containers:
            book_container.set_focus_handler(self._on_book_focused)
        self.showMainContainer()

        if self.has_saved_user():
            self.attempt_auto_login()

    def search_personal_library(self, query: str) -> None:
        if not self.userid or not self.password:
            return
        try:
            url = f"{self.base_url}/lib"
            data = {
                "userid": self.userid,
                "password": self.password,
                "query": query
            }

            response = requests.post(url, json=data)
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    books_data = result.get('books', [])

                    self._update_library_keys(books_data)
                    self.display_books(books_data)
        except Exception as e:
            pass

    def search_books(self, query: str) -> None:
        if not query:
            return

        try:
            response = requests.get(self.search_api + "?q=" + query.strip().replace(" ", "+"))
            if response.status_code == 200:
                result = response.json()
                self.display_books(result['docs'])
        except Exception as e:
            pass

    def display_books(self, books_data: list) -> None:
        right_pane = self.query_one("#right-pane", VerticalScroll)

        for container in self.book_containers:
            container.remove()
        self.book_containers.clear()

        for book_data in books_data:
            book = {
                'title': book_data.get('title', 'Без названия'),
                'author': ', '.join(book_data.get('author_name', ['Неизвестен'])),
                'year': book_data.get('first_publish_year', 'Неизвестен'),
                'cover_i': book_data.get('cover_i', 0),
                'key': book_data.get('key', ''),
                'language': book_data.get('language', '')
            }

            book_container = BookContainer(
                book,
                add_to_lib=self.app.add_book_to_library,
                rem_in_lib=self.app.remove_book_from_library,
                is_added=self.is_book_in_library(book),
            )

            book_container.set_focus_handler(self.app._on_book_focused)
            self.app.book_containers.append(book_container)
            right_pane.mount(book_container)

    def is_book_in_library(self, book) -> bool:
        return book.get("key") in self.library_keys

    def _update_library_keys_full(self) -> None:
        try:
            url = f"{self.base_url}/lib"
            data = {
                "userid": self.userid,
                "password": self.password,
                "query": ""
            }

            response = requests.post(url, json=data)
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    books_data = result.get('books', [])
                    self._update_library_keys(books_data)
            self.update_user_info_display()
        except Exception as e:
            pass

    def _update_library_keys(self, books_data: list) -> None:
        self.library_keys.clear()
        
        for book in books_data:
            book_key = book.get('key')
            if book_key:
                self.library_keys[book_key] = True
        
        self.user_books_count = len(self.library_keys)
        self.update_user_info_display()


    def _handle_login_backend(self, username: str, password: str) -> bool:
        try:
            url = f"{self.base_url}/login"
            data = {
                "username": username,
                "password": password
            }
            response = requests.post(url, json=data)
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    self.current_user = username
                    self.userid = result.get('userid')
                    self.password = password

                    return True
            return False
        except Exception as e:
            return False

    def _handle_register_backend(self, username: str, password: str) -> bool:
        try:
            url = f"{self.base_url}/register"
            data = {
                "username": username,
                "password": password
            }

            response = requests.post(url, json=data)
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    self.current_user = username
                    self.userid = result.get('userid')
                    self.password = password

                    return True
            return False
        except Exception as e:
            return False


    def has_saved_user(self) -> bool:
        return os.path.exists(self.config_file)

    def load_config(self):
        if not os.path.exists(self.config_file):
            return None
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            return None

    def save_config(self, username: str, password: str) -> None:
        config = {
            "username": username,
            "password": password
        }
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            pass

    def clear_config(self) -> None:
        if os.path.exists(self.config_file):
            try:
                os.remove(self.config_file)
            except Exception as e:
                pass

    def get_saved_credentials(self):
        config = self.load_config()
        if config:
            username = config.get("username")
            password = config.get("password")
            if username and password:
                return username, password
        return None

    def attempt_auto_login(self) -> None:
        self.auto_login_attempted = True
        credentials = self.get_saved_credentials()
        success = False
        if credentials:
            username, saved_password = credentials
            success = self._handle_login_backend(username, saved_password)
        if success:
            self.curremr_user = username
            self.password = saved_password
            self._update_library_keys_full()
        self.showMainContainer()
        self.update_user_info_display()


    def _on_book_focused(self, book_container: BookContainer) -> None:
        self.last_focused_book = book_container

    def is_focus_on_books(self) -> bool:
        focused = self.focused
        if focused and isinstance(focused, BookContainer):
            return True
        return False

    def action_focus_next_book(self) -> None:
        if not self.book_containers:
            return

        if not self.is_focus_on_books():
            if self.last_focused_book and self.last_focused_book in self.book_containers:
                self.last_focused_book.focus()
            else:
                self.book_containers[0].focus()
        else:
            current_index = self.get_current_book_index()
            next_index = (current_index + 1) % len(self.book_containers)
            self.book_containers[next_index].focus()

    def action_focus_previous_book(self) -> None:
        if not self.book_containers:
            return

        if not self.is_focus_on_books():
            if self.last_focused_book and self.last_focused_book in self.book_containers:
                self.last_focused_book.focus()
            else:
                self.book_containers[0].focus()
        else:
            current_index = self.get_current_book_index()
            prev_index = (current_index - 1) % len(self.book_containers)
            self.book_containers[prev_index].focus()

    def get_current_book_index(self) -> int:
        if self.is_focus_on_books():
            return self.book_containers.index(self.focused)
        elif self.last_focused_book and self.last_focused_book in self.book_containers:
            return self.book_containers.index(self.last_focused_book)
        return 0

    def action_scroll_down(self) -> None:
        right_pane = self.query_one("#right-pane", VerticalScroll)
        right_pane.scroll_down()

    def action_scroll_up(self) -> None:
        right_pane = self.query_one("#right-pane", VerticalScroll)
        right_pane.scroll_up()

    def action_focus_first(self) -> None:
        section1 = self.query_one("#section1", InputSection)
        section1.query_one("#text-input", Input).focus()

    def action_focus_second(self) -> None:
        section2 = self.query_one("#section2", InputSection)
        section2.query_one("#text-input", Input).focus()

    def action_toggle_panes(self) -> None:
        input_container = self.query_one("#input-container", VerticalScroll)
        right_pane = self.query_one("#right-pane", VerticalScroll)

        self.panes_collapsed = not self.panes_collapsed

        if self.panes_collapsed:
            input_container.display = False
            right_pane.styles.column_span = 2
            right_pane.styles.row_span = 3
        else:
            input_container.display = True
            right_pane.styles.column_span = 1
            right_pane.styles.row_span = 2

    def update_user_info_display(self) -> None:
        try:
            user_info_container = self.query_one("#user-info", UserInfoContainer)
            user_info_container.update_user_info(self.current_user, self.user_books_count)
        except Exception as e:
            pass

    def logout(self) -> None:
        self.clear_config()
        self.current_user = "Гость"
        self.user_books_count = 0
        self.userid = None
        self.password = None
        self.update_user_info_display()

        self.hideMainContainer()
        self.show_login_screen()

    def increment_books_count(self) -> None:
        self.user_books_count += 1
        self.update_user_info_display()

    def decrement_books_count(self) -> None:
        if self.user_books_count > 0:
            self.user_books_count -= 1
            self.update_user_info_display()

    def set_books_count(self, count: int) -> None:
        self.user_books_count = count
        self.update_user_info_display()


    def add_book_to_library(self, book: dict) -> bool:
        if not self.userid or not self.password:
            return False

        try:
            url = f"{self.base_url}/lib/addbook"
            data = {
                "userid": self.userid,
                "password": self.password,
                "cover_i": book.get('cover_i', 0),
                "first_year_publish": book.get('year', 0),
                "key": book.get('key', ''),
                "language": book.get('language', 'ru'),
                "title": book.get('title', '')
            }

            response = requests.post(url, json=data, timeout=10)

            if response.status_code == 200:
                result = response.json()
                success = result.get('success', False)

                if success:
                    self._update_library_keys_full()
                    self.update_user_info_display()
                    return True
                else:
                    return False
            else:
                return False

        except Exception as e:
            return False

    def remove_book_from_library(self, book: dict) -> bool:
        try:
            url = f"{self.base_url}/lib/removebook"
            data = {
                "userid": self.userid,
                "password": self.password,
                "key": book.get('key', '')
            }
            response = requests.post(url, json=data, timeout=10)

            if response.status_code == 200:
                result = response.json()
                success = result.get('success', False)
                if success:
                    self._update_library_keys_full()
                    self.update_user_info_display()
                    return True
                else:
                    return False
            else:
                return False

        except Exception as e:
            return False


    def hideMainContainer(self):
        if self.main_container:
            self.main_container.display = False

    def showMainContainer(self):
        if self.main_container:
            self.main_container.display = True
            self.main_container.styles.display = "block"
            self.action_focus_first()


if __name__ == "__main__":
    app = LibApp()
    app.run()
