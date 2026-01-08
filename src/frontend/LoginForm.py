from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Header, Footer, Input, Button, Static, Label
from textual.validation import Validator, ValidationResult, Length, Function
from textual.reactive import reactive
from textual import events
import json
import os
from typing import Callable, Optional


class UsernameValidator(Validator):
    def validate(self, value: str) -> ValidationResult:
        if not value:
            return self.failure("Имя пользователя не может быть пустым")
        if len(value) < 3:
            return self.failure("Имя пользователя должно быть не менее 3 символов")
        if len(value) > 20:
            return self.failure("Имя пользователя должно быть не более 20 символов")
        return self.success()


class PasswordValidator(Validator):
    def validate(self, value: str) -> ValidationResult:
        if not value:
            return self.failure("Пароль не может быть пустым")
        if len(value) < 6:
            return self.failure("Пароль должен быть не менее 6 символов")
        if len(value) > 30:
            return self.failure("Пароль должен быть не более 30 символов")
        return self.success()


class LoginForm(Container):
    username = reactive("")
    password = reactive("")
    username_valid = reactive(False)
    password_valid = reactive(False)

    def __init__(
        self,
        on_login: Optional[Callable[[str, str], bool]] = None,
        on_register: Optional[Callable[[str, str], bool]] = None
    ):
        super().__init__()
        self.users_file = "users.json"
        self.on_login_callback = on_login
        self.on_register_callback = on_register

    def on_mount(self) -> None:
        self.update_button_styles()

    def compose(self) -> ComposeResult:
        with Vertical(classes="login-container"):
            yield Static("Вход в приложение", classes="title")

            with Vertical(classes="form-fields"):
                yield Label("Имя пользователя:")
                yield Input(
                    placeholder="Введите имя пользователя",
                    id="username",
                    validators=[UsernameValidator()]
                )

                yield Label("Пароль:")
                yield Input(
                    placeholder="Введите пароль",
                    password=True,
                    id="password",
                    validators=[PasswordValidator()]
                )

            with Vertical(classes="buttons"):
                yield Button("Войти", variant="primary", id="login-btn")
                yield Button("Зарегистрироваться", variant="default", id="register-btn")

            yield Static("", id="message", classes="message")

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "username":
            self.username = event.value
            if hasattr(event.validation_result, 'is_valid'):
                self.username_valid = event.validation_result.is_valid
        elif event.input.id == "password":
            self.password = event.value
            if hasattr(event.validation_result, 'is_valid'):
                self.password_valid = event.validation_result.is_valid

        message = self.query_one("#message", Static)
        message.update("")

        self.update_button_styles()

    def update_button_styles(self) -> None:
        login_btn = self.query_one("#login-btn", Button)
        register_btn = self.query_one("#register-btn", Button)

        login_enabled = self.username_valid and self.password_valid
        login_btn.disabled = not login_enabled

        register_enabled = self.username_valid and self.password_valid
        register_btn.disabled = not register_enabled

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "login-btn":
            self.login()
        elif event.button.id == "register-btn":
            self.register()

    def login(self) -> None:
        message = self.query_one("#message", Static)
        if not self.username or not self.password:
            message.update("[red]Заполните все поля[/red]")
            return

        success = False
        if self.on_login_callback:
            success = self.on_login_callback(self.username, self.password)

        if success:
            message.update("[green]Успешный вход![/green]")
            self.app.update_user_info_display()
            self.app.save_config(self.username, self.password)
            self.close_popup()
            self.app.showMainContainer()
        else:
            message.update("[red]Неверное имя пользователя или пароль.[/red]")

    def register(self) -> None:
        message = self.query_one("#message", Static)

        if not self.username_valid or not self.password_valid:
            message.update("[red]Исправьте ошибки в форме[/red]")
            return

        success = False

        if self.on_register_callback:
            success = self.on_register_callback(self.username, self.password)

        if success:
            message.update("[green]Аккаунт успешно создан[/green]")
            self.app.update_user_info_display()
            self.app.save_config(self.username, self.password)
            self.close_popup()
            self.app.showMainContainer()
        else:
            message.update("[red]Ошибка при регистрации[/red]")

    def on_key(self, event: events.Key) -> None:
        if event.key == "enter":
            active = self.app.focused
            if active and hasattr(active, 'id'):
                if active.id == "username":
                    self.query_one("#password", Input).focus()
                elif active.id == "password":
                    self.login()

    def close_popup(self) -> None:
        from ScreenPop import ScreenPop
        parent = self.parent
        while parent and not isinstance(parent, ScreenPop):
            parent = parent.parent

        if parent and isinstance(parent, ScreenPop):
            parent.pop()

