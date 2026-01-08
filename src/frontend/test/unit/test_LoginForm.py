import pytest
from unittest.mock import Mock, patch, PropertyMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try:
    from LoginForm import LoginForm, UsernameValidator, PasswordValidator
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    raise


class TestValidators:
    
    def test_username_validator(self):
        validator = UsernameValidator()
        
        assert validator.validate("user").is_valid
        assert validator.validate("user123").is_valid
        assert validator.validate("a" * 20).is_valid  # граничное значение
        
        result = validator.validate("")
        assert not result.is_valid
        failure_text = " ".join(str(desc) for desc in result.failure_descriptions)
        assert "не может быть пустым" in failure_text.lower()
        
        result = validator.validate("ab")
        assert not result.is_valid
        failure_text = " ".join(str(desc) for desc in result.failure_descriptions)
        assert "не менее 3 символов" in failure_text.lower()
        
        result = validator.validate("a" * 21)
        assert not result.is_valid
        failure_text = " ".join(str(desc) for desc in result.failure_descriptions)
        assert "не более 20 символов" in failure_text.lower()
    
    def test_password_validator(self):
        validator = PasswordValidator()
        
        assert validator.validate("pass123").is_valid
        assert validator.validate("password").is_valid
        assert validator.validate("a" * 30).is_valid  # граничное значение
        
        result = validator.validate("")
        assert not result.is_valid
        failure_text = " ".join(str(desc) for desc in result.failure_descriptions)
        assert "не может быть пустым" in failure_text.lower()
        
        result = validator.validate("12345")
        assert not result.is_valid
        failure_text = " ".join(str(desc) for desc in result.failure_descriptions)
        assert "не менее 6 символов" in failure_text.lower()
        
        result = validator.validate("a" * 31)
        assert not result.is_valid
        failure_text = " ".join(str(desc) for desc in result.failure_descriptions)
        assert "не более 30 символов" in failure_text.lower()


class TestLoginFormBasic:
    
    def test_form_init(self):
        form = LoginForm()
        assert form.username == ""
        assert form.password == ""
        assert form.username_valid is False
        assert form.password_valid is False
    
    def test_form_init_with_callbacks(self):
        login_cb = Mock()
        register_cb = Mock()
        form = LoginForm(on_login=login_cb, on_register=register_cb)
        assert form.on_login_callback is login_cb
        assert form.on_register_callback is register_cb


class TestLoginFormMethods:
    
    def test_update_button_styles(self):
        form = LoginForm()
        
        login_btn = Mock()
        register_btn = Mock()
        
        with patch.object(form, 'query_one') as mock_query:
            def query_side_effect(selector, widget_type):
                if selector == "#login-btn":
                    return login_btn
                elif selector == "#register-btn":
                    return register_btn
                return Mock()
            
            mock_query.side_effect = query_side_effect
            
            login_btn.disabled = None  # очищаем
            register_btn.disabled = None
            
            form.username_valid = False
            form.password_valid = False
            form.update_button_styles()
            
            assert login_btn.disabled is True
            assert register_btn.disabled is True
            
            login_btn.disabled = None
            register_btn.disabled = None
            
            form.username_valid = True
            form.password_valid = True
            form.update_button_styles()
            
            assert login_btn.disabled is False
            assert register_btn.disabled is False
    
    def test_login_empty_fields(self):
        form = LoginForm()
        form.username = ""
        form.password = ""
        
        with patch.object(form, 'query_one') as mock_query:
            message_widget = Mock()
            mock_query.return_value = message_widget
            
            form.login()
            
            message_widget.update.assert_called_once()
            call_arg = message_widget.update.call_args[0][0]
            assert "заполните все поля" in call_arg.lower()
    
    def test_login_with_callback_success(self):
        callback = Mock(return_value=True)
        form = LoginForm(on_login=callback)
        form.username = "user"
        form.password = "pass123"
        
        with patch.object(form, 'query_one') as mock_query:
            message_widget = Mock()
            mock_query.return_value = message_widget
            
            mock_app = Mock()
            mock_app.update_user_info_display = Mock()
            mock_app.save_config = Mock()
            mock_app.showMainContainer = Mock()
            
            with patch.object(LoginForm, 'app', new_callable=PropertyMock) as mock_app_prop:
                mock_app_prop.return_value = mock_app
                
                with patch.object(form, 'close_popup'):
                    form.login()
                    
                    callback.assert_called_once_with("user", "pass123")
                    
                    assert message_widget.update.called
                    call_arg = message_widget.update.call_args[0][0]
                    assert "успешный вход" in call_arg.lower()
                    
                    mock_app.update_user_info_display.assert_called_once()
                    mock_app.save_config.assert_called_once_with("user", "pass123")
                    mock_app.showMainContainer.assert_called_once()
    
    def test_login_with_callback_failure(self):
        callback = Mock(return_value=False)
        form = LoginForm(on_login=callback)
        form.username = "user"
        form.password = "wrong"
        
        with patch.object(form, 'query_one') as mock_query:
            message_widget = Mock()
            mock_query.return_value = message_widget
            
            mock_app = Mock()
            
            with patch.object(LoginForm, 'app', new_callable=PropertyMock) as mock_app_prop:
                mock_app_prop.return_value = mock_app
                
                form.login()
                
                callback.assert_called_once_with("user", "wrong")
                assert message_widget.update.called
                call_arg = message_widget.update.call_args[0][0]
                assert "неверное" in call_arg.lower() or "ошибка" in call_arg.lower()
    
    def test_register_success(self):
        callback = Mock(return_value=True)
        form = LoginForm(on_register=callback)
        form.username = "newuser"
        form.password = "newpass"
        form.username_valid = True
        form.password_valid = True
        
        with patch.object(form, 'query_one') as mock_query:
            message_widget = Mock()
            mock_query.return_value = message_widget
            
            mock_app = Mock()
            mock_app.update_user_info_display = Mock()
            mock_app.save_config = Mock()
            mock_app.showMainContainer = Mock()
            
            with patch.object(LoginForm, 'app', new_callable=PropertyMock) as mock_app_prop:
                mock_app_prop.return_value = mock_app
                
                with patch.object(form, 'close_popup'):
                    form.register()
                    
                    callback.assert_called_once_with("newuser", "newpass")
                    assert message_widget.update.called
                    call_arg = message_widget.update.call_args[0][0]
                    assert "аккаунт успешно создан" in call_arg.lower()
    
    def test_register_failed(self):
        callback = Mock(return_value=False)
        form = LoginForm(on_register=callback)
        form.username = "user"
        form.password = "pass"
        form.username_valid = True
        form.password_valid = True
        
        with patch.object(form, 'query_one') as mock_query:
            message_widget = Mock()
            mock_query.return_value = message_widget
            
            mock_app = Mock()
            
            with patch.object(LoginForm, 'app', new_callable=PropertyMock) as mock_app_prop:
                mock_app_prop.return_value = mock_app
                
                form.register()
                
                callback.assert_called_once_with("user", "pass")
                assert message_widget.update.called
                call_arg = message_widget.update.call_args[0][0]
                assert "ошибка при регистрации" in call_arg.lower()
    
    def test_register_invalid_data(self):
        form = LoginForm()
        form.username_valid = False
        form.password_valid = False
        
        with patch.object(form, 'query_one') as mock_query:
            message_widget = Mock()
            mock_query.return_value = message_widget
            
            form.register()
            
            assert message_widget.update.called
            call_arg = message_widget.update.call_args[0][0]
            assert "исправьте ошибки" in call_arg.lower()

class TestLoginFormEvents:
    "Тесты обработчиков событий"
    
    def test_on_input_changed_username(self):
        form = LoginForm()
        
        event = Mock()
        event.input = Mock()
        event.input.id = "username"
        event.value = "newuser"
        event.validation_result = Mock(is_valid=True)
        
        with patch.object(form, 'query_one') as mock_query:
            message_widget = Mock()
            mock_query.return_value = message_widget
            
            with patch.object(form, 'update_button_styles') as mock_update:
                form.on_input_changed(event)
                
                assert form.username == "newuser"
                assert form.username_valid is True
                
                message_widget.update.assert_called_once_with("")
                
                mock_update.assert_called_once()
    
    def test_on_button_pressed_login(self):
        form = LoginForm()
        
        event = Mock()
        event.button = Mock(id="login-btn")
        
        with patch.object(form, 'login') as mock_login:
            form.on_button_pressed(event)
            mock_login.assert_called_once()
    
    def test_on_button_pressed_register(self):
        form = LoginForm()
        
        event = Mock()
        event.button = Mock(id="register-btn")
        
        with patch.object(form, 'register') as mock_register:
            form.on_button_pressed(event)
            mock_register.assert_called_once()
    
    def test_on_key_enter_username_to_password(self):
        form = LoginForm()
        
        mock_app = Mock()
        mock_app.focused = Mock(id="username")
        
        with patch.object(LoginForm, 'app', new_callable=PropertyMock) as mock_app_prop:
            mock_app_prop.return_value = mock_app
            
            with patch.object(form, 'query_one') as mock_query:
                password_input = Mock()
                mock_query.return_value = password_input
                
                event = Mock(key="enter")
                form.on_key(event)
                
                password_input.focus.assert_called_once()
    
    def test_on_key_enter_password_login(self):
        form = LoginForm()
        
        mock_app = Mock()
        mock_app.focused = Mock(id="password")
        
        with patch.object(LoginForm, 'app', new_callable=PropertyMock) as mock_app_prop:
            mock_app_prop.return_value = mock_app
            
            with patch.object(form, 'login') as mock_login:
                event = Mock(key="enter")
                form.on_key(event)
                
                mock_login.assert_called_once()


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v"]))
