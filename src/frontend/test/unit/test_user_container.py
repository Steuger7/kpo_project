import pytest
from unittest.mock import Mock, patch
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try:
    from userContainer import UserInfoContainer
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    raise


class TestUserInfoContainerInitialization:
    
    def test_container_init_default(self):
        container = UserInfoContainer()
        
        assert container.username == ""
        assert container.books_count == 0
        assert container.on_logout is None
    
    def test_container_init_with_values(self):
        logout_callback = Mock()
        container = UserInfoContainer(
            username="testuser",
            books_count=5,
            on_logout=logout_callback
        )
        
        assert container.username == "testuser"
        assert container.books_count == 5
        assert container.on_logout is logout_callback
    
    def test_container_default_css(self):
        assert hasattr(UserInfoContainer, 'DEFAULT_CSS')
        assert isinstance(UserInfoContainer.DEFAULT_CSS, str)
        assert len(UserInfoContainer.DEFAULT_CSS) > 0
        
        assert 'UserInfoContainer' in UserInfoContainer.DEFAULT_CSS
        assert '.username' in UserInfoContainer.DEFAULT_CSS
        assert '.books-count' in UserInfoContainer.DEFAULT_CSS
        assert '.logout-button' in UserInfoContainer.DEFAULT_CSS


class TestUserInfoContainerComposition:
    
    def test_compose_creates_widgets(self):
        container = UserInfoContainer(
            username="testuser",
            books_count=3
        )
        
        compose_result = list(container.compose())
        
        assert len(compose_result) == 3
        
        assert all(widget is not None for widget in compose_result)
    
    def test_compose_with_correct_values(self):
        with patch('userContainer.Static') as MockStaticClass, \
             patch('userContainer.Button') as MockButtonClass:
            
            mock_static1 = Mock()
            mock_static2 = Mock()
            mock_button = Mock()
            
            MockStaticClass.side_effect = [mock_static1, mock_static2]
            MockButtonClass.return_value = mock_button
            
            container = UserInfoContainer(
                username="Иван",
                books_count=10
            )
            
            list(container.compose())
            
            MockStaticClass.assert_any_call("Иван", classes="username")
            
            MockStaticClass.assert_any_call("Книг: 10", classes="books-count")
            
            MockButtonClass.assert_called_once_with(
                "login",
                id="logout-button",
                classes="logout-button",
                variant="error"
            )


class TestUserInfoContainerEventHandling:
    
    def test_on_button_pressed_logout_button(self):
        logout_callback = Mock()
        container = UserInfoContainer(
            username="testuser",
            books_count=5,
            on_logout=logout_callback
        )
        
        mock_button = Mock()
        mock_button.id = "logout-button"
        
        mock_event = Mock()
        mock_event.button = mock_button
        
        with patch.object(container, '_handle_logout') as mock_handle:
            container.on_button_pressed(mock_event)
            
            mock_handle.assert_called_once()
    
    def test_on_button_pressed_wrong_button(self):
        logout_callback = Mock()
        container = UserInfoContainer(
            username="testuser",
            books_count=5,
            on_logout=logout_callback
        )
        
        mock_button = Mock()
        mock_button.id = "other-button"  # Не та кнопка
        
        mock_event = Mock()
        mock_event.button = mock_button
        
        with patch.object(container, '_handle_logout') as mock_handle:
            container.on_button_pressed(mock_event)
            
            mock_handle.assert_not_called()
    
    def test_on_button_pressed_without_callback(self):
        container = UserInfoContainer(
            username="testuser",
            books_count=5
        )
        
        mock_button = Mock()
        mock_button.id = "logout-button"
        
        mock_event = Mock()
        mock_event.button = mock_button
        
        with patch.object(container, '_handle_logout') as mock_handle:
            container.on_button_pressed(mock_event)
            
            mock_handle.assert_called_once()


class TestUserInfoContainerLogoutHandling:
    
    def test_handle_logout_with_callback(self):
        logout_callback = Mock()
        container = UserInfoContainer(
            username="testuser",
            books_count=5,
            on_logout=logout_callback
        )
        
        container._handle_logout()
        
        logout_callback.assert_called_once()
    
    def test_handle_logout_without_callback(self):
        container = UserInfoContainer(
            username="testuser",
            books_count=5
        )
        
        try:
            container._handle_logout()
            assert True
        except Exception as e:
            pytest.fail(f"Метод упал с исключением: {e}")
    
    def test_handle_logout_callback_exception(self):
        def failing_callback():
            raise ValueError("Ошибка в коллбеке выхода")
        
        container = UserInfoContainer(
            username="testuser",
            books_count=5,
            on_logout=failing_callback
        )
        
        try:
            container._handle_logout()
            assert True
        except ValueError:
            pytest.fail("Исключение из коллбека не должно проваливаться наружу")


class TestUserInfoContainerUpdateMethods:
    def test_update_books_count_zero(self):
        "Тест обновления количества книг на 0"
        container = UserInfoContainer(
            username="testuser",
            books_count=5
        )
        
        mock_count_widget = Mock()
        
        with patch.object(container, 'query_one') as mock_query:
            mock_query.return_value = mock_count_widget
            
            container.update_books_count(0)
            
            assert container.books_count == 0
            mock_count_widget.update.assert_called_once_with("Книг: 0")
    
    def test_update_books_count_negative(self):
        "Тест обновления количества книг на отрицательное число"
        container = UserInfoContainer(
            username="testuser",
            books_count=5
        )
        
        mock_count_widget = Mock()
        
        with patch.object(container, 'query_one') as mock_query:
            mock_query.return_value = mock_count_widget
            
            container.update_books_count(-3)
            
            assert container.books_count == -3
            mock_count_widget.update.assert_called_once_with("Книг: -3")
    
    def test_update_user_info(self):
        "Тест одновременного обновления имени и количества книг"
        container = UserInfoContainer(
            username="старое_имя",
            books_count=5
        )
        
        mock_username_widget = Mock()
        mock_count_widget = Mock()
        
        with patch.object(container, 'query_one') as mock_query:
            def query_side_effect(selector, widget_type):
                if selector == ".username":
                    return mock_username_widget
                elif selector == ".books-count":
                    return mock_count_widget
                return Mock()
            
            mock_query.side_effect = query_side_effect
            
            container.update_user_info("новое_имя", 15)
            
            assert container.username == "новое_имя"
            assert container.books_count == 15
            
            assert mock_query.call_count == 2
            mock_username_widget.update.assert_called_once_with("новое_имя")
            mock_count_widget.update.assert_called_once_with("Книг: 15")
    
    def test_update_user_info_same_values(self):
        "Тест обновления информации теми же значениями"
        container = UserInfoContainer(
            username="имя",
            books_count=5
        )
        
        mock_username_widget = Mock()
        mock_count_widget = Mock()
        
        with patch.object(container, 'query_one') as mock_query:
            def query_side_effect(selector, widget_type):
                if selector == ".username":
                    return mock_username_widget
                elif selector == ".books-count":
                    return mock_count_widget
                return Mock()
            
            mock_query.side_effect = query_side_effect
            
            container.update_user_info("имя", 5)
            
            assert container.username == "имя"
            assert container.books_count == 5
            
            mock_username_widget.update.assert_called_once_with("имя")
            mock_count_widget.update.assert_called_once_with("Книг: 5")


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v"]))
